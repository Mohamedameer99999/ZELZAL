# ZELZAL v5.0 — Kali Linux Cybersecurity Toolkit

Advanced terminal-based security assessment and hardening toolkit for Kali Linux.
6 real modules, 65+ security features, Rich-powered TUI.

## Quick Start

```bash
chmod +x install.sh
sudo ./install.sh
zelzal
```

Or run directly:

```bash
pip3 install rich
python3 zelzal.py
```

## Modules

| Module | Features | Dependencies |
|--------|----------|-------------|
| **Network Protection** | ARP spoofing detection, nmap scan, WiFi scanner, speed test, iptables blocking, DHCP snooping, bandwidth analysis, IPv6 audit, Bluetooth scan, fake AP detection, SMB scan, mDNS discovery | `nmap`, `arp-scan`, `iwconfig`, `speedtest-cli`, `conntrack`, `tshark`, `smbclient` |
| **Web Protection** | Secure DNS, phishing URL check, privacy cleaner, data leak scan, cookie analysis, email breach check, DNS leak test, WebRTC leak test, HTTPS enforcement, ClamAV download scanner, adblocker check | `dig`, `openssl`, `clamav`, `curl` |
| **Advanced Firewall** | iptables rule management, custom rules, per-app firewall, traffic shaping, intrusion prevention, connection history, GeoIP blocking, port knocking | `iptables`, `tc`, `conntrack`, `ipset`, `iprange` |
| **System Protection** | UFW firewall, ClamAV malware scan, Lynis vulnerability scan, USB device monitor, ransomware protection, log analysis, keylogger detection, config backup, kernel module audit, cron audit, service hardening | `ufw`, `clamav`, `lynis`, `auditd`, `rkhunter` |
| **Performance** | Disk cleanup, config analysis, memory optimization, startup analysis, temp file management, system health check | `systemd-analyze`, `journalctl` |
| **Identity Protection** | Password audit (shadow), strength evaluation, credential guard, 2FA/MFA check, breach monitor, biometric auth check | `zxcvbn`, `openssl`, `keyring` |

## Usage

```
Interactive menu:    python3 zelzal.py
Quick scan:          python3 zelzal.py --scan
Full report:         python3 zelzal.py --report
Version:             python3 zelzal.py --version
```

## Requirements

- **OS:** Kali Linux (or any Debian-based Linux)
- **Python:** 3.8+
- **Python packages:** `rich`, `cryptography`, `requests`, `psutil`
- **Root:** Required for firewall, system, and identity modules

## Report Format

All reports are saved as JSON in `reports/`:

```json
{
  "timestamp": "2026-06-08T12:00:00",
  "module": "network",
  "results": { ... }
}
```

## Architecture

```
kali_tools/
├── zelzal.py              # Main TUI launcher
├── core.py                # Core engine (run_command, save_report, deps check)
├── install.sh             # Kali Linux installer
├── requirements.txt       # Python dependencies
├── modules/
│   ├── __init__.py        # Module exports
│   ├── network_protection.py
│   ├── web_protection.py
│   ├── firewall_advanced.py
│   ├── system_protection.py
│   ├── performance_protection.py
│   └── identity_protection.py
└── reports/               # Generated reports (JSON)
```

## Notes

- The **ZELZAL web platform** (Flask + React) is in the parent directory
- This CLI toolkit is standalone and does not require the web platform
- Full functionality requires Kali Linux; partial functionality on other distros
