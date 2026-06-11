"""
ZELZAL Reconnaissance Module v5.0
Real tools: nmap stealth, masscan, enum4linux, smbmap, dnsrecon, dnsenum,
fierce, sublist3r, amass, theharvester, recon-ng, sherlock, whatweb, wafw00f
"""
from datetime import datetime
from typing import Dict, Any

from core import run_command, save_report, check_dependencies

MODULE_NAME = "reconnaissance"


class Reconnaissance:
    def __init__(self):
        self.name = MODULE_NAME
        self.deps = ["nmap", "masscan", "enum4linux", "smbclient", "dnsrecon",
                      "theharvester", "whatweb", "sherlock", "amass"]

    def check_status(self) -> Dict[str, Any]:
        available = [d for d in self.deps if check_dependencies([d]).get(d, False)]
        return {
            "module": self.name,
            "status": "available" if len(available) > len(self.deps) // 2 else "limited",
            "tools_found": available,
            "tools_missing": [d for d in self.deps if d not in available],
            "timestamp": datetime.now().isoformat(),
        }

    def stealth_nmap_scan(self, target: str = "127.0.0.1", ports: str = "1-1024") -> Dict[str, Any]:
        result = {"module": "stealth_nmap", "target": target, "findings": []}
        code, out, err = run_command(
            ["nmap", "-sS", "-sV", "-T4", "--open", "-p", ports, target], timeout=120
        )
        if code == 0:
            for line in out.split("\n"):
                if "/tcp" in line and "open" in line:
                    parts = line.split()
                    result["findings"].append({
                        "port": parts[0], "state": parts[1], "service": " ".join(parts[2:])
                    })
        else:
            result["error"] = err or "nmap not available or scan failed"
        result["open_ports"] = len(result["findings"])
        return result

    def masscan_scan(self, target: str = "127.0.0.1", ports: str = "80,443,22,3389") -> Dict[str, Any]:
        result = {"module": "masscan", "target": target, "findings": []}
        code, out, err = run_command(
            ["masscan", target, "-p", ports, "--rate=1000", "-oL", "-"], timeout=60
        )
        if code == 0:
            for line in out.split("\n"):
                if line.startswith("open"):
                    parts = line.split()
                    if len(parts) >= 4:
                        result["findings"].append({"port": parts[2], "protocol": parts[3]})
        else:
            result["error"] = err or "masscan not available"
        return result

    def enum4linux_scan(self, target: str = "127.0.0.1") -> Dict[str, Any]:
        result = {"module": "enum4linux", "target": target, "findings": []}
        code, out, err = run_command(["enum4linux", "-a", target], timeout=60)
        if code == 0:
            sections = {"users": [], "shares": [], "os_info": ""}
            for line in out.split("\n"):
                if "local users" in line.lower() or "\\user" in line.lower():
                    sections["users"].append(line.strip())
                if "disk" in line.lower() or "share" in line.lower():
                    sections["shares"].append(line.strip())
                if "os " in line.lower() or "workgroup" in line.lower():
                    sections["os_info"] += line.strip() + " "
            result["findings"] = sections
        else:
            result["error"] = err or "enum4linux not available"
        return result

    def smbmap_scan(self, target: str = "127.0.0.1") -> Dict[str, Any]:
        result = {"module": "smbmap", "target": target, "findings": []}
        code, out, err = run_command(["smbmap", "-H", target, "-u", "guest"], timeout=30)
        if code == 0:
            for line in out.split("\n"):
                if "READ" in line or "WRITE" in line or "disk" in line.lower():
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "smbmap not available"
        return result

    def dns_recon(self, domain: str = "example.com") -> Dict[str, Any]:
        result = {"module": "dns_recon", "domain": domain, "records": []}
        code, out, err = run_command(
            ["dnsrecon", "-d", domain, "-t", "std"], timeout=30
        )
        if code == 0:
            for line in out.split("\n"):
                if line.strip() and not line.startswith("#"):
                    result["records"].append(line.strip())
        else:
            result["records"].append("dnsrecon not available")
        # fallback: dig
        code2, out2, _ = run_command(["dig", domain, "ANY", "+short"], timeout=10)
        if code2 == 0 and out2.strip():
            result["records"].append("--- dig ANY ---")
            result["records"].extend([l.strip() for l in out2.split("\n") if l.strip()])
        return result

    def dns_enum(self, domain: str = "example.com") -> Dict[str, Any]:
        result = {"module": "dnsenum", "domain": domain, "findings": []}
        code, out, err = run_command(["dnsenum", "--enum", domain], timeout=60)
        if code == 0:
            for line in out.split("\n"):
                if "host" in line.lower() or "ip" in line.lower() or "subdomain" in line.lower():
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "dnsenum not available"
        return result

    def fierce_scan(self, domain: str = "example.com") -> Dict[str, Any]:
        result = {"module": "fierce", "domain": domain, "findings": []}
        code, out, err = run_command(["fierce", "--domain", domain], timeout=60)
        if code == 0:
            for line in out.split("\n"):
                if "found" in line.lower() or "host" in line.lower():
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "fierce not available"
        return result

    def sublist3r_scan(self, domain: str = "example.com") -> Dict[str, Any]:
        result = {"module": "sublist3r", "domain": domain, "subdomains": []}
        code, out, err = run_command(["sublist3r", "-d", domain], timeout=60)
        if code == 0:
            for line in out.split("\n"):
                if domain in line and not line.startswith("-"):
                    result["subdomains"].append(line.strip())
        else:
            result["error"] = err or "sublist3r not available"
        return result

    def amass_scan(self, domain: str = "example.com") -> Dict[str, Any]:
        result = {"module": "amass", "domain": domain, "subdomains": []}
        code, out, err = run_command(
            ["amass", "enum", "-passive", "-d", domain], timeout=120
        )
        if code == 0:
            for line in out.split("\n"):
                if domain in line:
                    result["subdomains"].append(line.strip())
        else:
            result["error"] = err or "amass not available"
        return result

    def theharvester_scan(self, domain: str = "example.com") -> Dict[str, Any]:
        result = {"module": "theharvester", "domain": domain, "emails": [], "hosts": []}
        code, out, err = run_command(
            ["theharvester", "-d", domain, "-b", "google", "-l", "50"], timeout=60
        )
        if code == 0:
            for line in out.split("\n"):
                if "@" in line and domain in line:
                    result["emails"].append(line.strip())
                if "host" in line.lower() and domain in line.lower():
                    result["hosts"].append(line.strip())
        else:
            result["error"] = err or "theharvester not available"
        return result

    def recon_ng_scan(self, domain: str = "example.com") -> Dict[str, Any]:
        result = {"module": "recon-ng", "domain": domain, "findings": []}
        script = (
            f"workspaces create zelzal_scan\n"
            f"db insert domain {domain}\n"
            f"use recon/domains-hosts/hackertarget\n"
            f"run\n"
            f"exit\n"
        )
        with open("/tmp/reconng_script.txt", "w") as f:
            f.write(script)
        code, out, err = run_command(
            ["recon-ng", "-r", "/tmp/reconng_script.txt"], timeout=90
        )
        if code == 0:
            for line in out.split("\n"):
                if domain in line or "host" in line.lower():
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "recon-ng not available"
        return result

    def sherlock_scan(self, username: str = "john") -> Dict[str, Any]:
        result = {"module": "sherlock", "username": username, "sites_found": []}
        code, out, err = run_command(
            ["sherlock", username, "--output", "/dev/null"], timeout=120
        )
        if code == 0:
            for line in out.split("\n"):
                if "[+]" in line:
                    result["sites_found"].append(line.replace("[+]", "").strip())
        else:
            result["error"] = err or "sherlock not available"
        return result

    def whatweb_scan(self, target: str = "example.com") -> Dict[str, Any]:
        result = {"module": "whatweb", "target": target, "technologies": []}
        code, out, err = run_command(["whatweb", target, "--aggression", "1"], timeout=30)
        if code == 0:
            for line in out.split("\n"):
                if "[" in line or "CMS" in line or "framework" in line.lower():
                    result["technologies"].append(line.strip())
        else:
            result["error"] = err or "whatweb not available"
        return result

    def wafw00f_scan(self, target: str = "example.com") -> Dict[str, Any]:
        result = {"module": "wafw00f", "target": target, "waf_detected": None}
        code, out, err = run_command(["wafw00f", target], timeout=30)
        if code == 0:
            for line in out.split("\n"):
                if "WAF" in line or "firewall" in line.lower():
                    result["waf_detected"] = line.strip()
        else:
            result["error"] = err or "wafw00f not available"
        if not result["waf_detected"]:
            result["waf_detected"] = "No WAF detected or tool unavailable"
        return result

    def full_assessment(self, target: str = "example.com") -> Dict[str, Any]:
        timestamp = datetime.now().isoformat()
        report = {
            "module": self.name,
            "timestamp": timestamp,
            "stealth_nmap": self.stealth_nmap_scan(target),
            "masscan": self.masscan_scan(target),
            "enum4linux": self.enum4linux_scan(target),
            "smbmap": self.smbmap_scan(target),
            "dns_recon": self.dns_recon(target),
            "dns_enum": self.dns_enum(target),
            "fierce": self.fierce_scan(target),
            "sublist3r": self.sublist3r_scan(target),
            "amass": self.amass_scan(target),
            "theharvester": self.theharvester_scan(target),
            "whatweb": self.whatweb_scan(target),
            "wafw00f": self.wafw00f_scan(target),
        }
        save_report(report, self.name)
        return report
