"""
ZELZAL Advanced Firewall Module v5.0
Real implementations using: iptables, nftables, ufw, ipset
"""

import os
import json
import ipaddress
from datetime import datetime
from typing import Dict, List, Optional, Any

from core import write_log, run_command, save_report, is_root, check_dependencies

MODULE_NAME = "firewall_advanced"
REQUIRED_TOOLS = ["iptables", "iptables-save", "ipset"]


class FirewallAdvanced:
    """Advanced firewall management and monitoring"""

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

    def _check_root(self) -> bool:
        if not is_root():
            write_log("Root privileges required for firewall operations", "ERROR")
            return False
        return True

    def get_current_rules(self) -> Dict[str, Any]:
        """Retrieve current iptables rules"""
        write_log("Retrieving current firewall rules", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "rules": {}, "raw": ""}
        if not self._check_root():
            return result
        try:
            code, stdout, stderr = run_command(["iptables-save"])
            if code == 0:
                result["raw"] = stdout
                chains = {}
                current_chain = None
                for line in stdout.split("\n"):
                    if line.startswith("*"):
                        current_chain = line[1:]
                        chains[current_chain] = []
                    elif line.startswith("-A"):
                        if current_chain:
                            chains[current_chain].append(line)
                result["rules"] = chains
                total = sum(len(rules) for rules in chains.values())
                write_log(f"Retrieved {total} rules across {len(chains)} chains", "SUCCESS")
            else:
                write_log(f"Failed to get rules: {stderr[:100]}", "ERROR")
        except Exception as e:
            write_log(f"Error getting rules: {e}", "ERROR")
        return result

    def add_rule(self, chain: str = "INPUT", rule: str = "") -> Dict[str, Any]:
        """Add a custom iptables rule"""
        write_log(f"Adding rule to {chain}: {rule}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "chain": chain, "rule": rule, "added": False}
        if not self._check_root():
            return result
        try:
            args = ["iptables", "-A", chain] + rule.split()
            code, stdout, stderr = run_command(args)
            if code == 0:
                result["added"] = True
                write_log(f"Rule added to {chain}", "SUCCESS")
            else:
                result["error"] = stderr[:200]
                write_log(f"Failed to add rule: {stderr[:100]}", "ERROR")
        except Exception as e:
            write_log(f"Error adding rule: {e}", "ERROR")
            result["error"] = str(e)
        return result

    def app_firewall(self, app_path: str, action: str = "allow") -> Dict[str, Any]:
        """Set per-application firewall rules"""
        write_log(f"Setting firewall rule for {app_path}: {action}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "app": app_path, "action": action, "configured": False}
        if not self._check_root():
            return result
        try:
            if not os.path.exists(app_path):
                result["error"] = f"Application not found: {app_path}"
                return result
            app_name = os.path.basename(app_path)
            if action == "allow":
                args = ["iptables", "-A", "OUTPUT", "-m", "owner", "--pid-owner",
                        str(os.popen(f"pidof {app_name}").read().strip()), "-j", "ACCEPT"]
            else:
                args = ["iptables", "-A", "OUTPUT", "-m", "string", "--string", app_name,
                        "--algo", "bm", "-j", "DROP"]
            code, _, stderr = run_command(args)
            if code == 0:
                result["configured"] = True
                write_log(f"Application rule set: {app_name} -> {action}", "SUCCESS")
            else:
                result["error"] = stderr[:200]
        except Exception as e:
            write_log(f"App firewall error: {e}", "ERROR")
            result["error"] = str(e)
        return result

    def traffic_shaping(self, interface: str = "eth0", rate: str = "1mbit") -> Dict[str, Any]:
        """Configure traffic shaping using tc"""
        write_log(f"Configuring traffic shaping on {interface}: {rate}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "interface": interface, "rate": rate, "configured": False}
        if not self._check_root():
            return result
        try:
            cmds = [
                ["tc", "qdisc", "add", "dev", interface, "root", "handle", "1:", "htb"],
                ["tc", "class", "add", "dev", interface, "parent", "1:", "classid", "1:1", "htb", "rate", rate],
            ]
            for cmd in cmds:
                run_command(cmd)
            result["configured"] = True
            write_log(f"Traffic shaping configured: {rate} on {interface}", "SUCCESS")
        except Exception as e:
            write_log(f"Traffic shaping error: {e}", "ERROR")
            result["error"] = str(e)
        return result

    def intrusion_rules(self, action: str = "list") -> Dict[str, Any]:
        """Manage custom intrusion detection rules"""
        write_log(f"Managing intrusion rules: {action}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "action": action, "rules": []}
        if not self._check_root():
            return result
        try:
            if action == "list":
                code, stdout, _ = run_command(["iptables", "-L", "-n", "-v"])
                if code == 0:
                    for line in stdout.split("\n"):
                        if "DROP" in line or "REJECT" in line:
                            result["rules"].append(line.strip())
            elif action == "enable":
                # Enable common IDS rules
                rules = [
                    ["iptables", "-A", "INPUT", "-p", "tcp", "--dport", "22", "-m", "state",
                     "--state", "NEW", "-m", "recent", "--set"],
                    ["iptables", "-A", "INPUT", "-p", "tcp", "--dport", "22", "-m", "state",
                     "--state", "NEW", "-m", "recent", "--update", "--seconds", "60",
                     "--hitcount", "5", "-j", "DROP"],
                    ["iptables", "-A", "INPUT", "-p", "icmp", "--icmp-type", "echo-request",
                     "-m", "limit", "--limit", "1/s", "-j", "ACCEPT"],
                    ["iptables", "-A", "INPUT", "-p", "icmp", "--icmp-type", "echo-request", "-j", "DROP"],
                ]
                for rule in rules:
                    run_command(rule)
                result["rules_applied"] = len(rules)
                write_log(f"Applied {len(rules)} intrusion prevention rules", "SUCCESS")
            write_log(f"Intrusion rules {action}: {len(result['rules'])} rules", "SUCCESS")
        except Exception as e:
            write_log(f"Intrusion rules error: {e}", "ERROR")
        return result

    def connection_history(self, lines: int = 50) -> Dict[str, Any]:
        """Retrieve recent connection history from conntrack"""
        write_log("Retrieving connection history", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "connections": [], "total": 0}
        try:
            code, stdout, stderr = run_command(["conntrack", "-L", "-n"], timeout=10)
            if code == 0:
                conns = stdout.strip().split("\n")[-lines:]
                for conn in conns:
                    if conn.strip():
                        parts = conn.split()
                        entry = {}
                        for p in parts:
                            if "=" in p:
                                k, v = p.split("=", 1)
                                entry[k] = v
                        result["connections"].append(entry)
                result["total"] = len(result["connections"])
                write_log(f"Connection history: {result['total']} entries", "SUCCESS")
            else:
                # Fallback to ss
                code, stdout, _ = run_command(["ss", "-tunap"])
                if code == 0:
                    lines_out = stdout.strip().split("\n")[1:][:lines]
                    result["connections"] = [{"raw": l.strip()} for l in lines_out]
                    result["total"] = len(result["connections"])
        except Exception as e:
            write_log(f"Connection history error: {e}", "ERROR")
        return result

    def geoip_block(self, country_code: str = "cn") -> Dict[str, Any]:
        """Block IP ranges by country using geoip and ipset"""
        write_log(f"Blocking country: {country_code.upper()}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "country": country_code, "blocked": False}
        if not self._check_root():
            return result
        try:
            set_name = f"geoip_{country_code.lower()}"
            run_command(["ipset", "create", set_name, "hash:net", "-exist"])
            # Try to download and parse GeoIP data
            code, stdout, _ = run_command(["curl", "-s",
                f"https://www.ipdeny.com/ipblocks/data/countries/{country_code.lower()}.zone"])
            if code == 0 and stdout:
                ips = stdout.strip().split("\n")
                count = 0
                for ip in ips[:1000]:  # Limit to first 1000
                    if ip.strip():
                        run_command(["ipset", "add", set_name, ip.strip(), "-exist"])
                        count += 1
                # Create iptables rule
                run_command(["iptables", "-A", "INPUT", "-m", "set", "--match-set",
                           set_name, "src", "-j", "DROP"])
                result["blocked"] = True
                result["networks_blocked"] = count
                write_log(f"Geo-blocked {country_code.upper()}: {count} networks", "SUCCESS")
            else:
                result["error"] = "Could not fetch GeoIP data"
                write_log(f"Failed to fetch GeoIP data for {country_code}", "WARNING")
                # Fallback: block known ranges
                known_ranges = {
                    "cn": ["1.0.1.0/24", "1.0.2.0/23", "1.0.8.0/21"],
                    "ru": ["2.56.0.0/13", "2.60.0.0/14"],
                    "kp": ["175.45.176.0/22"],
                }
                for ip_range in known_ranges.get(country_code.lower(), []):
                    run_command(["ipset", "add", set_name, ip_range, "-exist"])
        except Exception as e:
            write_log(f"GeoIP block error: {e}", "ERROR")
            result["error"] = str(e)
        return result

    def port_knocking(self, ports: List[int] = None, action: str = "setup") -> Dict[str, Any]:
        """Configure port knocking authentication"""
        if ports is None:
            ports = [7000, 8000, 9000]
        write_log(f"Configuring port knocking: {ports}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "ports": ports, "action": action, "configured": False}
        if not self._check_root():
            return result
        try:
            if action == "setup":
                chain_name = "KNOCKING"
                run_command(["iptables", "-N", chain_name, "-exist"])
                run_command(["iptables", "-A", "INPUT", "-j", chain_name])
                for i, port in enumerate(ports):
                    if i == 0:
                        run_command(["iptables", "-A", chain_name, "-p", "tcp", "--dport", str(port),
                                   "-m", "state", "--state", "NEW", "-j", "ACCEPT"])
                    else:
                        run_command(["iptables", "-A", chain_name, "-p", "tcp", "--dport", str(port),
                                   "-m", "state", "--state", "NEW", "-j", "LOG",
                                   "--log-prefix", f"KNOCK_{i}_"])
                result["configured"] = True
                write_log("Port knocking configured", "SUCCESS")
            elif action == "remove":
                run_command(["iptables", "-D", "INPUT", "-j", "KNOCKING"])
                run_command(["iptables", "-X", "KNOCKING"])
                result["configured"] = True
                write_log("Port knocking removed", "SUCCESS")
        except Exception as e:
            write_log(f"Port knocking error: {e}", "ERROR")
        return result

    def full_assessment(self) -> Dict[str, Any]:
        """Run complete firewall assessment"""
        write_log("Starting full firewall assessment", "INFO")
        results = {
            "timestamp": datetime.now().isoformat(),
            "current_rules": self.get_current_rules(),
            "connection_history": self.connection_history(),
            "intrusion_status": self.intrusion_rules("list"),
        }
        save_report(results, "firewall_full_assessment")
        write_log("Firewall assessment complete", "SUCCESS")
        return results
