#!/usr/bin/env python3
"""
ZELZAL v5.0 - Kali Linux Cybersecurity Toolkit
Advanced terminal UI for security assessment and hardening

Usage:
    python3 zelzal.py          # Interactive TUI mode
    python3 zelzal.py --scan   # Quick system scan
    python3 zelzal.py --report # Generate full report
"""

import os
import sys
import signal
from datetime import datetime
from typing import Optional

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    from rich.columns import Columns
    from rich.live import Live
    from rich import box
    from rich.markdown import Markdown
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from core import (
    write_log, get_config, set_config, generate_password,
    is_root, is_kali, get_system_info, check_dependencies,
    save_report, encrypt_file, decrypt_file, clear_old_logs,
    VERSION,
)
from modules import (
    NetworkProtection,
    WebProtection,
    FirewallAdvanced,
    SystemProtection,
    PerformanceProtection,
    IdentityProtection,
    ContainerSecurity,
    WirelessSecurity,
    ExploitDetection,
    Reconnaissance,
    WebAppScanning,
    Exploitation,
    Forensics,
    CloudSecurity,
)


console = Console() if HAS_RICH else None

BANNER = """
███████╗███████╗██╗     ███████╗ █████╗ ██╗
╚══███╔╝╚══███╔╝██║     ██╔════╝██╔══██╗██║
  ███╔╝   ███╔╝ ██║     █████╗  ███████║██║
 ███╔╝   ███╔╝  ██║     ██╔══╝  ██╔══██║██║
███████╗███████╗███████╗███████╗██║  ██║███████╗
╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝╚══════╝
"""


