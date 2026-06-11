"""
ZELZAL Core Engine v5.0 - Kali Linux Cybersecurity Framework
Enhanced core with logging, encryption, configuration, and utility functions
"""

import os
import json
import base64
import hashlib
import secrets
import string
import platform
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

try:
    from cryptography.fernet import Fernet
    HAS_FERNET = True
except ImportError:
    HAS_FERNET = False

VERSION = "5.0.0"
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"
REPORTS_DIR = BASE_DIR / "reports"
QUARANTINE_DIR = BASE_DIR / "quarantine"

for d in [LOG_DIR, CONFIG_DIR, REPORTS_DIR, QUARANTINE_DIR]:
    d.mkdir(exist_ok=True)


def is_kali() -> bool:
    """Check if running on Kali Linux"""
    try:
        with open("/etc/os-release") as f:
            content = f.read().lower()
            return "kali" in content
    except FileNotFoundError:
        return False


def is_root() -> bool:
    """Check if running as root"""
    if platform.system() == "Linux":
        return os.geteuid() == 0
    return False


def check_dependencies(tools: List[str]) -> Dict[str, bool]:
    """Check which required tools are installed on the system"""
    results = {}
    for tool in tools:
        results[tool] = shutil.which(tool) is not None
    return results


def write_log(message: str, level: str = "INFO") -> None:
    """Write timestamped log entry"""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {message}"
    log_file = LOG_DIR / f"zelzal_{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(entry + "\n")
    print(entry)


def get_config(key: str, default: Any = None) -> Any:
    """Read a configuration value"""
    cfg_file = CONFIG_DIR / "settings.json"
    if cfg_file.exists():
        try:
            return json.loads(cfg_file.read_text()).get(key, default)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def set_config(key: str, value: Any) -> None:
    """Write a configuration value"""
    cfg_file = CONFIG_DIR / "settings.json"
    cfg = {}
    if cfg_file.exists():
        try:
            cfg = json.loads(cfg_file.read_text())
        except (json.JSONDecodeError, OSError):
            cfg = {}
    cfg[key] = value
    cfg_file.write_text(json.dumps(cfg, indent=2))


def generate_password(length: int = 16, no_symbols: bool = False) -> str:
    """Generate cryptographically secure password"""
    chars = string.ascii_letters + string.digits
    if not no_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return "".join(secrets.choice(chars) for _ in range(length))


def _fernet_key(password: str) -> bytes:
    """Derive Fernet key from password"""
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())


def encrypt_file(path: str, password: str) -> Optional[str]:
    """Encrypt a file using Fernet AES encryption"""
    if not HAS_FERNET:
        write_log("cryptography library required for encryption", "ERROR")
        return None
    try:
        f = Fernet(_fernet_key(password))
        with open(path, "rb") as fh:
            data = fh.read()
        out_path = path + ".encrypted"
        with open(out_path, "wb") as fh:
            fh.write(f.encrypt(data))
        write_log(f"File encrypted: {out_path}", "SUCCESS")
        return out_path
    except Exception as e:
        write_log(f"Encryption failed: {e}", "ERROR")
        return None


def decrypt_file(path: str, password: str) -> Optional[str]:
    """Decrypt a Fernet-encrypted file"""
    if not HAS_FERNET:
        write_log("cryptography library required for decryption", "ERROR")
        return None
    try:
        f = Fernet(_fernet_key(password))
        with open(path, "rb") as fh:
            data = fh.read()
        out_path = path.replace(".encrypted", ".decrypted")
        with open(out_path, "wb") as fh:
            fh.write(f.decrypt(data))
        write_log(f"File decrypted: {out_path}", "SUCCESS")
        return out_path
    except Exception as e:
        write_log(f"Decryption failed: {e}", "ERROR")
        return None


def clear_old_logs(days: int = 30) -> int:
    """Remove log files older than specified days"""
    cutoff = datetime.now().timestamp() - days * 86400
    removed = 0
    for f in LOG_DIR.glob("*.log"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
            removed += 1
    write_log(f"Removed {removed} log files older than {days} days", "INFO")
    return removed


def run_command(cmd: List[str], timeout: int = 60) -> Tuple[int, str, str]:
    """Run a system command and return exit code, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -2, "", f"Command not found: {cmd[0]}"
    except Exception as e:
        return -3, "", str(e)


def save_report(data: Dict[str, Any], report_name: str) -> str:
    """Save a JSON report to the reports directory"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{report_name}_{ts}.json"
    path = REPORTS_DIR / filename
    path.write_text(json.dumps(data, indent=2, default=str))
    write_log(f"Report saved: {path}", "INFO")
    return str(path)


def get_system_info() -> Dict[str, Any]:
    """Gather basic system information"""
    info = {
        "platform": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
        "python_version": platform.python_version(),
        "timestamp": datetime.now().isoformat(),
        "is_kali": is_kali(),
        "is_root": is_root(),
    }
    if platform.system() == "Linux":
        try:
            with open("/proc/cpuinfo") as f:
                for line in f:
                    if line.startswith("model name"):
                        info["cpu"] = line.split(":")[1].strip()
                        break
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal"):
                        kb = int(line.split()[1])
                        info["memory_mb"] = kb // 1024
                        break
        except FileNotFoundError:
            pass
    return info
