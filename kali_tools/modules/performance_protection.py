"""
ZELZAL Performance Protection Module v5.0
Real implementations using: psutil, systemd tools, disk utilities
"""

import os
import shutil
from datetime import datetime
from typing import Dict, Any

from core import write_log, run_command, save_report, check_dependencies

MODULE_NAME = "performance_protection"
REQUIRED_TOOLS = ["iotop", "htop", "du", "df"]


class PerformanceProtection:
    """System performance optimization and monitoring"""

    def __init__(self):
        self.name = MODULE_NAME
        self.tools = check_dependencies(REQUIRED_TOOLS)

    def check_status(self) -> Dict[str, Any]:
        found = [t for t, v in self.tools.items() if v]
        return {
            "module": self.name,
            "status": "available" if len(found) > len(self.tools) // 2 else "limited",
            "tools_found": found,
            "tools_missing": [t for t in self.tools if not self.tools[t]],
            "timestamp": datetime.now().isoformat(),
        }

    def disk_cleanup(self) -> Dict[str, Any]:
        """Clean temporary files and free disk space"""
        write_log("Starting disk cleanup", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "freed_bytes": 0, "cleaned": [], "failed": []}
        try:
            # Get initial free space
            code, stdout, _ = run_command(["df", "-B1", "/"])
            initial_free = 0
            if code == 0:
                parts = stdout.split("\n")[1].split()
                initial_free = int(parts[3]) if len(parts) > 3 else 0

            # Clean targets
            targets = [
                ("APT cache", "/var/cache/apt/archives", ["*.deb"]),
                ("Thumbnails", os.path.expanduser("~/.cache/thumbnails"), []),
                ("Browser cache", os.path.expanduser("~/.cache"), []),
                ("System logs", "/var/log", ["*.log.*", "*.gz"]),
                ("Temporary files", "/tmp", []),
                ("Journal logs", "/var/log/journal", []),
            ]
            for name, path, patterns in targets:
                if os.path.exists(path):
                    try:
                        if name == "APT cache":
                            run_command(["apt-get", "clean"], timeout=30)
                        elif name == "Journal logs":
                            run_command(["journalctl", "--vacuum-time=3d"], timeout=30)
                        elif name == "System logs":
                            run_command(["find", path, "-name", "*.log.*", "-mtime", "+7", "-delete"])
                        else:
                            for item in os.listdir(path):
                                item_path = os.path.join(path, item)
                                try:
                                    if os.path.isfile(item_path):
                                        os.remove(item_path)
                                    elif os.path.isdir(item_path):
                                        shutil.rmtree(item_path, ignore_errors=True)
                                except Exception:
                                    pass
                        result["cleaned"].append(name)
                    except Exception as e:
                        result["failed"].append({"name": name, "error": str(e)})

            # Get final free space
            code, stdout, _ = run_command(["df", "-B1", "/"])
            if code == 0:
                parts = stdout.split("\n")[1].split()
                final_free = int(parts[3]) if len(parts) > 3 else 0
                result["freed_bytes"] = final_free - initial_free
                result["freed_mb"] = round(result["freed_bytes"] / 1024 / 1024, 2)

            write_log(f"Disk cleanup: freed {result.get('freed_mb', 0)} MB", "SUCCESS")
        except Exception as e:
            write_log(f"Disk cleanup error: {e}", "ERROR")
        return result

    def registry_analyzer(self) -> Dict[str, Any]:
        """Analyze system configuration health (Linux equivalent)"""
        write_log("Analyzing system configuration", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "issues": [], "config_files_checked": 0}
        try:
            configs = {
                "/etc/sysctl.conf": "kernel parameters",
                "/etc/security/limits.conf": "system limits",
                "/etc/fstab": "filesystem table",
                "/etc/default/grub": "bootloader config",
            }
            for path, desc in configs.items():
                if os.path.exists(path):
                    result["config_files_checked"] += 1
                    try:
                        content = open(path).read()
                        # Check for syntax issues (basic)
                        for i, line in enumerate(content.split("\n"), 1):
                            if line.strip() and not line.strip().startswith("#"):
                                if "=" in line and line.count("=") > 2:
                                    result["issues"].append(f"Possible syntax issue in {path}:{i}")
                    except Exception as e:
                        result["issues"].append(f"Cannot read {path}: {e}")
            write_log(f"Config analysis: {result['config_files_checked']} files, "
                      f"{len(result['issues'])} issues", "SUCCESS")
        except Exception as e:
            write_log(f"Config analyzer error: {e}", "ERROR")
        return result

    def memory_optimizer(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        write_log("Optimizing memory usage", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "memory_freed_mb": 0, "status": {}}
        try:
            # Get initial memory
            code, stdout, _ = run_command(["free", "-m"])
            if code == 0:
                lines = stdout.split("\n")
                if len(lines) > 1:
                    parts = lines[1].split()
                    result["status"]["total_mb"] = int(parts[1]) if len(parts) > 1 else 0
                    result["status"]["used_mb"] = int(parts[2]) if len(parts) > 2 else 0
                    result["status"]["free_mb"] = int(parts[3]) if len(parts) > 3 else 0
                    result["status"]["available_mb"] = int(parts[6]) if len(parts) > 6 else 0

            # Clear page cache, dentries, inodes
            if hasattr(os, 'geteuid') and os.geteuid() == 0:
                run_command(["sync"])
                with open("/proc/sys/vm/drop_caches", "w") as f:
                    f.write("3")
                write_log("Memory caches cleared", "SUCCESS")

            # Check for memory-heavy processes
            code, stdout, _ = run_command(["ps", "aux", "--sort=-%mem"])
            if code == 0:
                top_processes = []
                for line in stdout.split("\n")[1:11]:
                    parts = line.split()
                    if len(parts) >= 11:
                        top_processes.append({
                            "user": parts[0],
                            "pid": parts[1],
                            "cpu": parts[2],
                            "mem": parts[3],
                            "command": " ".join(parts[10:])[:50],
                        })
                result["top_processes"] = top_processes

            # Get final memory
            code, stdout, _ = run_command(["free", "-m"])
            if code == 0:
                lines = stdout.split("\n")
                if len(lines) > 1:
                    parts = lines[1].split()
                    result["memory_freed_mb"] = result["status"]["free_mb"]
            write_log(f"Memory optimizer: {result.get('status', {}).get('available_mb', '?')} MB available", "SUCCESS")
        except Exception as e:
            write_log(f"Memory optimizer error: {e}", "ERROR")
        return result

    def startup_optimizer(self) -> Dict[str, Any]:
        """Analyze and optimize startup programs and services"""
        write_log("Analyzing startup configuration", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "startup_services": [], "recommended_disable": []}
        try:
            # Check enabled systemd services
            code, stdout, _ = run_command(["systemctl", "list-unit-files", "--type=service", "--state=enabled"])
            if code == 0:
                for line in stdout.split("\n")[1:]:
                    parts = line.split()
                    if parts:
                        svc = parts[0]
                        result["startup_services"].append(svc)
                        # Flag non-essential services
                        non_essential = ["cups", "bluetooth", "avahi", "whoopsie", "ModemManager"]
                        for ne in non_essential:
                            if ne in svc.lower():
                                result["recommended_disable"].append(svc)

            # Check startup time
            code, stdout, _ = run_command(["systemd-analyze"])
            if code == 0:
                result["boot_time"] = stdout.strip()

            code, stdout, _ = run_command(["systemd-analyze", "blame"])
            if code == 0:
                slow_services = []
                for line in stdout.split("\n")[:5]:
                    if line.strip():
                        slow_services.append(line.strip()[:100])
                result["slowest_services"] = slow_services

            write_log(f"Startup analysis: {len(result['startup_services'])} services, "
                      f"{len(result['recommended_disable'])} recommended to disable", "SUCCESS")
        except Exception as e:
            write_log(f"Startup optimizer error: {e}", "ERROR")
        return result

    def temp_manager(self) -> Dict[str, Any]:
        """Manage temporary file cleanup"""
        write_log("Managing temporary files", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "temp_files_removed": 0, "space_freed_mb": 0}
        try:
            temp_dirs = ["/tmp", "/var/tmp", os.path.expanduser("~/.cache")]
            for td in temp_dirs:
                if os.path.exists(td):
                    code, stdout, _ = run_command(["du", "-sb", td])
                    if code == 0:
                        try:
                            int(stdout.split()[0])
                        except (ValueError, IndexError):
                            pass
                    # Remove files older than 7 days
                    run_command(["find", td, "-type", "f", "-atime", "+7", "-delete"], timeout=30)
                    run_command(["find", td, "-type", "d", "-empty", "-delete"], timeout=30)
                    result["temp_files_removed"] += 1
            write_log(f"Temp manager: cleaned {result['temp_files_removed']} directories", "SUCCESS")
        except Exception as e:
            write_log(f"Temp manager error: {e}", "ERROR")
        return result

    def system_health(self) -> Dict[str, Any]:
        """Comprehensive system health check"""
        write_log("Running system health check", "INFO")
        result = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "good",
            "checks": {},
            "issues": [],
        }
        try:
            # CPU load
            code, stdout, _ = run_command(["uptime"])
            if code == 0:
                load_part = stdout.split("load average:")[-1].strip()
                result["checks"]["cpu_load"] = load_part

            # Memory
            code, stdout, _ = run_command(["free", "-h"])
            if code == 0:
                result["checks"]["memory"] = stdout.split("\n")[1] if len(stdout.split("\n")) > 1 else ""

            # Disk usage
            code, stdout, _ = run_command(["df", "-h", "/"])
            if code == 0:
                result["checks"]["disk"] = stdout.split("\n")[1] if len(stdout.split("\n")) > 1 else ""

            # System temperature
            code, stdout, _ = run_command(["sensors"])
            if code == 0:
                temp_lines = [l for l in stdout.split("\n") if "°C" in l or "°F" in l]
                result["checks"]["temperature"] = temp_lines[:3] if temp_lines else "No sensors"

            # Running processes
            code, stdout, _ = run_command(["ps", "--no-headers", "-eo", "pid,comm", "--sort=-%mem"])
            if code == 0:
                total = len([l for l in stdout.split("\n") if l.strip()])
                result["checks"]["processes"] = total

            # Uptime
            code, stdout, _ = run_command(["uptime", "-p"])
            if code == 0:
                result["checks"]["uptime"] = stdout.strip()

            # Determine health
            issues = []
            try:
                load_values = [float(x) for x in load_part.replace(",", ".").split()]
                if any(l > 4.0 for l in load_values):
                    issues.append("High CPU load")
            except (ValueError, NameError):
                pass

            result["issues"] = issues
            result["overall_health"] = "warning" if issues else "good"

            write_log(f"System health: {result['overall_health']}", "SUCCESS")
        except Exception as e:
            write_log(f"Health check error: {e}", "ERROR")
            result["overall_health"] = "error"
        return result

    def full_assessment(self) -> Dict[str, Any]:
        """Run complete performance assessment"""
        write_log("Starting full performance assessment", "INFO")
        results = {
            "timestamp": datetime.now().isoformat(),
            "disk_cleanup": self.disk_cleanup(),
            "memory_status": self.memory_optimizer(),
            "startup_analysis": self.startup_optimizer(),
            "system_health": self.system_health(),
        }
        save_report(results, "performance_full_assessment")
        write_log("Performance assessment complete", "SUCCESS")
        return results
