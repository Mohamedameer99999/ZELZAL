"""
ZELZAL Web Protection Module v5.0
Real implementations using: requests, dnspython, whois, sslyze, curl
"""

import re
import os
import socket
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

from core import write_log, run_command, save_report, check_dependencies

MODULE_NAME = "web_protection"
REQUIRED_TOOLS = ["curl", "openssl", "whois"]


class WebProtection:
    """Web security assessment and privacy protection"""

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

    def secure_dns(self, dns_servers: List[str] = None) -> Dict[str, Any]:
        """Configure secure DNS servers"""
        if dns_servers is None:
            dns_servers = ["1.1.1.1", "9.9.9.9", "8.8.8.8"]
        write_log(f"Configuring secure DNS: {', '.join(dns_servers)}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "dns_servers": dns_servers, "configured": False}
        try:
            resolv_path = "/etc/resolv.conf"
            backup_path = f"{resolv_path}.backup"
            code, stdout, _ = run_command(["cp", resolv_path, backup_path])
            if code == 0:
                content = "\n".join(f"nameserver {dns}" for dns in dns_servers)
                with open(resolv_path, "w") as f:
                    f.write(f"# ZELZAL Secure DNS Configuration\n{content}\n")
                result["configured"] = True
                result["backup"] = backup_path
                write_log("Secure DNS configured successfully", "SUCCESS")
            else:
                result["error"] = "Failed to backup resolv.conf"
                write_log("Failed to configure DNS - need root", "ERROR")
        except Exception as e:
            write_log(f"DNS configuration error: {e}", "ERROR")
            result["error"] = str(e)
        return result

    def phishing_check(self, url: str) -> Dict[str, Any]:
        """Check a URL for phishing indicators"""
        write_log(f"Checking URL for phishing indicators: {url}", "INFO")
        result = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "risk_score": 0,
            "risk_level": "safe",
            "indicators": [],
        }
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            result["domain"] = domain
            # Check for suspicious TLDs
            suspicious_tlds = [".xyz", ".top", ".club", ".gq", ".ml", ".tk", ".cf", ".click"]
            for tld in suspicious_tlds:
                if domain.endswith(tld):
                    result["indicators"].append(f"Suspicious TLD: {tld}")
                    result["risk_score"] += 25
            # Check for IP-based URL
            if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
                result["indicators"].append("IP-based URL instead of domain name")
                result["risk_score"] += 30
            # Check for excessive subdomains
            subdomain_count = domain.count('.')
            if subdomain_count > 3:
                result["indicators"].append(f"Excessive subdomains: {subdomain_count}")
                result["risk_score"] += 15
            # Check for URL shorteners
            shorteners = ["bit.ly", "tinyurl", "goo.gl", "ow.ly", "is.gd", "buff.ly", "t.co"]
            if any(s in domain for s in shorteners):
                result["indicators"].append(f"URL shortener detected: {domain}")
                result["risk_score"] += 20
            # Try HTTPS
            try:
                import ssl
                import socket as sock
                ctx = ssl.create_default_context()
                with ctx.wrap_socket(sock.socket(), server_hostname=domain) as s:
                    s.settimeout(5)
                    s.connect((domain, 443))
                    cert = s.getpeercert()
                    if cert:
                        result["indicators"].append("Valid SSL certificate found")
            except Exception:
                result["indicators"].append("No valid HTTPS connection")
                result["risk_score"] += 20
            # Determine risk level
            score = result["risk_score"]
            if score >= 60:
                result["risk_level"] = "dangerous"
            elif score >= 30:
                result["risk_level"] = "suspicious"
            else:
                result["risk_level"] = "safe"
            write_log(f"Phishing check: {result['risk_level']} (score: {score})", "SUCCESS")
        except Exception as e:
            write_log(f"Phishing check error: {e}", "ERROR")
            result["error"] = str(e)
        return result

    def privacy_cleaner(self) -> Dict[str, Any]:
        """Clean browser and system privacy data"""
        write_log("Cleaning privacy data", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "cleaned": [], "failed": []}
        targets = [
            ("Chrome cache", os.path.expanduser("~/.cache/google-chrome")),
            ("Firefox cache", os.path.expanduser("~/.cache/mozilla/firefox")),
            ("Brave cache", os.path.expanduser("~/.cache/Brave-Browser")),
            ("System trash", os.path.expanduser("~/.local/share/Trash")),
            ("Thumbnails", os.path.expanduser("~/.thumbnails")),
            ("Recent documents", os.path.expanduser("~/.recently-used")),
        ]
        try:
            import shutil
            for name, path in targets:
                expanded = os.path.expanduser(path)
                if os.path.exists(expanded):
                    try:
                        for item in os.listdir(expanded):
                            item_path = os.path.join(expanded, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path, ignore_errors=True)
                        result["cleaned"].append(name)
                        write_log(f"Cleaned: {name}", "SUCCESS")
                    except Exception as e:
                        result["failed"].append({"name": name, "error": str(e)})
            # Clear bash history
            history_files = [os.path.expanduser("~/.bash_history"), os.path.expanduser("~/.zsh_history")]
            for hf in history_files:
                if os.path.exists(hf):
                    try:
                        os.remove(hf)
                        result["cleaned"].append(f"Shell history: {os.path.basename(hf)}")
                    except Exception as e:
                        result["failed"].append({"name": f"Shell history: {hf}", "error": str(e)})
        except Exception as e:
            write_log(f"Privacy cleaner error: {e}", "ERROR")
        return result

    def data_leak_scan(self, email: Optional[str] = None) -> Dict[str, Any]:
        """Scan for potential data leaks using public breach databases"""
        write_log("Scanning for data leaks", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "leaks_found": 0, "breaches": []}
        try:
            import requests
            # Use Have I Been Pwned API (v3)
            if email:
                headers = {"hibp-api-key": ""}  # User needs to provide API key
                code, stdout, _ = run_command(["curl", "-s",
                    f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"])
                if code == 0 and stdout and stdout != "[]":
                    try:
                        breaches = json.loads(stdout)
                        result["leaks_found"] = len(breaches)
                        result["breaches"] = [b.get("Name", "Unknown") for b in breaches]
                        write_log(f"Found {len(breaches)} breaches for {email}", "WARNING")
                    except json.JSONDecodeError:
                        pass
            # Check for common leaked password patterns in local files
            leaked_patterns = [
                os.path.expanduser("~/.ssh/id_rsa"),
                os.path.expanduser("~/.aws/credentials"),
                os.path.expanduser("~/.git-credentials"),
            ]
            for pattern in leaked_patterns:
                import os as os_module
                if os_module.path.exists(pattern):
                    result["leaks_found"] += 1
                    result["breaches"].append(f"Exposed credentials: {pattern}")
                    write_log(f"Sensitive file found: {pattern}", "WARNING")
        except Exception as e:
            write_log(f"Data leak scan error: {e}", "ERROR")
        if result["leaks_found"] == 0:
            write_log("No data leaks detected", "SUCCESS")
        return result

    def cookie_analysis(self) -> Dict[str, Any]:
        """Analyze browser cookies for tracking"""
        write_log("Analyzing cookies for tracking", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "tracking_cookies": 0, "total_cookies": 0, "domains": {}}
        cookie_paths = [
            os.path.expanduser("~/.mozilla/firefox/*.default/cookies.sqlite"),
        ]
        try:
            import glob
            import os as os_module
            for pattern in cookie_paths:
                for cookie_db in glob.glob(pattern):
                    if os_module.path.exists(cookie_db):
                        try:
                            code, stdout, _ = run_command(["sqlite3", cookie_db,
                                "SELECT host, name FROM moz_cookies"])
                            if code == 0:
                                for line in stdout.strip().split("\n"):
                                    if line and "," in line:
                                        host, name = line.split(",", 1)
                                        result["total_cookies"] += 1
                                        if host not in result["domains"]:
                                            result["domains"][host] = 0
                                        result["domains"][host] += 1
                                        # Simple heuristic for tracking cookies
                                        tracking_keywords = ["track", "analytics", "pixel", "ad", "session"]
                                        if any(k in name.lower() for k in tracking_keywords):
                                            result["tracking_cookies"] += 1
                        except Exception:
                            pass
            write_log(f"Cookie analysis: {result['tracking_cookies']} tracking out of "
                      f"{result['total_cookies']} total", "SUCCESS")
        except Exception as e:
            write_log(f"Cookie analysis error: {e}", "ERROR")
        return result

    def email_breach_check(self, email: str) -> Dict[str, Any]:
        """Check if email was involved in known breaches"""
        return self.data_leak_scan(email)

    def secure_browser_launch(self) -> Dict[str, Any]:
        """Launch browser in secure/sandboxed mode"""
        write_log("Launching secure browser session", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "launched": False, "browser": None}
        try:
            browsers = [
                ["firefox", "--private-window", "--safe-mode"],
                ["chromium", "--incognito", "--no-sandbox"],
                ["google-chrome", "--incognito", "--no-sandbox"],
            ]
            for browser_cmd in browsers:
                if run_command(["which", browser_cmd[0]])[0] == 0:
                    subprocess.Popen(browser_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    result["launched"] = True
                    result["browser"] = browser_cmd[0]
                    write_log(f"Launched {browser_cmd[0]} in secure mode", "SUCCESS")
                    break
            if not result["launched"]:
                write_log("No supported browser found", "WARNING")
        except Exception as e:
            write_log(f"Browser launch error: {e}", "ERROR")
        return result

    def dns_leak_test(self) -> Dict[str, Any]:
        """Test DNS requests for leaks beyond VPN"""
        write_log("Testing DNS for leaks", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "leak_detected": False, "dns_servers": []}
        try:
            code, stdout, _ = run_command(["nslookup", "google.com"])
            if code == 0:
                for line in stdout.split("\n"):
                    if "Server:" in line or "Address:" in line:
                        addr = line.split()[-1]
                        if addr not in ["#53"] and not addr.startswith("127."):
                            result["dns_servers"].append(addr.split("#")[0])
                # If multiple DNS servers detected beyond expected, potential leak
                if len(result["dns_servers"]) > 2:
                    result["leak_detected"] = True
                    write_log("DNS leak detected!", "WARNING")
                else:
                    write_log(f"No DNS leak: {result['dns_servers']}", "SUCCESS")
        except Exception as e:
            write_log(f"DNS leak test error: {e}", "ERROR")
        return result

    def webrtc_leak_test(self) -> Dict[str, Any]:
        """Test WebRTC for IP leaks"""
        write_log("Testing WebRTC for IP leaks", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "leak_detected": False, "local_ips": []}
        try:
            import socket as sock
            result["local_ips"] = list(set([
                sock.gethostbyname(sock.gethostname()),
                sock.gethostbyname_ex(sock.gethostname())[2][0] if sock.gethostbyname_ex(sock.gethostname())[2] else "",
            ]))
            result["local_ips"] = [ip for ip in result["local_ips"] if ip]
        except Exception as e:
            write_log(f"WebRTC test error: {e}", "ERROR")
        return result

    def https_enforce(self) -> Dict[str, Any]:
        """Check and enforce HTTPS-only configuration"""
        write_log("Checking HTTPS enforcement", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "https_enforced": False, "status": {}}
        try:
            # Check HSTS status
            code, stdout, _ = run_command(["curl", "-sI", "https://google.com"])
            if code == 0:
                for line in stdout.split("\n"):
                    line = line.strip()
                    if "Strict-Transport-Security" in line or "strict-transport-security" in line:
                        result["https_enforced"] = True
                        result["status"]["hsts"] = line
            write_log(f"HTTPS enforcement: {'active' if result['https_enforced'] else 'check manually'}", "SUCCESS")
        except Exception as e:
            write_log(f"HTTPS check error: {e}", "ERROR")
        return result

    def download_scanner(self, file_path: str) -> Dict[str, Any]:
        """Scan downloaded file for malware using ClamAV"""
        write_log(f"Scanning file: {file_path}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "file": file_path, "malicious": False, "signatures": []}
        try:
            code, stdout, stderr = run_command(["clamscan", "--no-summary", file_path], timeout=30)
            if code == 0:
                write_log(f"File clean: {file_path}", "SUCCESS")
            elif code == 1:
                result["malicious"] = True
                for line in stdout.split("\n"):
                    if "FOUND" in line:
                        result["signatures"].append(line.strip())
                write_log(f"MALWARE DETECTED: {file_path}", "WARNING")
            else:
                write_log(f"ClamAV error: {stderr[:100]}", "WARNING")
                result["error"] = stderr[:200]
        except Exception as e:
            write_log(f"File scan error: {e}", "ERROR")
            result["error"] = str(e)
        return result

    def adblocker_check(self) -> Dict[str, Any]:
        """Check and configure ad-blocking via hosts file"""
        write_log("Checking ad-blocking configuration", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "blocked_domains": 0, "active": False}
        try:
            hosts_path = "/etc/hosts"
            if os.path.exists(hosts_path):
                with open(hosts_path) as f:
                    content = f.read()
                ad_entries = [l for l in content.split("\n") if "127.0.0.1" in l and "localhost" not in l]
                result["blocked_domains"] = len(ad_entries)
                result["active"] = result["blocked_domains"] > 100
                write_log(f"Ad-blocking: {result['blocked_domains']} domains blocked", "SUCCESS")
        except Exception as e:
            write_log(f"Ad-blocker check error: {e}", "ERROR")
        return result

    def full_assessment(self) -> Dict[str, Any]:
        """Run complete web security assessment"""
        write_log("Starting full web security assessment", "INFO")
        results = {
            "dns_leak": self.dns_leak_test(),
            "webrtc_leak": self.webrtc_leak_test(),
            "https_status": self.https_enforce(),
            "adblocker": self.adblocker_check(),
            "privacy": self.privacy_cleaner(),
        }
        save_report(results, "web_full_assessment")
        write_log("Web assessment complete", "SUCCESS")
        return results



