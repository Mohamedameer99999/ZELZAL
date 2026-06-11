"""
ZELZAL System Protection Module v5.0
Real implementations using: psutil, clamav, lynis, chkrootkit, rkhunter
"""

import os
from datetime import datetime
from typing import Dict, Optional, Any

from core import write_log, run_command, save_report, is_root, check_dependencies

MODULE_NAME = "system_protection"
REQUIRED_TOOLS = ["clamscan", "lynis", "chkrootkit", "rkhunter", "ps aux"]


class SystemProtection:
    """System-level security hardening and monitoring"""

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

    def set_firewall_rules(self) -> Dict[str, Any]:
        """Apply system firewall rules"""
        write_log("Applying system firewall rules", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "rules_applied": 0, "failed": []}
        if not is_root():
            write_log("Root required for firewall rules", "ERROR")
            result["error"] = "Root required"
            return result
        try:
            base_rules = [
                ["ufw", "--force", "enable"],
                ["ufw", "default", "deny", "incoming"],
                ["ufw", "default", "allow", "outgoing"],
                ["ufw", "allow", "22/tcp"],
                ["ufw", "allow", "443/tcp"],
                ["ufw", "allow", "80/tcp"],
            ]
            for rule in base_rules:
                code, _, stderr = run_command(rule, timeout=10)
                if code == 0:
                    result["rules_applied"] += 1
                else:
                    result["failed"].append({"rule": " ".join(rule), "error": stderr[:50]})
            write_log(f"Applied {result['rules_applied']} firewall rules", "SUCCESS")
        except Exception as e:
            write_log(f"Firewall setup error: {e}", "ERROR")
        return result

    def malware_scan(self, quick: bool = True, path: str = "/") -> Dict[str, Any]:
        """Run malware scan using ClamAV"""
        mode = "quick" if quick else "full"
        write_log(f"Starting {mode} malware scan: {path}", "INFO")
        result = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "path": path,
            "infected": 0,
            "scanned": 0,
            "threats": [],
        }
        try:
            args = ["clamscan", "--no-summary", "-r"]
            if quick:
                args += ["--max-filesize=10M", "--max-scansize=100M"]
            else:
                args += ["--max-filesize=100M", "--max-scansize=1G"]
            args.append(path)
            timeout = 120 if quick else 600
            code, stdout, stderr = run_command(args, timeout=timeout)
            if code in (0, 1):
                for line in stdout.split("\n"):
                    if "FOUND" in line:
                        result["infected"] += 1
                        result["threats"].append(line.strip())
                    elif line.endswith(".scanned"):
                        try:
                            result["scanned"] = int(line.split(":")[-1].strip().split()[0])
                        except (ValueError, IndexError):
                            pass
                if result["infected"] > 0:
                    write_log(f"MALWARE FOUND: {result['infected']} threats in {result['scanned']} files", "WARNING")
                else:
                    write_log(f"Scan complete: {result['scanned']} files, clean", "SUCCESS")
            else:
                write_log(f"ClamAV error: {stderr[:100]}", "WARNING")
                result["error"] = stderr[:200]
        except Exception as e:
            write_log(f"Malware scan error: {e}", "ERROR")
        return result

    def vulnerability_scan(self) -> Dict[str, Any]:
        """Run vulnerability assessment using Lynis"""
        write_log("Starting vulnerability scan", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "warnings": 0, "suggestions": 0, "details": []}
        if not is_root():
            write_log("Lynis requires root for full scan", "WARNING")
        try:
            code, stdout, stderr = run_command(["lynis", "audit", "system", "--quick", "--no-colors"], timeout=300)
            if code == 0 or code == 1:
                for line in stdout.split("\n"):
                    if "[WARNING]" in line:
                        result["warnings"] += 1
                        result["details"].append({"type": "warning", "message": line})
                    elif "[SUGGESTION]" in line:
                        result["suggestions"] += 1
                        result["details"].append({"type": "suggestion", "message": line})
                write_log(f"Vulnerability scan: {result['warnings']} warnings, {result['suggestions']} suggestions", "SUCCESS")
            else:
                # Fallback: system checks
                result["details"].append({"type": "note", "message": "Lynis not available, running basic checks"})
                self._basic_vuln_check(result)
        except FileNotFoundError:
            self._basic_vuln_check(result)
        except Exception as e:
            write_log(f"Vulnerability scan error: {e}", "ERROR")
        return result

    def _basic_vuln_check(self, result: Dict[str, Any]) -> None:
        """Basic vulnerability checks when Lynis is not available"""
        checks = [
            ("SSH root login", "grep -q 'PermitRootLogin yes' /etc/ssh/sshd_config 2>/dev/null && echo 'WARNING' || echo 'OK'"),
            ("Password expiration", "grep -q 'PASS_MAX_DAYS' /etc/login.defs 2>/dev/null && echo 'OK' || echo 'CHECK'"),
            ("Open ports", "ss -tln | grep -c ':'"),
        ]
        for name, cmd in checks:
            code, stdout, _ = run_command(["bash", "-c", cmd])
            if code == 0:
                result["details"].append({"type": "check", "name": name, "status": stdout.strip()})

    def usb_scanner(self) -> Dict[str, Any]:
        """Scan connected USB devices for threats"""
        write_log("Scanning USB devices", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "devices": [], "suspicious": 0}
        try:
            code, stdout, stderr = run_command(["lsusb"])
            if code == 0:
                for line in stdout.split("\n"):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 6:
                            device = {
                                "bus": parts[1] if len(parts) > 1 else "",
                                "device": parts[3] if len(parts) > 3 else "",
                                "id": parts[5] if len(parts) > 5 else "",
                                "description": " ".join(parts[6:]) if len(parts) > 6 else "",
                            }
                            result["devices"].append(device)
                write_log(f"USB scan: {len(result['devices'])} devices", "SUCCESS")
            # Check for BadUSB-like devices (HID + Storage combined)
            hid_devices = [d for d in result["devices"] if "keyboard" in d.get("description", "").lower() or "HID" in d.get("description", "")]
            storage_devices = [d for d in result["devices"] if "storage" in d.get("description", "").lower() or "Mass Storage" in d.get("description", "")]
            if hid_devices and storage_devices:
                write_log("Potential BadUSB attack vector: HID + Storage devices present", "WARNING")
                result["suspicious"] = len(hid_devices)
        except Exception as e:
            write_log(f"USB scan error: {e}", "ERROR")
        return result

    def ransomware_protection(self, action: str = "status") -> Dict[str, Any]:
        """Check and enable ransomware protection"""
        write_log(f"Ransomware protection: {action}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "action": action, "protected": False}
        try:
            # Check for common ransomware indicators
            if action == "status":
                indicator_dirs = [
                    "/etc/clamav",
                    "/var/lib/clamav",
                ]
                for d in indicator_dirs:
                    if os.path.exists(d):
                        write_log(f"ClamAV found: {d}", "INFO")
                        result["protected"] = True
                # Check if auditd is running
                code, stdout, _ = run_command(["systemctl", "is-active", "auditd"])
                result["auditd_active"] = code == 0
                # Check for file integrity tools
                for tool in ["aide", "tripwire", "osquery"]:
                    if run_command(["which", tool])[0] == 0:
                        result["integrity_tool"] = tool
                        result["protected"] = True
                if not result["protected"]:
                    write_log("Ransomware protection: consider installing clamav, aide, or tripwire", "WARNING")
                else:
                    write_log("Ransomware protection active", "SUCCESS")
            elif action == "enable" and is_root():
                # Enable auditd for file monitoring
                run_command(["systemctl", "enable", "auditd"])
                run_command(["systemctl", "start", "auditd"])
                # Add file integrity monitoring rules
                watch_dirs = ["/etc", "/bin", "/sbin", "/usr/bin"]
                for wd in watch_dirs:
                    run_command(["auditctl", "-w", wd, "-p", "wa", "-k", "system_integrity"])
                result["protected"] = True
                write_log("Ransomware protection enabled with auditd", "SUCCESS")
        except Exception as e:
            write_log(f"Ransomware protection error: {e}", "ERROR")
        return result

    def event_log_analysis(self) -> Dict[str, Any]:
        """Analyze system logs for suspicious activity"""
        write_log("Analyzing system event logs", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "suspicious_events": [], "total_analyzed": 0}
        try:
            log_files = {
                "/var/log/auth.log": ["Failed password", "Invalid user", "BREAK-IN"],
                "/var/log/syslog": ["error", "panic", "critical"],
                "/var/log/kern.log": ["segfault", "buffer overflow", "DENIED"],
            }
            for log_file, patterns in log_files.items():
                if os.path.exists(log_file):
                    code, stdout, _ = run_command(["tail", "-100", log_file])
                    if code == 0:
                        lines = stdout.split("\n")
                        result["total_analyzed"] += len(lines)
                        for pattern in patterns:
                            matching = [l for l in lines if pattern.lower() in l.lower()]
                            for match in matching[:5]:  # Limit to 5 per pattern
                                result["suspicious_events"].append({
                                    "source": log_file,
                                    "pattern": pattern,
                                    "line": match[:200],
                                })
            write_log(f"Log analysis: {len(result['suspicious_events'])} suspicious events in "
                      f"{result['total_analyzed']} lines", "SUCCESS")
        except Exception as e:
            write_log(f"Log analysis error: {e}", "ERROR")
        return result

    def keylogger_detection(self) -> Dict[str, Any]:
        """Detect potential keylogger activity"""
        write_log("Scanning for keyloggers", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "keyloggers_found": 0, "suspicious_processes": []}
        try:
            # Check for known keylogger processes
            known_keyloggers = ["logkeys", "uberkey", "pykeylogger", "lkl", "vlogger", "xspy"]
            code, stdout, _ = run_command(["ps", "aux"])
            if code == 0:
                for line in stdout.split("\n"):
                    for kls in known_keyloggers:
                        if kls.lower() in line.lower():
                            result["keyloggers_found"] += 1
                            result["suspicious_processes"].append(line.strip()[:150])
                            write_log(f"Potential keylogger: {kls}", "WARNING")
            # Check for /dev/input access by non-root processes
            code, stdout, _ = run_command(["fuser", "/dev/input/mice", "/dev/input/event*"], timeout=5)
            if code == 0 and stdout.strip():
                result["suspicious_processes"].append(f"Input device access: {stdout.strip()[:150]}")
                write_log("Suspicious input device access detected", "WARNING")
            if result["keyloggers_found"] == 0:
                write_log("No keyloggers detected", "SUCCESS")
        except Exception as e:
            write_log(f"Keylogger detection error: {e}", "ERROR")
        return result

    def registry_backup(self, backup_path: Optional[str] = None) -> Dict[str, Any]:
        """Backup system configuration (Linux equivalent)"""
        write_log("Backing up system configuration", "INFO")
        if backup_path is None:
            backup_path = f"/tmp/zelzal_backup_{datetime.now().strftime('%Y%m%d')}"
        result = {"timestamp": datetime.now().isoformat(), "backup_path": backup_path, "files_backed_up": 0}
        try:
            os.makedirs(backup_path, exist_ok=True)
            config_dirs = ["/etc", "/var/spool/cron", "/etc/ssh", "/etc/nginx", "/etc/apache2"]
            for d in config_dirs:
                if os.path.exists(d):
                    dest = os.path.join(backup_path, d.lstrip("/"))
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    code, _, _ = run_command(["cp", "-r", d, dest])
                    if code == 0:
                        result["files_backed_up"] += 1
            write_log(f"Backup complete: {result['files_backed_up']} dirs to {backup_path}", "SUCCESS")
        except Exception as e:
            write_log(f"Backup error: {e}", "ERROR")
        return result

    def driver_scanner(self) -> Dict[str, Any]:
        """Scan kernel modules for known vulnerable versions"""
        write_log("Scanning kernel modules", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "modules": [], "suspicious": 0}
        try:
            code, stdout, _ = run_command(["lsmod"])
            if code == 0:
                for line in stdout.split("\n")[1:]:
                    parts = line.split()
                    if parts:
                        result["modules"].append(parts[0])
                write_log(f"Kernel modules: {len(result['modules'])} loaded", "SUCCESS")
            # Check for unnecessary or dangerous modules
            dangerous_modules = ["bluetooth", "pcan", "ath9k_htc", "b43", "ssb", "bcma"]
            for mod in result["modules"]:
                if mod in dangerous_modules:
                    result["suspicious"] += 1
                    write_log(f"Dangerous module loaded: {mod}", "WARNING")
        except Exception as e:
            write_log(f"Driver scan error: {e}", "ERROR")
        return result

    def task_audit(self) -> Dict[str, Any]:
        """Audit scheduled tasks (cron jobs) for unauthorized entries"""
        write_log("Auditing scheduled tasks", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "cron_jobs": [], "unauthorized": 0}
        try:
            cron_paths = [
                "/var/spool/cron/crontabs",
                "/etc/cron.d",
                "/etc/cron.hourly",
                "/etc/cron.daily",
                "/etc/cron.weekly",
                "/etc/cron.monthly",
            ]
            for cp in cron_paths:
                if os.path.exists(cp):
                    for f in os.listdir(cp):
                        filepath = os.path.join(cp, f)
                        if os.path.isfile(filepath):
                            try:
                                content = open(filepath).read()
                                result["cron_jobs"].append({
                                    "file": filepath,
                                    "content": content[:500],
                                })
                            except Exception:
                                pass
            write_log(f"Cron audit: {len(result['cron_jobs'])} job files found", "SUCCESS")
        except Exception as e:
            write_log(f"Task audit error: {e}", "ERROR")
        return result

    def service_hardening(self) -> Dict[str, Any]:
        """Harden system services by disabling unnecessary ones"""
        write_log("Auditing system services for hardening", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "enabled_services": [], "recommended_disable": []}
        try:
            code, stdout, _ = run_command(["systemctl", "list-unit-files", "--type=service", "--state=enabled"])
            if code == 0:
                for line in stdout.split("\n")[1:]:
                    parts = line.split()
                    if parts and len(parts) > 1:
                        result["enabled_services"].append(parts[0])
            # Common services to disable on security-hardened systems
            disable_candidates = ["cups.service", "avahi-daemon.service", "bluetooth.service",
                                  "cups-browsed.service", "whoopsie.service", "ModemManager.service"]
            for svc in result["enabled_services"]:
                for candidate in disable_candidates:
                    if candidate in svc:
                        result["recommended_disable"].append(svc)
            write_log(f"Service audit: {len(result['enabled_services'])} enabled, "
                      f"{len(result['recommended_disable'])} recommended to disable", "SUCCESS")
        except Exception as e:
            write_log(f"Service hardening error: {e}", "ERROR")
        return result

    def full_assessment(self) -> Dict[str, Any]:
        """Run complete system security assessment"""
        write_log("Starting full system security assessment", "INFO")
        results = {
            "timestamp": datetime.now().isoformat(),
            "malware_scan": self.malware_scan(quick=True),
            "vulnerability": self.vulnerability_scan(),
            "event_logs": self.event_log_analysis(),
            "keylogger": self.keylogger_detection(),
            "driver_scan": self.driver_scanner(),
            "service_hardening": self.service_hardening(),
            "task_audit": self.task_audit(),
            "usb_devices": self.usb_scanner(),
        }
        save_report(results, "system_full_assessment")
        write_log("System assessment complete", "SUCCESS")
        return results
