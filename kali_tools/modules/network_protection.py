"""
ZELZAL Network Protection Module v5.0
Real implementations using Kali Linux tools: nmap, scapy, iptables, aircrack-ng
"""

import os
import ipaddress
import socket
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any



from core import write_log, run_command, save_report, is_root, check_dependencies

MODULE_NAME = "network_protection"
REQUIRED_TOOLS = ["nmap", "arp-scan", "iwconfig", "iwlist", "speedtest-cli", "tshark"]


class NetworkProtection:
    """Network security assessment and monitoring"""

    def __init__(self):
        self.name = MODULE_NAME
        self.tools = check_dependencies(REQUIRED_TOOLS)
        self.scan_results = {}

    def check_status(self) -> Dict[str, Any]:
        found = [t for t, v in self.tools.items() if v]
        return {
            "module": self.name,
            "status": "available" if len(found) > len(self.tools) // 2 else "limited",
            "tools_found": found,
            "tools_missing": [t for t in self.tools if not self.tools[t]],
            "timestamp": datetime.now().isoformat(),
        }

    def arp_spoofing_check(self, interface: str = "eth0") -> Dict[str, Any]:
        """Detect ARP spoofing attacks on the local network"""
        write_log("Starting ARP spoofing detection", "INFO")
        result = {
            "timestamp": datetime.now().isoformat(),
            "interface": interface,
            "spoofing_detected": False,
            "suspicious_pairs": [],
            "gateway_mac": None,
        }
        try:
            code, stdout, stderr = run_command(["arp-scan", "--local", "--retry=3"])
            if "arp-scan" not in self.tools or not self.tools["arp-scan"]:
                code, stdout, stderr = run_command(["arp", "-a"])

            if code == 0:
                lines = stdout.strip().split("\n")
                gateway = None
                mac_counts = {}
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 3 and "(" in line:
                        ip = parts[0].strip("()")
                        mac = parts[1] if len(parts) > 1 else ""
                        if "gateway" in line.lower() or ip.endswith(".1") or ip.endswith(".254"):
                            gateway = {"ip": ip, "mac": mac}
                        if mac:
                            mac_counts[mac] = mac_counts.get(mac, []) + [ip]

                result["gateway_mac"] = gateway
                for mac, ips in mac_counts.items():
                    if len(ips) > 1:
                        result["suspicious_pairs"].append({
                            "mac": mac, "ips": ips, "type": "MITM"
                        })
                        result["spoofing_detected"] = True

                write_log(f"ARP spoofing check complete: {len(lines)} devices, "
                          f"{'spoofing detected' if result['spoofing_detected'] else 'no threats'}", "SUCCESS")
            else:
                write_log(f"ARP scan failed: {stderr[:100]}", "WARNING")
        except Exception as e:
            write_log(f"ARP check error: {e}", "ERROR")
        return result

    def network_scan(self, target: str = "192.168.1.0/24", fast: bool = True) -> Dict[str, Any]:
        """Run network scan using nmap"""
        write_log(f"Starting {'fast' if fast else 'full'} network scan: {target}", "INFO")
        result = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "mode": "fast" if fast else "full",
            "hosts_up": 0,
            "hosts": [],
        }
        if not self.tools.get("nmap"):
            write_log("nmap not installed, using basic ping scan", "WARNING")
            return self._basic_scan(target)

        try:
            args = ["nmap", "-sn", "-T4", target] if fast else ["nmap", "-sV", "-O", "-T4", target]
            code, stdout, stderr = run_command(args, timeout=120)
            if code == 0:
                hosts = []
                current_host = {}
                for line in stdout.split("\n"):
                    if "Nmap scan report for" in line:
                        if current_host:
                            hosts.append(current_host)
                        host_info = line.split("for")[-1].strip()
                        current_host = {"host": host_info, "ports": []}
                        result["hosts_up"] += 1
                    elif "open" in line and not fast:
                        parts = line.split()
                        if len(parts) >= 2:
                            port = parts[0]
                            service = parts[2] if len(parts) > 2 else "unknown"
                            current_host["ports"].append(f"{port}/{service}")
                if current_host:
                    hosts.append(current_host)
                result["hosts"] = hosts
                write_log(f"Network scan complete: {result['hosts_up']} hosts up", "SUCCESS")
            else:
                write_log(f"Nmap scan failed: {stderr[:100]}", "WARNING")
                return self._basic_scan(target)
        except Exception as e:
            write_log(f"Scan error: {e}", "ERROR")
            return self._basic_scan(target)
        return result

    def _basic_scan(self, target: str) -> Dict[str, Any]:
        """Basic ping-based network scan as fallback"""
        result = {"timestamp": datetime.now().isoformat(), "target": target, "mode": "basic", "hosts_up": 0, "hosts": []}
        try:
            network = ipaddress.ip_network(target, strict=False)
            for ip in network.hosts():
                ip_str = str(ip)
                code, _, _ = run_command(["ping", "-c", "1", "-W", "1", ip_str], timeout=2)
                if code == 0:
                    result["hosts"].append({"host": ip_str, "ports": []})
                    result["hosts_up"] += 1
        except Exception as e:
            write_log(f"Basic scan error: {e}", "ERROR")
        return result

    def wifi_scanner(self, interface: str = "wlan0") -> Dict[str, Any]:
        """Scan for nearby WiFi networks"""
        write_log(f"Scanning WiFi networks on {interface}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "interface": interface, "networks": []}
        try:
            code, stdout, stderr = run_command(["iwlist", interface, "scan"])
            if code != 0:
                code, stdout, stderr = run_command(["iw", interface, "scan"])
            if code == 0:
                current = {}
                for line in stdout.split("\n"):
                    if "ESSID:" in line:
                        current["ssid"] = line.split("ESSID:")[-1].strip().strip('"')
                    elif "Address:" in line:
                        current["bssid"] = line.split("Address:")[-1].strip()
                    elif "Channel:" in line:
                        try:
                            current["channel"] = int(line.split("Channel:")[-1].strip())
                        except ValueError:
                            pass
                    elif "Signal level=" in line:
                        try:
                            part = line.split("Signal level=")[-1].split()[0]
                            current["signal_dbm"] = part
                        except (IndexError, ValueError):
                            pass
                    elif "Encryption" in line and ":" in line:
                        current["encryption"] = line.split(":")[-1].strip()
                        if current.get("ssid"):
                            result["networks"].append(current)
                            current = {}
                if current.get("ssid"):
                    result["networks"].append(current)
                write_log(f"Found {len(result['networks'])} WiFi networks", "SUCCESS")
            else:
                write_log(f"WiFi scan failed: {stderr[:100]}", "WARNING")
        except Exception as e:
            write_log(f"WiFi scan error: {e}", "ERROR")
        return result

    def speed_test(self) -> Dict[str, Any]:
        """Test network speed using speedtest-cli"""
        write_log("Running network speed test", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "download_mbps": 0, "upload_mbps": 0, "ping_ms": 0}
        try:
            if self.tools.get("speedtest-cli"):
                code, stdout, stderr = run_command(["speedtest-cli", "--simple"], timeout=60)
                if code == 0:
                    for line in stdout.split("\n"):
                        if "Ping:" in line:
                            result["ping_ms"] = float(line.split()[-2] if line.split()[-1] == "ms" else line.split()[-1])
                        elif "Download:" in line:
                            result["download_mbps"] = float(line.split()[-2])
                        elif "Upload:" in line:
                            result["upload_mbps"] = float(line.split()[-2])
                write_log(f"Speed test: {result['download_mbps']} Mbps down / {result['upload_mbps']} Mbps up", "SUCCESS")
            else:
                result["error"] = "speedtest-cli not installed"
                write_log("speedtest-cli not available", "WARNING")
        except Exception as e:
            write_log(f"Speed test error: {e}", "ERROR")
        return result

    def block_malicious_ips(self, ips: List[str]) -> Dict[str, Any]:
        """Block malicious IPs using iptables/nftables"""
        write_log(f"Blocking {len(ips)} malicious IPs", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "blocked": [], "failed": []}
        if not is_root():
            write_log("Root privileges required to block IPs", "ERROR")
            result["error"] = "Root privileges required"
            return result
        for ip in ips:
            try:
                code, _, stderr = run_command(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
                if code == 0:
                    result["blocked"].append(ip)
                    write_log(f"Blocked IP: {ip}", "SUCCESS")
                else:
                    result["failed"].append({"ip": ip, "error": stderr[:50]})
            except Exception as e:
                result["failed"].append({"ip": ip, "error": str(e)})
        return result

    def dhcp_snooping_check(self) -> Dict[str, Any]:
        """Check for rogue DHCP servers"""
        write_log("Checking for rogue DHCP servers", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "rogue_dhcp": False, "dhcp_servers": []}
        try:
            code, stdout, stderr = run_command(["nmap", "--script=broadcast-dhcp-discover", "-e", "eth0"])
            if code == 0 and "DHCP" in stdout:
                for line in stdout.split("\n"):
                    if "DHCP" in line or "Server" in line:
                        result["dhcp_servers"].append(line.strip())
                if len(result["dhcp_servers"]) > 1:
                    result["rogue_dhcp"] = True
            write_log(f"DHCP check: {len(result['dhcp_servers'])} servers found", "SUCCESS")
        except Exception as e:
            write_log(f"DHCP check error: {e}", "ERROR")
        return result

    def bandwidth_hogs(self, interface: str = "eth0") -> Dict[str, Any]:
        """Identify bandwidth-heavy connections"""
        write_log("Analyzing bandwidth usage", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "connections": [], "total_connections": 0}
        try:
            code, stdout, stderr = run_command(["ss", "-tun"], timeout=10)
            if code == 0:
                lines = stdout.strip().split("\n")[1:]
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 5:
                        result["connections"].append({
                            "protocol": parts[0],
                            "local": parts[4] if len(parts) > 4 else "",
                            "remote": parts[5] if len(parts) > 5 else "",
                            "state": parts[1] if len(parts) > 1 else "",
                        })
                result["total_connections"] = len(result["connections"])
            write_log(f"Bandwidth: {result['total_connections']} active connections", "SUCCESS")
        except Exception as e:
            write_log(f"Bandwidth check error: {e}", "ERROR")
        return result

    def ipv6_security_audit(self) -> Dict[str, Any]:
        """Audit IPv6 security configuration"""
        write_log("Auditing IPv6 security", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "ipv6_enabled": False, "issues": []}
        try:
            code, stdout, stderr = run_command(["sysctl", "net.ipv6.conf.all.disable_ipv6"])
            if code == 0:
                val = stdout.strip().split("=")[-1].strip()
                result["ipv6_enabled"] = val == "0"
                if result["ipv6_enabled"]:
                    result["issues"].append("IPv6 enabled - ensure firewall rules cover IPv6")
            code, stdout, stderr = run_command(["ip", "-6", "addr"])
            if code == 0:
                result["ipv6_addresses"] = len([l for l in stdout.split("\n") if "inet6" in l])
            write_log("IPv6 audit complete", "SUCCESS")
        except Exception as e:
            write_log(f"IPv6 audit error: {e}", "ERROR")
        return result

    def bluetooth_scan(self) -> Dict[str, Any]:
        """Scan for nearby Bluetooth devices"""
        write_log("Scanning Bluetooth devices", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "devices": []}
        try:
            code, stdout, stderr = run_command(["bluetoothctl", "scan", "on"], timeout=10)
            if code != 0:
                code, stdout, stderr = run_command(["hcitool", "scan"], timeout=10)
            if code == 0:
                for line in stdout.split("\n"):
                    if "Device" in line or ":" in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            result["devices"].append(line.strip())
                write_log(f"Found {len(result['devices'])} Bluetooth devices", "SUCCESS")
        except Exception as e:
            write_log(f"Bluetooth scan error: {e}", "ERROR")
        return result

    def data_usage_stats(self) -> Dict[str, Any]:
        """Retrieve network data usage statistics"""
        write_log("Collecting data usage statistics", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "interfaces": []}
        try:
            if os.name == 'nt':
                code, stdout, _ = run_command(
                    ["powershell", "Get-NetAdapterStatistics | Select-Object Name, ReceivedBytes, SentBytes | ConvertTo-Json"]
                )
                if code == 0 and stdout.strip():
                    import json as _json
                    stats = _json.loads(stdout.strip())
                    if not isinstance(stats, list):
                        stats = [stats]
                    for s in stats:
                        name = s.get("Name", "unknown")
                        rx = int(s.get("ReceivedBytes", 0))
                        tx = int(s.get("SentBytes", 0))
                        result["interfaces"].append({
                            "interface": name,
                            "rx_bytes": rx,
                            "tx_bytes": tx,
                            "rx_mb": round(rx / 1024 / 1024, 2),
                            "tx_mb": round(tx / 1024 / 1024, 2),
                        })
            else:
                for iface_dir in Path("/sys/class/net").iterdir():
                    iface = iface_dir.name
                    rx_file = iface_dir / "statistics" / "rx_bytes"
                    tx_file = iface_dir / "statistics" / "tx_bytes"
                    if rx_file.exists() and tx_file.exists():
                        rx = int(rx_file.read_text().strip())
                        tx = int(tx_file.read_text().strip())
                        result["interfaces"].append({
                            "interface": iface,
                            "rx_bytes": rx,
                            "tx_bytes": tx,
                            "rx_mb": round(rx / 1024 / 1024, 2),
                            "tx_mb": round(tx / 1024 / 1024, 2),
                        })
            write_log(f"Data usage: {len(result['interfaces'])} interfaces", "SUCCESS")
        except Exception as e:
            write_log(f"Data usage error: {e}", "ERROR")
        return result

    def fake_ap_detection(self, interface: str = "wlan0") -> Dict[str, Any]:
        """Detect rogue/fake access points"""
        write_log("Detecting fake access points", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "fake_aps": [], "total_aps": 0}
        scan_result = self.wifi_scanner(interface)
        result["total_aps"] = len(scan_result.get("networks", []))
        ssid_counts = {}
        for net in scan_result.get("networks", []):
            ssid = net.get("ssid", "")
            if ssid:
                ssid_counts[ssid] = ssid_counts.get(ssid, 0) + 1
        for ssid, count in ssid_counts.items():
            if count > 1:
                result["fake_aps"].append({"ssid": ssid, "count": count})
        write_log(f"Fake AP check: {len(result['fake_aps'])} potential fake APs", "SUCCESS")
        return result

    def device_report(self) -> Dict[str, Any]:
        """Generate comprehensive network device report"""
        write_log("Generating network device report", "INFO")
        scan = self.network_scan(fast=True)
        arp = self.arp_spoofing_check()
        report = {
            "timestamp": datetime.now().isoformat(),
            "scan_summary": {
                "total_hosts": scan.get("hosts_up", 0),
                "hosts": scan.get("hosts", []),
            },
            "arp_check": {
                "spoofing_detected": arp.get("spoofing_detected", False),
                "suspicious_pairs": arp.get("suspicious_pairs", []),
            },
        }
        save_report(report, "network_device_report")
        return report

    def smb_scan(self, target: str = "192.168.1.0/24") -> Dict[str, Any]:
        """Scan for accessible SMB shares"""
        write_log(f"Scanning SMB shares: {target}", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "target": target, "shares": []}
        try:
            code, stdout, stderr = run_command(["nmap", "-p", "445", "--open", "-T4", target], timeout=120)
            if code == 0:
                for line in stdout.split("\n"):
                    if "Nmap scan report for" in line:
                        host = line.split("for")[-1].strip()
                        result["shares"].append({"host": host, "port": 445, "service": "SMB"})
                write_log(f"SMB scan: {len(result['shares'])} hosts with SMB open", "SUCCESS")
        except Exception as e:
            write_log(f"SMB scan error: {e}", "ERROR")
        return result

    def mdns_discovery(self) -> Dict[str, Any]:
        """Discover mDNS devices on the network"""
        write_log("Discovering mDNS devices", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "devices": []}
        try:
            code, stdout, stderr = run_command(["avahi-browse", "-a", "-t"], timeout=10)
            if code == 0:
                for line in stdout.split("\n"):
                    if "=" in line and any(s in line for s in ["_http", "_ssh", "_sftp", "_airplay"]):
                        result["devices"].append(line.strip())
            write_log(f"mDNS discovery: {len(result['devices'])} services found", "SUCCESS")
        except Exception as e:
            write_log(f"mDNS error: {e}", "ERROR")
        return result

    def packet_capture(self, interface: str = "eth0", packet_count: int = 50, filter_expr: str = "") -> Dict[str, Any]:
        result = {"module": "packet_capture", "interface": interface, "packets": [], "packet_count": 0}
        # Try tshark first
        tshark_cmd = ["tshark", "-i", interface, "-c", str(packet_count), "-T", "fields",
               "-e", "frame.number", "-e", "frame.time", "-e", "ip.src", "-e", "ip.dst",
               "-e", "ip.proto", "-e", "tcp.port", "-e", "udp.port", "-e", "frame.len"]
        if filter_expr:
            tshark_cmd += ["-f", filter_expr]
        code, out, err = run_command(tshark_cmd, timeout=30)
        if code == 0 and out.strip():
            for line in out.strip().split("\n"):
                parts = line.split("\t")
                if len(parts) >= 4:
                    result["packets"].append({
                        "frame": parts[0], "time": parts[1] if len(parts) > 1 else "",
                        "src": parts[2] if len(parts) > 2 else "",
                        "dst": parts[3] if len(parts) > 3 else "",
                        "proto": parts[4] if len(parts) > 4 else "",
                        "port": parts[5] if len(parts) > 5 else parts[6] if len(parts) > 6 else "",
                        "len": parts[7] if len(parts) > 7 else "",
                    })
            result["packet_count"] = len(result["packets"])
            return result
        # Fallback: netstat connection monitor
        code2, out2, _ = run_command(["netstat", "-an"], timeout=5)
        if code2 == 0 and out2:
            for line in out2.split("\n"):
                parts = line.split()
                if len(parts) >= 4 and parts[0] in ("TCP", "UDP"):
                    local = parts[1]
                    remote = parts[2] if len(parts) > 2 else ""
                    state = parts[3] if len(parts) > 3 else ""
                    l_ip, l_port = (local.rsplit(":", 1) + [""])[:2]
                    r_ip, r_port = (remote.rsplit(":", 1) + [""])[:2]
                    if l_port and r_port:
                        result["packets"].append({
                            "proto": parts[0], "src": l_ip, "sport": l_port,
                            "dst": r_ip, "dport": r_port, "state": state,
                        })
            result["packet_count"] = len(result["packets"])
            result["tool"] = "netstat"
            if not result["packets"]:
                result["note"] = "No active connections"
        else:
            result["error"] = err or "packet capture unavailable (install tshark or run as admin)"
        return result

    def protocol_analysis(self, interface: str = "eth0", duration: int = 10) -> Dict[str, Any]:
        result = {"module": "protocol_analysis", "interface": interface, "protocols": {}}
        cmd = ["tshark", "-i", interface, "-a", f"duration:{duration}",
               "-T", "fields", "-e", "ip.proto", "-e", "frame.len"]
        code, out, err = run_command(cmd, timeout=duration + 10)
        if code == 0 and out.strip():
            proto_map = {"6": "TCP", "17": "UDP", "1": "ICMP", "2": "IGMP",
                         "132": "SCTP", "33": "DCCP", "47": "GRE"}
            total_bytes = 0
            for line in out.strip().split("\n"):
                parts = line.split("\t")
                proto = parts[0] if parts else "0"
                pname = proto_map.get(proto, f"PROTO-{proto}")
                result["protocols"][pname] = result["protocols"].get(pname, 0) + 1
                if len(parts) > 1 and parts[1].isdigit():
                    total_bytes += int(parts[1])
            result["total_packets"] = sum(result["protocols"].values())
            result["total_bytes"] = total_bytes
            return result
        # Fallback: netstat -s for protocol stats
        code2, out2, _ = run_command(["netstat", "-s"], timeout=5)
        if code2 == 0 and out2:
            result["tool"] = "netstat"
            current_proto = ""
            for line in out2.split("\n"):
                stripped = line.strip()
                if stripped in ("IPv4 Statistics", "IPv6 Statistics", "ICMPv4 Statistics", "ICMPv6 Statistics",
                               "TCP Statistics", "UDP Statistics"):
                    current_proto = stripped.split()[0]
                    result["protocols"][current_proto] = []
                elif current_proto and stripped:
                    result["protocols"][current_proto].append(stripped[:100])
        else:
            result["error"] = err or "protocol analysis unavailable (install tshark)"
        return result

    def dns_analysis(self, interface: str = "eth0", duration: int = 15) -> Dict[str, Any]:
        result = {"module": "dns_analysis", "interface": interface, "queries": []}
        cmd = ["tshark", "-i", interface, "-a", f"duration:{duration}",
               "-Y", "dns.flags.response == 0", "-T", "fields",
               "-e", "dns.qry.name", "-e", "dns.qry.type", "-e", "dns.qry.class"]
        code, out, err = run_command(cmd, timeout=duration + 10)
        if code == 0 and out.strip():
            for line in out.strip().split("\n"):
                parts = line.split("\t")
                if parts[0]:
                    result["queries"].append({"query": parts[0],
                        "type": parts[1] if len(parts) > 1 else "",
                        "class": parts[2] if len(parts) > 2 else ""})
            result["total_queries"] = len(result["queries"])
            return result
        # Fallback: nslookup queries to common domains
        domains = ["google.com", "github.com", "cloudflare.com", "facebook.com", "youtube.com"]
        for domain in domains:
            code2, out2, _ = run_command(["nslookup", domain], timeout=5)
            if code2 == 0:
                for line in out2.split("\n"):
                    if "Address:" in line and not line.startswith(">"):
                        addr = line.split("Address:")[-1].strip()
                        if addr and addr != domain:
                            result["queries"].append({"query": domain, "resolved": addr})
                            break
        result["total_queries"] = len(result["queries"])
        result["tool"] = "nslookup" if result["queries"] else "unavailable"
        return result

    def http_analysis(self, interface: str = "eth0", duration: int = 15) -> Dict[str, Any]:
        result = {"module": "http_analysis", "interface": interface, "requests": []}
        cmd = ["tshark", "-i", interface, "-a", f"duration:{duration}",
               "-Y", "http.request", "-T", "fields",
               "-e", "http.request.method", "-e", "http.request.uri",
               "-e", "http.host", "-e", "http.response.code"]
        code, out, err = run_command(cmd, timeout=duration + 10)
        if code == 0 and out.strip():
            for line in out.strip().split("\n"):
                parts = line.split("\t")
                if parts[0]:
                    result["requests"].append({
                        "method": parts[0], "uri": parts[1] if len(parts) > 1 else "",
                        "host": parts[2] if len(parts) > 2 else "",
                        "response": parts[3] if len(parts) > 3 else ""})
            result["total_requests"] = len(result["requests"])
            return result
        # Fallback: curl/urllib probes to common sites
        targets = [("http://google.com", "GET", "/"),
                   ("http://github.com", "GET", "/"),
                   ("http://cloudflare.com", "GET", "/")]
        for url, method, path in targets:
            code2, out2, _ = run_command(["curl", "-sI", "-o", "/dev/null", "-w",
                                          "%{http_code}:%{content_type}:%{size_download}", url], timeout=10)
            if code2 == 0 and out2:
                parts = out2.strip().split(":")
                result["requests"].append({
                    "method": method, "uri": path,
                    "host": url.split("://")[1],
                    "response": parts[0] if parts else "",
                    "size": parts[2] if len(parts) > 2 else ""})
        if not result["requests"]:
            try:
                import urllib.request
                for url, method, path in targets:
                    req = urllib.request.Request(url, method=method)
                    resp = urllib.request.urlopen(req, timeout=5)
                    result["requests"].append({
                        "method": method, "uri": path,
                        "host": url.split("://")[1],
                        "response": str(resp.status),
                        "size": str(len(resp.read()))})
                    resp.close()
            except Exception as e:
                result["note"] = f"urllib fallback: {e}"
        result["total_requests"] = len(result["requests"])
        result["tool"] = "curl" if result["requests"] else "unavailable"
        return result

    def full_assessment(self) -> Dict[str, Any]:
        write_log("Starting full network security assessment", "INFO")
        results = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {
                "hostname": socket.gethostname(),
                "local_ip": socket.gethostbyname(socket.gethostname()),
            },
            "arp_check": self.arp_spoofing_check(),
            "network_scan": self.network_scan(fast=True),
            "bandwidth": self.bandwidth_hogs(),
            "ipv6_audit": self.ipv6_security_audit(),
            "data_usage": self.data_usage_stats(),
            "dhcp_check": self.dhcp_snooping_check(),
            "packet_capture": self.packet_capture(),
            "dns_analysis": self.dns_analysis(),
        }
        save_report(results, "network_full_assessment")
        write_log("Network assessment complete", "SUCCESS")
        return results
