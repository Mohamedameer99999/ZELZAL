"""
ZELZAL Web Application Scanning Module v5.0
Real tools: nikto, wpscan, gobuster, sqlmap, dirb, joomscan, droopescan, whatweb
"""
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

from core import write_log, run_command, save_report, check_dependencies, is_root

MODULE_NAME = "web_app_scanning"

class WebAppScanning:
    def __init__(self):
        self.name = MODULE_NAME
        self.deps = ["nikto", "wpscan", "gobuster", "sqlmap", "dirb",
                      "joomscan", "droopescan"]

    def check_status(self) -> Dict[str, Any]:
        available = [d for d in self.deps if check_dependencies([d]).get(d, False)]
        return {
            "module": self.name,
            "status": "available" if len(available) > len(self.deps) // 2 else "limited",
            "tools_found": available,
            "tools_missing": [d for d in self.deps if d not in available],
            "timestamp": datetime.now().isoformat(),
        }

    def nikto_scan(self, target: str = "http://localhost:80") -> Dict[str, Any]:
        result = {"module": "nikto", "target": target, "vulnerabilities": []}
        code, out, err = run_command(
            ["nikto", "-h", target, "-Tuning", "123456789", "-nointeractive"],
            timeout=120
        )
        if code == 0 or code is None:
            for line in out.split("\n"):
                if "+" in line and ("/" in line or ":" in line):
                    vuln = line.strip().lstrip("+ ")
                    if vuln:
                        result["vulnerabilities"].append(vuln)
        else:
            result["error"] = err or "nikto not available"
        return result

    def wpscan_scan(self, target: str = "http://localhost") -> Dict[str, Any]:
        result = {"module": "wpscan", "target": target, "findings": []}
        code, out, err = run_command(
            ["wpscan", "--url", target, "--no-update", "--format", "cli"],
            timeout=120
        )
        if code == 0:
            for line in out.split("\n"):
                if "[!]" in line or "[i]" in line:
                    result["findings"].append(line.strip())
                if "vulnerability" in line.lower() or "theme" in line.lower():
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "wpscan not available"
        return result

    def gobuster_scan(self, target: str = "http://localhost", wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> Dict[str, Any]:
        result = {"module": "gobuster", "target": target, "directories": []}
        if not os.path.exists(wordlist):
            wordlist = "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"
        code, out, err = run_command(
            ["gobuster", "dir", "-u", target, "-w", wordlist,
             "-t", "20", "-q", "--no-color", "-k"], timeout=120
        )
        if code == 0:
            for line in out.split("\n"):
                if "/" in line and ("Status:" in line or "200" in line or "301" in line or "403" in line):
                    result["directories"].append(line.strip())
        else:
            result["error"] = err or "gobuster not available"
        return result

    def sqlmap_scan(self, target: str = "http://localhost/page?id=1") -> Dict[str, Any]:
        result = {"module": "sqlmap", "target": target, "vulnerabilities": []}
        code, out, err = run_command(
            ["sqlmap", "-u", target, "--batch", "--random-agent",
             "--level", "1", "--risk", "1", "--output-dir=/tmp/sqlmap_zelzal"],
            timeout=180
        )
        if code == 0:
            for line in out.split("\n"):
                if "[INFO]" in line and "injectable" in line.lower():
                    result["vulnerabilities"].append(line.strip())
                if "parameter" in line.lower() and "vulnerable" in line.lower():
                    result["vulnerabilities"].append(line.strip())
        else:
            result["error"] = err or "sqlmap not available"
        return result

    def dirb_scan(self, target: str = "http://localhost", wordlist: str = "/usr/share/wordlists/dirb/common.txt") -> Dict[str, Any]:
        result = {"module": "dirb", "target": target, "directories": []}
        code, out, err = run_command(
            ["dirb", target, wordlist, "-S", "-N", "404", "-w"], timeout=120
        )
        if code == 0 or code is None:
            for line in out.split("\n"):
                if "==> " in line or "CODE:200" in line or "CODE:301" in line or "CODE:403" in line:
                    result["directories"].append(line.strip())
        else:
            result["error"] = err or "dirb not available"
        return result

    def joomscan_scan(self, target: str = "http://localhost") -> Dict[str, Any]:
        result = {"module": "joomscan", "target": target, "findings": []}
        code, out, err = run_command(
            ["joomscan", "-u", target, "--no-check-certificate"], timeout=90
        )
        if code == 0 or code is None:
            for line in out.split("\n"):
                if "[+]" in line:
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "joomscan not available"
        return result

    def droopescan_scan(self, target: str = "http://localhost") -> Dict[str, Any]:
        result = {"module": "droopescan", "target": target, "findings": []}
        code, out, err = run_command(
            ["droopescan", "scan", "drupal", "-u", target], timeout=90
        )
        if code == 0:
            for line in out.split("\n"):
                if "[+]" in line or "[!]" in line:
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "droopescan not available"
        return result

    def full_assessment(self, target: str = "http://localhost") -> Dict[str, Any]:
        timestamp = datetime.now().isoformat()
        report = {
            "module": self.name,
            "timestamp": timestamp,
            "nikto": self.nikto_scan(target),
            "wpscan": self.wpscan_scan(target),
            "gobuster": self.gobuster_scan(target),
            "sqlmap": self.sqlmap_scan(target),
            "dirb": self.dirb_scan(target),
            "joomscan": self.joomscan_scan(target),
            "droopescan": self.droopescan_scan(target),
        }
        save_report(report, self.name)
        return report
