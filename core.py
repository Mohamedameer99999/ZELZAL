# ZELZAL v4.5 - Anonymous Security Framework (Python Port)
# Core Engine - mirrors Core.ps1
import os, json, base64, hashlib, secrets, string, ctypes, subprocess
from pathlib import Path
from datetime import datetime
from cryptography.fernet import Fernet

VERSION = "4.5.0"
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "Logs"
CONFIG_DIR = BASE_DIR / "Config"
QUARANTINE_DIR = BASE_DIR / "Quarantine"
REPORTS_DIR = BASE_DIR / "Reports"

for d in [LOG_DIR, CONFIG_DIR, QUARANTINE_DIR, REPORTS_DIR]:
    d.mkdir(exist_ok=True)

def write_log(message, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{ts}] [{level}] {message}"
    log_file = LOG_DIR / f"security_{datetime.now().strftime('%Y-%m-%d')}.log"
    with open(log_file, "a") as f:
        f.write(entry + "\n")
    print(entry)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_config(key, default=None):
    cfg_file = CONFIG_DIR / "settings.json"
    if cfg_file.exists():
        try:
            return json.loads(cfg_file.read_text()).get(key, default)
        except:
            pass
    return default

def set_config(key, value):
    cfg_file = CONFIG_DIR / "settings.json"
    cfg = {}
    if cfg_file.exists():
        try:
            cfg = json.loads(cfg_file.read_text())
        except:
            cfg = {}
    cfg[key] = value
    cfg_file.write_text(json.dumps(cfg, indent=2))

def generate_password(length=16, no_symbols=False):
    chars = string.ascii_letters + string.digits
    if not no_symbols:
        chars += "!@#%^&*()_+-=[]{}|;:,.<>?"
    return "".join(secrets.choice(chars) for _ in range(length))

def _fernet_key(password):
    return base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())

def encrypt_file(path, password):
    f = Fernet(_fernet_key(password))
    with open(path, "rb") as fh:
        data = fh.read()
    out_path = path + ".encrypted"
    with open(out_path, "wb") as fh:
        fh.write(f.encrypt(data))
    write_log(f"Encrypted: {out_path}", "SUCCESS")
    return out_path

def decrypt_file(path, password):
    f = Fernet(_fernet_key(password))
    with open(path, "rb") as fh:
        data = fh.read()
    out_path = path.replace(".encrypted", ".decrypted")
    with open(out_path, "wb") as fh:
        fh.write(f.decrypt(data))
    write_log(f"Decrypted: {out_path}", "SUCCESS")
    return out_path

def clear_old_logs(days=30):
    cutoff = datetime.now().timestamp() - days * 86400
    for f in LOG_DIR.glob("*.log"):
        if f.stat().st_mtime < cutoff:
            f.unlink()
    write_log(f"Removed logs older than {days} days", "INFO")
