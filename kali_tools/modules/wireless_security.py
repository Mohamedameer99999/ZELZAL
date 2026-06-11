"""
ZELZAL Wireless Security Module v5.0
Real implementations using: aircrack-ng, iw, iwconfig, macchanger, wash, reaver
"""

import re
from datetime import datetime
from typing import Dict, List, Any

from core import write_log, run_command, save_report, check_dependencies, is_root


class WirelessSecurity:
    """Wireless network security auditing"""

    def __init__(self):
        self.name = "wireless_security"
        self.dependencies = {
            "aircrack-ng": "aircrack-ng",
            "iwconfig": "iwconfig",
            "iw": "iw",
            "macchanger": "macchanger",
            "wash": "wash",
        }

    def check_status(self) -> Dict[str, Any]:
        results = check_dependencies(list(self.dependencies.values()))
        found = [dep for dep, binary in self.dependencies.items() if results.get(binary, False)]
        return {
            "module": self.name,
            "status": "available" if len(found) > len(self.dependencies) // 2 else "limited",
            "tools_found": found,
            "tools_missing": [dep for dep in self.dependencies if dep not in found],
            "timestamp": datetime.now().isoformat(),
        }

    def _get_interfaces(self) -> List[str]:
        code, out, _ = run_command("iwconfig 2>/dev/null | grep -o '^[^ ]\\+'")
        if code == 0 and out.strip():
            return out.strip().split('\n')
        code2, out2, _ = run_command("iw dev 2>/dev/null | grep Interface | awk '{print $2}'")
        if code2 == 0 and out2.strip():
            return out2.strip().split('\n')
        return []

    def interface_audit(self) -> Dict[str, Any]:
        """Audit wireless interfaces for security issues"""
        write_log("Running wireless interface audit", "info")
        result = {"status": "ok", "interfaces": []}

        interfaces = self._get_interfaces()
        if not interfaces:
            result["status"] = "error"
            result["error"] = "No wireless interfaces found"
            return result

        for iface in interfaces[:5]:
            info = {"interface": iface, "checks": []}

            code, out, _ = run_command(f"iwconfig {iface} 2>/dev/null")
            mode_match = re.search(r'Mode[:]?(\S+)', out or '')
            mode = mode_match.group(1) if mode_match else 'unknown'
            info["mode"] = mode

            if mode.lower() == 'monitor':
                info["checks"].append({"check": "Monitor Mode", "secure": False, "detail": "Interface in monitor mode - potential sniffing"})
            else:
                info["checks"].append({"check": "Monitor Mode", "secure": True})

            code2, out2, _ = run_command(f"macchanger -s {iface} 2>/dev/null")
            if code2 == 0:
                is_spoofed = 'Permanent' not in (out2 or '') and 'Current' in (out2 or '')
                if is_spoofed:
                    curr = re.search(r'Current MAC:\s+(\S+)', out2)
                    info["checks"].append({"check": "MAC Spoofing", "secure": True, "detail": f"Spoofed: {curr.group(1) if curr else ''}"})
                else:
                    info["checks"].append({"check": "MAC Spoofing", "secure": False, "detail": "Using permanent MAC address"})
            else:
                info["checks"].append({"check": "MAC Spoofing", "secure": None, "detail": "Cannot check"})

            code3, out3, _ = run_command(f"iw dev {iface} link 2>/dev/null")
            info["connected"] = code3 == 0 and bool(out3.strip())

            code4, out4, _ = run_command(f"iw {iface} scan 2>/dev/null | grep -c SSID")
            info["networks_visible"] = int(out4.strip()) if code4 == 0 and out4.strip() else 0

            result["interfaces"].append(info)

        return result

    def deauth_detection(self, interface: str = "wlan0", duration: int = 10) -> Dict[str, Any]:
        """Detect deauthentication attacks on a wireless interface"""
        write_log(f"Running deauth detection on {interface} for {duration}s", "info")
        result = {"status": "ok", "interface": interface, "duration": duration}

        if not is_root():
            result["status"] = "error"
            result["error"] = "Root privileges required"
            return result

        code, out, _ = run_command(f"iwconfig {interface} 2>/dev/null")
        if code != 0:
            result["status"] = "error"
            result["error"] = f"Interface {interface} not found"
            return result

        code2, out2, _ = run_command(f"timeout {duration} tcpdump -i {interface} -c 50 type mgt subtype deauth -e 2>/dev/null || true")
        if code2 == 0 and out2.strip():
            lines = out2.strip().split('\n')
            deauth_count = len(lines)
            result["deauth_packets"] = deauth_count
            result["attack_detected"] = deauth_count > 5
            bssids = set()
            for line in lines:
                m = re.search(r'BSSID[:]?(\S+)', line) or re.search(r'SA[:]?(\S+)', line)
                if m:
                    bssids.add(m.group(1))
            result["unique_bssids"] = list(bssids)[:10]
            result["threat_level"] = "critical" if deauth_count > 50 else "high" if deauth_count > 20 else "medium" if deauth_count > 5 else "low"
        else:
            result["deauth_packets"] = 0
            result["attack_detected"] = False
            result["threat_level"] = "safe"

        return result

    def wps_audit(self, interface: str = "wlan0") -> Dict[str, Any]:
        """Scan for WPS-enabled networks and check security"""
        write_log("Running WPS audit", "info")
        result = {"status": "ok", "networks": []}

        code, out, _ = run_command(f"wash -i {interface} -o /dev/stdout 2>/dev/null | head -30 || iw dev {interface} scan 2>/dev/null | grep -A 20 'WPS' || true")
        if code == 0 and out.strip():
            lines = out.strip().split('\n')
            for line in lines:
                m = re.search(r'(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
                if m:
                    result["networks"].append({
                        "bssid": m.group(1),
                        "channel": m.group(2),
                        "signal": m.group(3),
                        "wps_version": m.group(4),
                        "locked": 'No' in line or 'Yes' in line,
                    })
        else:
            code2, out2, _ = run_command("iw dev wlan0 scan 2>/dev/null | grep -E 'SSID|WPS|Authentication' | head -20 || true")
            if code2 == 0 and out2.strip():
                result["raw_scan"] = out2.strip()[:500]

        result["wps_networks"] = len(result["networks"])
        result["secure"] = result["wps_networks"] == 0

        return result

    def evil_twin_check(self, interface: str = "wlan0") -> Dict[str, Any]:
        """Check for evil twin / rogue AP attacks"""
        write_log("Checking for evil twin attacks", "info")
        result = {"status": "ok"}

        code, out, _ = run_command(f"iw dev {interface} scan 2>/dev/null")
        if code != 0 or not out:
            result["status"] = "error"
            result["error"] = "Cannot scan networks"
            return result

        ssids = re.findall(r'SSID:\s*(.+)', out)

        ssid_counts = {}
        for ssid in ssids:
            ssid = ssid.strip()
            if ssid and ssid != '':
                ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1

        duplicates = {k: v for k, v in ssid_counts.items() if v > 1}
        result["duplicate_ssids"] = duplicates
        result["evil_twin_detected"] = len(duplicates) > 0
        result["total_networks"] = len(ssids)
        result["unique_networks"] = len(ssid_counts)

        if result["evil_twin_detected"]:
            result["threat_level"] = "critical"
            result["warning"] = f"Found {len(duplicates)} SSID(s) with multiple BSSIDs - possible evil twin attack"

        return result

    def packet_capture_check(self, interface: str = "wlan0") -> Dict[str, Any]:
        """Check if interface can capture packets (promiscuous mode check)"""
        write_log("Checking packet capture capability", "info")
        result = {"status": "ok", "interface": interface}

        code, out, _ = run_command(f"iw dev {interface} set monitor none 2>&1 || true")
        if code == 0:
            result["monitor_mode"] = True
            result["capture_possible"] = True
            run_command(f"iw dev {interface} set type managed 2>/dev/null || true")
        else:
            result["monitor_mode"] = False
            result["capture_possible"] = False
            result["detail"] = "Cannot enable monitor mode -可能需要 additional drivers"

        return result

    def full_assessment(self) -> Dict[str, Any]:
        write_log("Starting full wireless security assessment", "info")
        result = {
            "timestamp": datetime.now().isoformat(),
            "module": self.name,
            "interface_audit": self.interface_audit(),
            "evil_twin_check": self.evil_twin_check(),
            "packet_capture": self.packet_capture_check(),
        }
        save_path = save_report(result, "wireless_security_report")
        result["report_path"] = save_path
        write_log(f"Wireless security report saved: {save_path}", "info")
        return result