class ZelzalTUI:
    """Main Terminal User Interface for ZELZAL Security Toolkit"""

    def __init__(self):
        self.network = NetworkProtection()
        self.web = WebProtection()
        self.firewall = FirewallAdvanced()
        self.system = SystemProtection()
        self.performance = PerformanceProtection()
        self.identity = IdentityProtection()
        self.container = ContainerSecurity()
        self.wireless = WirelessSecurity()
        self.exploit = ExploitDetection()
        self.recon = Reconnaissance()
        self.webapp = WebAppScanning()
        self.exploitation = Exploitation()
        self.forensics = Forensics()
        self.cloud = CloudSecurity()
        self.system_info = get_system_info()
        self.running = True

    def clear(self):
        if HAS_RICH:
            console.clear()

    def print_banner(self):
        if HAS_RICH:
            banner_style = "bold green" if is_kali() else "bold yellow"
            console.print(Text(BANNER, style=banner_style))
            version_text = Text(f"═══ v{VERSION} ═══ Kali Linux Cybersecurity Toolkit ═══", style="bold green")
            console.print(version_text)
            console.print(f"  Host: {self.system_info.get('hostname', 'unknown')}")
            console.print(f"  Kernel: {self.system_info.get('release', 'unknown')}")
            console.print(f"  Root: {'✓' if is_root() else '✗'}")
            console.print()
        else:
            print(BANNER)
            print(f"ZELZAL v{VERSION} - Kali Linux Cybersecurity Toolkit")
            print(f"Host: {self.system_info.get('hostname', 'unknown')}")
            print()

    def print_menu(self):
        if HAS_RICH:
            table = Table(show_header=False, box=box.HEAVY, border_style="green")
            table.add_column("Option", style="bold green", width=5)
            table.add_column("Module", style="cyan", width=25)
            table.add_column("Description", style="white")
            menu_items = [
                ("1", "Network Protection", "ARP scan, WiFi, bandwidth, SMB, full assessment"),
                ("2", "Web Protection", "Phishing check, DNS test, privacy clean, data leak scan"),
                ("3", "Advanced Firewall", "Rules, traffic shaping, geo-block, port knocking"),
                ("4", "System Protection", "Malware scan, vulnerability check, keylogger detection"),
                ("5", "Performance", "Disk cleanup, memory optimization, startup analysis"),
                ("6", "Identity Protection", "Password audit, 2FA check, breach monitoring"),
                ("7", "Container Security", "Docker, K8s, Trivy vulnerability scan"),
                ("8", "Wireless Security", "Deauth detection, WPS audit, evil twin check"),
                ("9", "Exploit Detection", "CVE scan, rootkit check, port exposure audit"),
                ("A", "Reconnaissance", "Nmap stealth, masscan, enum4linux, dnsrecon"),
                ("B", "Web App Scanning", "Nikto, wpscan, gobuster, sqlmap, dirb"),
                ("C", "Exploitation", "Hydra, john, metasploit, crackmapexec, bettercap"),
                ("D", "Forensics", "Volatility, binwalk, foremost, steghide, exiftool"),
                ("E", "Cloud Security", "AWS, Azure, GCP, Prowler, ScoutSuite"),
                ("Q", "Quick Scan", "Run all modules in quick-assessment mode"),
                ("F", "Full Report", "Generate comprehensive security report"),
                ("T", "Tools", "Password generator, file encrypt/decrypt, config"),
                ("0", "Exit", "Exit ZELZAL"),
            ]
            for opt, mod, desc in menu_items:
                table.add_row(opt, mod, desc)
            console.print(table)
        else:
            print("\n─── MENU ───")
            print("1. Network Protection    2. Web Protection")
            print("3. Advanced Firewall     4. System Protection")
            print("5. Performance           6. Identity Protection")
            print("7. Container Security    8. Wireless Security")
            print("9. Exploit Detection     A. Reconnaissance")
            print("B. Web App Scanning      C. Exploitation")
            print("D. Forensics             E. Cloud Security")
            print("Q. Quick Scan            F. Full Report")
            print("T. Tools")
            print("0. Exit")

    def run(self):
        """Main TUI loop"""
        if not HAS_RICH:
            print("=" * 60)
            print("ZELZAL Kali Linux Toolkit")
            print("Tip: Install 'rich' for better UI: pip3 install rich")
            print("=" * 60)

        self.clear()
        self.print_banner()

        while self.running:
            self.print_menu()
            choice = Prompt.ask("\n[bold green]Select option[/]" if HAS_RICH else "\nSelect option: ")
            self.clear()
            self.print_banner()
            handlers = {
                "1": self.menu_network,
                "2": self.menu_web,
                "3": self.menu_firewall,
                "4": self.menu_system,
                "5": self.menu_performance,
                "6": self.menu_identity,
                "7": self.menu_container,
                "8": self.menu_wireless,
                "9": self.menu_exploit,
                "A": self.menu_recon,
                "a": self.menu_recon,
                "B": self.menu_webapp,
                "b": self.menu_webapp,
                "C": self.menu_exploitation,
                "c": self.menu_exploitation,
                "D": self.menu_forensics,
                "d": self.menu_forensics,
                "E": self.menu_cloud,
                "e": self.menu_cloud,
                "Q": self.quick_scan,
                "q": self.quick_scan,
                "F": self.full_report,
                "f": self.full_report,
                "T": self.menu_tools,
                "t": self.menu_tools,
                "0": self.exit_app,
            }
            handler = handlers.get(choice)
            if handler:
                handler()
            else:
                if HAS_RICH:
                    console.print("[red]Invalid option[/]")
                else:
                    print("Invalid option")
                Prompt.ask("\nPress Enter to continue")

    def _show_module_menu(self, module_name: str, actions: list, handler_func):
        """Generic module submenu"""
        if HAS_RICH:
            console.print(f"\n[bold cyan]═══ {module_name.upper()} ═══[/]")
            sub_table = Table(show_header=False, box=box.HEAVY, border_style="cyan")
            sub_table.add_column("Option", style="bold cyan", width=5)
            sub_table.add_column("Action", style="white", width=30)
            sub_table.add_column("Description", style="dim white")
            for opt, action, desc in actions:
                sub_table.add_row(opt, action, desc)
            sub_table.add_row("b", "Back to main menu", "")
            console.print(sub_table)
        else:
            print(f"\n--- {module_name} ---")
            for opt, action, desc in actions:
                print(f"{opt}. {action}")
            print("b. Back")
        choice = Prompt.ask("\n[cyan]Select[/]" if HAS_RICH else "\nSelect: ") if HAS_RICH else input("\nSelect: ").strip()
        if choice == "b":
            return
        handler_func(choice)

    # ─── Network Module Menu ───
    def menu_network(self):
        actions = [
            ("1", "ARP Spoofing Check", "Detect MITM attacks"),
            ("2", "Network Scan", "Discover hosts with nmap"),
            ("3", "WiFi Scanner", "Scan nearby networks"),
            ("4", "Speed Test", "Test bandwidth"),
            ("5", "Bandwidth Monitor", "Active connections"),
            ("6", "Packet Capture (Shark)", "Capture packets with tshark"),
            ("7", "Protocol Analysis", "Analyze network protocols"),
            ("8", "DNS Analysis", "Capture and analyze DNS queries"),
            ("9", "HTTP Analysis", "Capture and analyze HTTP traffic"),
            ("0", "Full Assessment", "Complete network audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1": self._show_result(self.network.arp_spoofing_check())
                elif choice == "2": self._show_result(self.network.network_scan())
                elif choice == "3": self._show_result(self.network.wifi_scanner())
                elif choice == "4": self._show_result(self.network.speed_test())
                elif choice == "5": self._show_result(self.network.bandwidth_hogs())
                elif choice == "6":
                    iface = Prompt.ask("Interface", default="eth0")
                    cnt = int(Prompt.ask("Packet count", default="50"))
                    self._show_result(self.network.packet_capture(iface, cnt))
                elif choice == "7":
                    iface = Prompt.ask("Interface", default="eth0")
                    dur = int(Prompt.ask("Duration (seconds)", default="10"))
                    self._show_result(self.network.protocol_analysis(iface, dur))
                elif choice == "8":
                    iface = Prompt.ask("Interface", default="eth0")
                    dur = int(Prompt.ask("Duration (seconds)", default="15"))
                    self._show_result(self.network.dns_analysis(iface, dur))
                elif choice == "9":
                    iface = Prompt.ask("Interface", default="eth0")
                    dur = int(Prompt.ask("Duration (seconds)", default="15"))
                    self._show_result(self.network.http_analysis(iface, dur))
                elif choice == "0": self._show_result(self.network.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Network Protection", actions, handler)

    # ─── Web Module Menu ───
    def menu_web(self):
        actions = [
            ("1", "Phishing Check", "Analyze URL for threats"),
            ("2", "DNS Leak Test", "Check for DNS leaks"),
            ("3", "WebRTC Leak Test", "Check for IP leaks"),
            ("4", "Data Leak Scan", "Check for credential leaks"),
            ("5", "Privacy Cleaner", "Clear browser traces"),
            ("6", "Full Assessment", "Complete web audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1":
                    url = Prompt.ask("Enter URL to check")
                    self._show_result(self.web.phishing_check(url))
                elif choice == "2": self._show_result(self.web.dns_leak_test())
                elif choice == "3": self._show_result(self.web.webrtc_leak_test())
                elif choice == "4":
                    email = Prompt.ask("Enter email (optional)", default="")
                    self._show_result(self.web.data_leak_scan(email or None))
                elif choice == "5": self._show_result(self.web.privacy_cleaner())
                elif choice == "6": self._show_result(self.web.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Web Protection", actions, handler)

    # ─── Firewall Module Menu ───
    def menu_firewall(self):
        actions = [
            ("1", "Show Rules", "Current iptables rules"),
            ("2", "Intrusion Rules", "Enable/List IDS rules"),
            ("3", "Connection History", "Active connections"),
            ("4", "GeoIP Block", "Block country by IP"),
            ("5", "Port Knocking", "Setup/Remove knock auth"),
            ("6", "Full Assessment", "Complete firewall audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1": self._show_result(self.firewall.get_current_rules())
                elif choice == "2": self._show_result(self.firewall.intrusion_rules("list"))
                elif choice == "3": self._show_result(self.firewall.connection_history())
                elif choice == "4":
                    cc = Prompt.ask("Country code (e.g., cn, ru, kp)")
                    self._show_result(self.firewall.geoip_block(cc))
                elif choice == "5": self._show_result(self.firewall.port_knocking())
                elif choice == "6": self._show_result(self.firewall.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Advanced Firewall", actions, handler)

    # ─── System Module Menu ───
    def menu_system(self):
        actions = [
            ("1", "Malware Scan", "Quick ClamAV scan"),
            ("2", "Vulnerability Scan", "Lynis assessment"),
            ("3", "Keylogger Detection", "Find suspicious processes"),
            ("4", "Event Log Analysis", "Check auth/syslog"),
            ("5", "Service Hardening", "Audit system services"),
            ("6", "Full Assessment", "Complete system audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1": self._show_result(self.system.malware_scan(True))
                elif choice == "2": self._show_result(self.system.vulnerability_scan())
                elif choice == "3": self._show_result(self.system.keylogger_detection())
                elif choice == "4": self._show_result(self.system.event_log_analysis())
                elif choice == "5": self._show_result(self.system.service_hardening())
                elif choice == "6": self._show_result(self.system.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("System Protection", actions, handler)

    # ─── Performance Module Menu ───
    def menu_performance(self):
        actions = [
            ("1", "Disk Cleanup", "Free up space"),
            ("2", "Memory Optimizer", "Clear caches, analyze RAM"),
            ("3", "Startup Analyzer", "Check boot services"),
            ("4", "System Health", "CPU, RAM, disk overview"),
            ("5", "Full Assessment", "Complete performance audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1": self._show_result(self.performance.disk_cleanup())
                elif choice == "2": self._show_result(self.performance.memory_optimizer())
                elif choice == "3": self._show_result(self.performance.startup_optimizer())
                elif choice == "4": self._show_result(self.performance.system_health())
                elif choice == "5": self._show_result(self.performance.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Performance Protection", actions, handler)

    # ─── Identity Module Menu ───
    def menu_identity(self):
        actions = [
            ("1", "Password Audit", "Check user password security"),
            ("2", "Password Strength", "Test a password"),
            ("3", "2FA Status", "Check MFA configuration"),
            ("4", "Breach Monitor", "Credential leak check"),
            ("5", "Credential Guard", "PAM and SSH audit"),
            ("6", "Full Assessment", "Complete identity audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1": self._show_result(self.identity.password_audit())
                elif choice == "2":
                    pwd = Prompt.ask("Enter password to test", password=True)
                    self._show_result(self.identity.password_strength(pwd))
                elif choice == "3": self._show_result(self.identity.twofa_status())
                elif choice == "4": self._show_result(self.identity.breach_monitor())
                elif choice == "5": self._show_result(self.identity.credential_guard_check())
                elif choice == "6": self._show_result(self.identity.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Identity Protection", actions, handler)

    # ─── Container Menu ───
    def menu_container(self):
        actions = [
            ("1", "Docker Audit", "Check Docker daemon security"),
            ("2", "Kubernetes Audit", "Check K8s cluster security"),
            ("3", "Trivy Scan", "Vulnerability scan (filesystem)"),
            ("4", "Full Assessment", "Complete container audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1": self._show_result(self.container.docker_audit())
                elif choice == "2": self._show_result(self.container.kubernetes_audit())
                elif choice == "3": self._show_result(self.container.trivy_scan())
                elif choice == "4": self._show_result(self.container.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Container Security", actions, handler)

    # ─── Wireless Menu ───
    def menu_wireless(self):
        actions = [
            ("1", "Interface Audit", "Check wireless interfaces"),
            ("2", "Deauth Detection", "Detect deauthentication attacks"),
            ("3", "Evil Twin Check", "Detect rogue access points"),
            ("4", "WPS Audit", "Check WPS-enabled networks"),
            ("5", "Full Assessment", "Complete wireless audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1": self._show_result(self.wireless.interface_audit())
                elif choice == "2":
                    iface = Prompt.ask("Interface", default="wlan0")
                    sec = int(Prompt.ask("Duration (seconds)", default="10"))
                    self._show_result(self.wireless.deauth_detection(iface, sec))
                elif choice == "3": self._show_result(self.wireless.evil_twin_check())
                elif choice == "4": self._show_result(self.wireless.wps_audit())
                elif choice == "5": self._show_result(self.wireless.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Wireless Security", actions, handler)

    # ─── Exploit Detection Menu ───
    def menu_exploit(self):
        actions = [
            ("1", "CVE Package Scan", "Check installed packages for CVEs"),
            ("2", "Nmap Vuln Scan", "Run vulnerability scan with NSE"),
            ("3", "Rootkit Detection", "Check for rootkits"),
            ("4", "Port Exposure Check", "Audit listening services"),
            ("5", "Full Assessment", "Complete exploit detection audit"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1": self._show_result(self.exploit.cve_scan_packages())
                elif choice == "2":
                    target = Prompt.ask("Target IP", default="127.0.0.1")
                    ports = Prompt.ask("Ports", default="22,80,443,8080")
                    self._show_result(self.exploit.nmap_vuln_scan(target, ports))
                elif choice == "3": self._show_result(self.exploit.rootkit_scan())
                elif choice == "4": self._show_result(self.exploit.port_exposure_check())
                elif choice == "5": self._show_result(self.exploit.full_assessment())
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Exploit Detection", actions, handler)

    # ─── Reconnaissance Menu ───
    def menu_recon(self):
        actions = [
            ("1", "Stealth Nmap Scan", "SYN scan with version detection"),
            ("2", "Masscan", "High-speed port scanner"),
            ("3", "Enum4linux", "Samba/Linux enumeration"),
            ("4", "Smbmap", "SMB share enumeration"),
            ("5", "DNS Recon", "DNS record enumeration"),
            ("6", "Sublist3r", "Subdomain enumeration"),
            ("7", "Amass", "Passive subdomain enumeration"),
            ("8", "TheHarvester", "Email & host discovery"),
            ("9", "WhatWeb", "Web technology detection"),
            ("0", "Full Assessment", "Run all recon tools"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1":
                    t = Prompt.ask("Target", default="127.0.0.1")
                    ps = Prompt.ask("Ports", default="1-1024")
                    self._show_result(self.recon.stealth_nmap_scan(t, ps))
                elif choice == "2":
                    t = Prompt.ask("Target", default="127.0.0.1")
                    ps = Prompt.ask("Ports", default="80,443,22,3389")
                    self._show_result(self.recon.masscan_scan(t, ps))
                elif choice == "3":
                    self._show_result(self.recon.enum4linux_scan(Prompt.ask("Target", default="127.0.0.1")))
                elif choice == "4":
                    self._show_result(self.recon.smbmap_scan(Prompt.ask("Target", default="127.0.0.1")))
                elif choice == "5":
                    self._show_result(self.recon.dns_recon(Prompt.ask("Domain", default="example.com")))
                elif choice == "6":
                    self._show_result(self.recon.sublist3r_scan(Prompt.ask("Domain", default="example.com")))
                elif choice == "7":
                    self._show_result(self.recon.amass_scan(Prompt.ask("Domain", default="example.com")))
                elif choice == "8":
                    self._show_result(self.recon.theharvester_scan(Prompt.ask("Domain", default="example.com")))
                elif choice == "9":
                    self._show_result(self.recon.whatweb_scan(Prompt.ask("Target", default="example.com")))
                elif choice == "0":
                    self._show_result(self.recon.full_assessment(Prompt.ask("Target domain", default="example.com")))
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Reconnaissance", actions, handler)

    # ─── Web App Scanning Menu ───
    def menu_webapp(self):
        actions = [
            ("1", "Nikto Scan", "Web server vulnerability scanner"),
            ("2", "WPScan", "WordPress vulnerability scanner"),
            ("3", "Gobuster", "Directory/file enumeration"),
            ("4", "SQLMap", "SQL injection detection"),
            ("5", "Dirb", "Directory brute-force"),
            ("6", "Joomscan", "Joomla vulnerability scanner"),
            ("7", "Droopescan", "Drupal vulnerability scanner"),
            ("8", "Full Assessment", "Run all web app scanners"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1":
                    self._show_result(self.webapp.nikto_scan(Prompt.ask("Target URL", default="http://localhost:80")))
                elif choice == "2":
                    self._show_result(self.webapp.wpscan_scan(Prompt.ask("Target URL", default="http://localhost")))
                elif choice == "3":
                    t = Prompt.ask("Target URL", default="http://localhost")
                    w = Prompt.ask("Wordlist path", default="/usr/share/wordlists/dirb/common.txt")
                    self._show_result(self.webapp.gobuster_scan(t, w))
                elif choice == "4":
                    self._show_result(self.webapp.sqlmap_scan(Prompt.ask("Target URL with parameter", default="http://localhost/page?id=1")))
                elif choice == "5":
                    t = Prompt.ask("Target URL", default="http://localhost")
                    w = Prompt.ask("Wordlist path", default="/usr/share/wordlists/dirb/common.txt")
                    self._show_result(self.webapp.dirb_scan(t, w))
                elif choice == "6":
                    self._show_result(self.webapp.joomscan_scan(Prompt.ask("Target URL", default="http://localhost")))
                elif choice == "7":
                    self._show_result(self.webapp.droopescan_scan(Prompt.ask("Target URL", default="http://localhost")))
                elif choice == "8":
                    self._show_result(self.webapp.full_assessment(Prompt.ask("Target URL", default="http://localhost")))
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Web App Scanning", actions, handler)

    # ─── Exploitation Menu ───
    def menu_exploitation(self):
        actions = [
            ("1", "Hydra Brute-Force", "Online password cracking"),
            ("2", "CrackMapExec", "SMB/Active Directory assessment"),
            ("3", "Metasploit Scan", "Auxiliary module scanner"),
            ("4", "Impacket Toolkit", "Check available impacket tools"),
            ("5", "Bettercap", "MITM/network reconnaissance"),
            ("6", "Hping3", "Firewall/port testing"),
            ("7", "Medusa Brute-Force", "Parallel password brute-forcer"),
            ("8", "Ncrack Brute-Force", "High-speed network auth cracker"),
            ("9", "Full Assessment", "Run all exploitation tools"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1":
                    t = Prompt.ask("Target", default="127.0.0.1")
                    s = Prompt.ask("Service", default="ssh")
                    u = Prompt.ask("Username", default="root")
                    self._show_result(self.exploitation.hydra_bruteforce(t, s, u))
                elif choice == "2":
                    self._show_result(self.exploitation.crackmapexec_scan(Prompt.ask("Target", default="127.0.0.1")))
                elif choice == "3":
                    t = Prompt.ask("Target", default="127.0.0.1")
                    p = Prompt.ask("Port", default="445")
                    self._show_result(self.exploitation.metasploit_scan(t, p))
                elif choice == "4":
                    self._show_result(self.exploitation.impacket_scan(Prompt.ask("Target", default="127.0.0.1")))
                elif choice == "5":
                    self._show_result(self.exploitation.bettercap_scan(Prompt.ask("Target", default="127.0.0.1")))
                elif choice == "6":
                    self._show_result(self.exploitation.hping3_scan(Prompt.ask("Target", default="127.0.0.1")))
                elif choice == "7":
                    t = Prompt.ask("Target", default="127.0.0.1")
                    s = Prompt.ask("Service", default="ssh")
                    u = Prompt.ask("Username", default="root")
                    self._show_result(self.exploitation.medusa_bruteforce(t, s, u))
                elif choice == "8":
                    t = Prompt.ask("Target", default="127.0.0.1")
                    s = Prompt.ask("Service", default="ssh")
                    self._show_result(self.exploitation.ncrack_bruteforce(t, s))
                elif choice == "9":
                    self._show_result(self.exploitation.full_assessment(Prompt.ask("Target", default="127.0.0.1")))
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Exploitation", actions, handler)

    # ─── Forensics Menu ───
    def menu_forensics(self):
        actions = [
            ("1", "Exiftool", "Extract file metadata"),
            ("2", "Strings", "Extract strings from file"),
            ("3", "Steghide", "Extract hidden data from images"),
            ("4", "Outguess", "Extract steganographic data"),
            ("5", "Zsteg", "Detect LSB steganography in PNG/BMP"),
            ("6", "Binwalk", "Firmware analysis and extraction"),
            ("7", "Bulk Extractor", "Extract forensic artifacts"),
            ("8", "Foremost", "File carving and recovery"),
            ("9", "Full Assessment", "Run all forensics tools"),
        ]
        def handler(choice):
            with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), transient=True) as p:
                p.add_task("Running...", total=None)
                if choice == "1":
                    self._show_result(self.forensics.exiftool_analyze(Prompt.ask("File path")))
                elif choice == "2":
                    f = Prompt.ask("File path")
                    n = Prompt.ask("Min string length", default="8")
                    self._show_result(self.forensics.strings_analysis(f, int(n)))
                elif choice == "3":
                    f = Prompt.ask("Image path")
                    p = Prompt.ask("Passphrase", default="")
                    self._show_result(self.forensics.steghide_extract(f, p))
                elif choice == "4":
                    f = Prompt.ask("Image path")
                    p = Prompt.ask("Passphrase", default="")
                    self._show_result(self.forensics.outguess_extract(f, p))
                elif choice == "5":
                    self._show_result(self.forensics.zsteg_analyze(Prompt.ask("Image path")))
                elif choice == "6":
                    self._show_result(self.forensics.binwalk_scan(Prompt.ask("Image path")))
                elif choice == "7":
                    f = Prompt.ask("Image path")
                    o = Prompt.ask("Output dir", default="/tmp/bulk_zelzal")
                    self._show_result(self.forensics.bulk_extractor_scan(f, o))
                elif choice == "8":
                    f = Prompt.ask("Image path")
                    o = Prompt.ask("Output dir", default="/tmp/foremost_zelzal")
                    self._show_result(self.forensics.foremost_recover(f, o))
                elif choice == "9":
                    self._show_result(self.forensics.full_assessment(Prompt.ask("Image path", default="")))
                else: return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Forensics", actions, handler)

    def menu_cloud(self):
        actions = [
            ("1", "AWS Audit", "Check IAM, S3, Security Groups, MFA"),
            ("2", "Azure Audit", "Check subscriptions, RBAC roles"),
            ("3", "GCP Audit", "Check projects, IAM policies"),
            ("4", "Full Assessment", "Run all cloud security checks"),
        ]
        def handler(choice):
            if choice == "1":
                self._show_result(self.cloud.aws_audit())
            elif choice == "2":
                self._show_result(self.cloud.azure_audit())
            elif choice == "3":
                self._show_result(self.cloud.gcp_audit())
            elif choice == "4":
                self._show_result(self.cloud.full_assessment())
            else:
                return
            Prompt.ask("\nPress Enter to continue")
        self._show_module_menu("Cloud Security", actions, handler)

    # ─── Tools Menu ───
    def menu_tools(self):
        if HAS_RICH:
            console.print("\n[bold cyan]═══ TOOLS ═══[/]")
            table = Table(show_header=False, box=box.HEAVY, border_style="cyan")
            table.add_column("Option", style="bold cyan", width=5)
            table.add_column("Tool", style="white", width=25)
            table.add_column("Description", style="dim white")
            table.add_row("1", "Password Generator", "Generate strong passwords")
            table.add_row("2", "File Encrypt", "Encrypt a file (AES)")
            table.add_row("3", "File Decrypt", "Decrypt a file")
            table.add_row("4", "System Info", "Display system information")
            table.add_row("5", "Clear Logs", "Remove old log files")
            table.add_row("b", "Back to main menu", "")
            console.print(table)
        else:
            print("\n--- Tools ---")
            print("1. Password Generator")
            print("2. File Encrypt")
            print("3. File Decrypt")
            print("4. System Info")
            print("5. Clear Logs")
            print("b. Back")
        choice = Prompt.ask("\n[cyan]Select[/]" if HAS_RICH else "\nSelect: ")
        if choice == "b":
            return
        if choice == "1":
            length = int(Prompt.ask("Length", default="16"))
            no_sym = Confirm.ask("No symbols?", default=False)
            pwd = generate_password(length, no_sym)
            if HAS_RICH:
                console.print(f"\n[bold green]Generated Password:[/] [yellow]{pwd}[/]")
            else:
                print(f"\nGenerated Password: {pwd}")
        elif choice == "2":
            path = Prompt.ask("File path")
            pwd = Prompt.ask("Encryption password", password=True)
            result = encrypt_file(path, pwd)
            if HAS_RICH:
                console.print(f"\n[green]Encrypted: {result}[/]" if result else "\n[red]Failed[/]")
            else:
                print(f"\nEncrypted: {result}" if result else "\nFailed")
        elif choice == "3":
            path = Prompt.ask("File path (.encrypted)")
            pwd = Prompt.ask("Decryption password", password=True)
            result = decrypt_file(path, pwd)
            if HAS_RICH:
                console.print(f"\n[green]Decrypted: {result}[/]" if result else "\n[red]Failed[/]")
            else:
                print(f"\nDecrypted: {result}" if result else "\nFailed")
        elif choice == "4":
            self._show_result(self.system_info)
        elif choice == "5":
            days = int(Prompt.ask("Delete logs older than (days)", default="30"))
            removed = clear_old_logs(days)
            if HAS_RICH:
                console.print(f"\n[green]Removed {removed} log files[/]")
            else:
                print(f"\nRemoved {removed} log files")
        Prompt.ask("\nPress Enter to continue")

    # ─── Quick Scan ───
    def quick_scan(self):
        if HAS_RICH:
            console.print("[bold yellow]═══ QUICK SYSTEM SCAN ═══[/]")
        else:
            print("\n=== QUICK SYSTEM SCAN ===")
        results = {}
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                     BarColumn(), transient=True) as progress:
            tasks = [
                ("Network scan...", "network", lambda: self.network.network_scan(fast=True)),
                ("ARP check...", "arp", lambda: self.network.arp_spoofing_check()),
                ("System check...", "system", lambda: self.system.service_hardening()),
                ("Password audit...", "passwd", lambda: self.identity.password_audit()),
                ("2FA check...", "2fa", lambda: self.identity.twofa_status()),
                ("Firewall rules...", "firewall", lambda: self.firewall.get_current_rules()),
                ("Health check...", "health", lambda: self.performance.system_health()),
            ]
            for desc, key, func in tasks:
                task_id = progress.add_task(desc, total=1)
                try:
                    results[key] = func()
                except Exception as e:
                    results[key] = {"error": str(e)}
                progress.update(task_id, completed=1)
        if HAS_RICH:
            console.print("\n[bold green]✓ Quick scan complete![/]")
            table = Table(box=box.SIMPLE, border_style="green")
            table.add_column("Module", style="cyan")
            table.add_column("Status", style="white")
            for key in results:
                r = results[key]
                status = "✓" if "error" not in r else "✗"
                if r.get("status") == "error":
                    status = "✗"
                table.add_row(key, status)
            console.print(table)
        else:
            print("\nQuick scan complete!")
            for key in results:
                print(f"  {key}: {'OK' if 'error' not in results[key] else 'ERROR'}")
        save_path = save_report(results, "quick_scan")
        if HAS_RICH:
            console.print(f"\n[dim]Report saved: {save_path}[/]")
        else:
            print(f"\nReport saved: {save_path}")
        Prompt.ask("\nPress Enter to continue")

    # ─── Full Report ───
    def full_report(self):
        if HAS_RICH:
            console.print("[bold yellow]═══ GENERATING FULL SECURITY REPORT ═══[/]")
        else:
            print("\n=== GENERATING FULL SECURITY REPORT ===")
        results = {}
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                     BarColumn(), transient=True) as progress:
            modules = [
                ("Network Protection", "network", lambda: self.network.full_assessment()),
                ("Web Protection", "web", lambda: self.web.full_assessment()),
                ("Advanced Firewall", "firewall", lambda: self.firewall.full_assessment()),
                ("System Protection", "system", lambda: self.system.full_assessment()),
                ("Performance", "performance", lambda: self.performance.full_assessment()),
                ("Identity Protection", "identity", lambda: self.identity.full_assessment()),
                ("Container Security", "container", lambda: self.container.full_assessment()),
                ("Wireless Security", "wireless", lambda: self.wireless.full_assessment()),
                ("Exploit Detection", "exploit", lambda: self.exploit.full_assessment()),
                ("Reconnaissance", "recon", lambda: self.recon.full_assessment()),
                ("Web App Scanning", "webapp", lambda: self.webapp.full_assessment()),
                ("Exploitation", "exploitation", lambda: self.exploitation.full_assessment()),
                ("Forensics", "forensics", lambda: self.forensics.full_assessment()),
                ("Cloud Security", "cloud", lambda: self.cloud.full_assessment()),
            ]
            for desc, key, func in modules:
                task_id = progress.add_task(desc, total=1)
                try:
                    results[key] = func()
                except Exception as e:
                    results[key] = {"error": str(e)}
                progress.update(task_id, completed=1)
        save_path = save_report(results, "zelzal_full_report")
        if HAS_RICH:
            console.print(f"\n[bold green]✓ Full security report generated![/]")
            console.print(f"[dim]Saved: {save_path}[/]")
            # Summary table
            table = Table(title="Security Report Summary", box=box.HEAVY, border_style="green")
            table.add_column("Module", style="cyan")
            table.add_column("Status", style="white")
            table.add_column("Issues", style="yellow")
            for key, r in results.items():
                if "error" in r:
                    table.add_row(key, "✗", r["error"])
                else:
                    table.add_row(key, "✓", "See report for details")
            console.print(table)
        else:
            print(f"\nFull security report generated: {save_path}")
        Prompt.ask("\nPress Enter to continue")

    def exit_app(self):
        self.running = False
        if HAS_RICH:
            console.print("\n[bold red]ZELZAL session terminated. Stay secure.[/]")
        else:
            print("\nZELZAL session terminated. Stay secure.")

    def _show_result(self, data: dict):
        """Display result data as rich JSON or simple text"""
        if HAS_RICH:
            import json
            json_str = json.dumps(data, indent=2, default=str)
            console.print(Syntax(json_str, "json", theme="monokai", line_numbers=False))
        else:
            import json
            print(json.dumps(data, indent=2, default=str))


def main():
    """Entry point"""
    if not HAS_RICH:
        print("ZELZAL v5.0 - Kali Linux Cybersecurity Toolkit")
        print("=" * 50)
        print("Tip: Install 'rich' for a better TUI experience:")
        print("     pip3 install rich")
        print()

    signal.signal(signal.SIGINT, lambda sig, frame: sys.exit(0))

    # Check CLI args
    if len(sys.argv) > 1:
        app = ZelzalTUI()
        if "--scan" in sys.argv:
            app.quick_scan()
            return
        elif "--report" in sys.argv:
            app.full_report()
            return
        elif "--version" in sys.argv:
            print(f"ZELZAL v{VERSION}")
            return

    app = ZelzalTUI()
    app.run()


if __name__ == "__main__":
    main()
