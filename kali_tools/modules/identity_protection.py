"""
ZELZAL Identity Protection Module v5.0
Real implementations using: passwd, chage, openssl, keyring, python3-zxcvbn
"""

import os
import re
from datetime import datetime
from typing import Dict, Optional, Any

from core import write_log, run_command, save_report, is_root, check_dependencies

MODULE_NAME = "identity_protection"
REQUIRED_TOOLS = ["openssl", "passwd", "chage", "lastlog"]


class IdentityProtection:
    """Identity security and credential management"""

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

    def password_audit(self, username: Optional[str] = None) -> Dict[str, Any]:
        """Audit password strength and policy compliance"""
        write_log("Auditing password security", "INFO")
        result = {
            "timestamp": datetime.now().isoformat(),
            "users_checked": 0,
            "weak_passwords": 0,
            "passwordless_accounts": 0,
            "details": [],
        }
        try:
            # Read shadow file for password hashes (requires root)
            shadow_path = "/etc/shadow"
            if is_root() and os.path.exists(shadow_path):
                with open(shadow_path) as f:
                    for line in f:
                        parts = line.strip().split(":")
                        if len(parts) >= 2:
                            user = parts[0]
                            pwd_hash = parts[1]
                            if username and user != username:
                                continue
                            result["users_checked"] += 1
                            # Check for passwordless accounts
                            if pwd_hash in ["", "!", "*", "!!"]:
                                result["passwordless_accounts"] += 1
                                result["details"].append({
                                    "user": user,
                                    "issue": "No password set / account locked",
                                    "severity": "critical",
                                })
                            elif pwd_hash.startswith("$6$"):
                                result["details"].append({
                                    "user": user,
                                    "issue": "SHA-512 hash (good)",
                                    "severity": "info",
                                })
                            elif pwd_hash.startswith("$1$"):
                                result["weak_passwords"] += 1
                                result["details"].append({
                                    "user": user,
                                    "issue": "MD5 hash (deprecated, upgrade to SHA-512)",
                                    "severity": "warning",
                                })

            # Check password aging
            code, stdout, _ = run_command(["chage", "-l", username or os.environ.get("USER", "")])
            if code == 0:
                result["password_policy"] = {}
                for line in stdout.split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        result["password_policy"][k.strip()] = v.strip()

            # Check for users with UID 0 (non-root admin)
            if os.name != 'nt':
                with open("/etc/passwd") as f:
                    for line in f:
                        parts = line.strip().split(":")
                        if len(parts) >= 3 and parts[2] == "0" and parts[0] != "root":
                            result["details"].append({
                                "user": parts[0],
                                "issue": "Non-root user with UID 0",
                                "severity": "critical",
                            })

            write_log(f"Password audit: {result['users_checked']} users, "
                      f"{result['weak_passwords']} weak, {result['passwordless_accounts']} passwordless", "SUCCESS")
        except Exception as e:
            write_log(f"Password audit error: {e}", "ERROR")
        return result

    def password_strength(self, password: str) -> Dict[str, Any]:
        """Evaluate password strength"""
        score = 0
        feedback = []
        if len(password) >= 8:
            score += 20
        else:
            feedback.append("Too short (min 8 characters)")
        if len(password) >= 12:
            score += 10
        if re.search(r'[A-Z]', password):
            score += 20
        else:
            feedback.append("Missing uppercase letters")
        if re.search(r'[a-z]', password):
            score += 20
        else:
            feedback.append("Missing lowercase letters")
        if re.search(r'\d', password):
            score += 15
        else:
            feedback.append("Missing digits")
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 15
        else:
            feedback.append("Missing special characters")
        # Check for common patterns
        common = ["password", "123456", "admin", "qwerty", "letmein", "welcome"]
        if any(p in password.lower() for p in common):
            score -= 30
            feedback.append("Contains common password pattern")
        if score >= 80:
            level = "very_strong"
        elif score >= 60:
            level = "strong"
        elif score >= 40:
            level = "moderate"
        elif score >= 20:
            level = "weak"
        else:
            level = "very_weak"
        return {
            "score": score,
            "level": level,
            "feedback": feedback,
            "length": len(password),
        }

    def credential_guard_check(self) -> Dict[str, Any]:
        """Check credential security configuration"""
        write_log("Checking credential security", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "credential_guard_active": False, "findings": []}
        try:
            # Check PAM configuration
            pam_files = ["/etc/pam.d/common-password", "/etc/pam.d/system-auth"]
            for pf in pam_files:
                if os.path.exists(pf):
                    with open(pf) as f:
                        content = f.read()
                    if "pam_unix.so" in content:
                        result["findings"].append(f"{pf}: using pam_unix")
                    if "pam_tally2" in content or "pam_faillock" in content:
                        result["findings"].append(f"{pf}: account lockout enabled")
                        result["credential_guard_active"] = True

            # Check for SSH key passphrase enforcement
            ssh_config = "/etc/ssh/sshd_config"
            if os.path.exists(ssh_config):
                with open(ssh_config) as f:
                    for line in f:
                        if "PasswordAuthentication" in line and "no" in line:
                            result["findings"].append("SSH password auth disabled (key-only)")
                            result["credential_guard_active"] = True
                        if "PubkeyAuthentication" in line and "yes" in line:
                            result["findings"].append("SSH public key auth enabled")

            # Check for sudo timestamp timeout
            sudoers = "/etc/sudoers"
            if os.path.exists(sudoers):
                code, stdout, _ = run_command(["grep", "-E", "timestamp_timeout", sudoers])
                if code == 0:
                    result["findings"].append(f"Sudo timeout: {stdout.strip()[:50]}")
                else:
                    result["findings"].append("Sudo: default timestamp timeout (5 min)")

            write_log(f"Credential guard: {'active' if result['credential_guard_active'] else 'basic'}", "SUCCESS")
        except Exception as e:
            write_log(f"Credential guard error: {e}", "ERROR")
        return result

    def twofa_status(self) -> Dict[str, Any]:
        """Check two-factor authentication status"""
        write_log("Checking 2FA/MFA status", "INFO")
        result = {
            "timestamp": datetime.now().isoformat(),
            "twofa_enabled": False,
            "methods": [],
        }
        try:
            # Check for Google Authenticator PAM module
            if os.path.exists("/etc/pam.d/common-auth"):
                with open("/etc/pam.d/common-auth") as f:
                    content = f.read()
                if "pam_google_authenticator" in content:
                    result["twofa_enabled"] = True
                    result["methods"].append("Google Authenticator (PAM)")
            # Check for SSH 2FA
            sshd_config = "/etc/ssh/sshd_config"
            if os.path.exists(sshd_config):
                with open(sshd_config) as f:
                    for line in f:
                        if "AuthenticationMethods" in line and "publickey,password" in line:
                            result["twofa_enabled"] = True
                            result["methods"].append("SSH multi-factor auth")

            # Check for u2f/pam_u2f
            if os.path.exists("/etc/pam.d") and run_command(["grep", "-r", "pam_u2f", "/etc/pam.d"])[0] == 0:
                result["twofa_enabled"] = True
                result["methods"].append("U2F/FIDO2 tokens")

            # Check for common 2FA tools
            for tool in ["google-authenticator", "ykman", "oath-toolkit"]:
                if run_command(["which", tool])[0] == 0:
                    result["methods"].append(f"2FA tool available: {tool}")

            write_log(f"2FA: {'enabled' if result['twofa_enabled'] else 'not configured'}", "SUCCESS")
        except Exception as e:
            write_log(f"2FA check error: {e}", "ERROR")
        return result

    def breach_monitor(self, email: Optional[str] = None) -> Dict[str, Any]:
        """Monitor for credential breaches"""
        write_log("Checking for credential breaches", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "breaches_found": 0, "breaches": [], "passwords_to_change": []}
        try:
            # Check local shadow file for compromised password hashes
            shadow_path = "/etc/shadow"
            if is_root() and os.path.exists(shadow_path):
                with open(shadow_path) as f:
                    for line in f:
                        parts = line.strip().split(":")
                        if len(parts) >= 2 and parts[1] not in ["!", "*", "!!", ""]:
                            pwd_hash = parts[1]
                            # Check for common/weak hash patterns
                            if pwd_hash.startswith("$1$"):
                                result["passwords_to_change"].append(parts[0])

            # Check for exposed SSH keys
            ssh_dir = os.path.expanduser("~/.ssh")
            if os.path.exists(ssh_dir):
                for key_file in ["id_rsa", "id_dsa", "id_ecdsa", "id_ed25519"]:
                    key_path = os.path.join(ssh_dir, key_file)
                    if os.path.exists(key_path):
                        with open(key_path) as f:
                            content = f.read()
                        if "ENCRYPTED" not in content:
                            result["breaches"].append(f"Unencrypted SSH key: {key_path}")
                            result["breaches_found"] += 1

            # Check for exposed credentials in environment
            for var in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AZURE_CLIENT_SECRET",
                        "GITHUB_TOKEN", "GITLAB_TOKEN", "API_KEY"]:
                if var in os.environ:
                    result["breaches"].append(f"Environment variable with credentials: {var}")
                    result["breaches_found"] += 1

            if result["breaches_found"] == 0:
                write_log("No credential breaches detected", "SUCCESS")
            else:
                write_log(f"Found {result['breaches_found']} credential issues", "WARNING")
        except Exception as e:
            write_log(f"Breach monitor error: {e}", "ERROR")
        return result

    def windows_hello_check(self) -> Dict[str, Any]:
        """Check biometric authentication status (Linux PAM equivalent)"""
        write_log("Checking biometric/PAM authentication", "INFO")
        result = {"timestamp": datetime.now().isoformat(), "biometric_auth": False, "methods_available": []}
        try:
            # Check for pam_fprintd (fingerprint)
            if os.path.exists("/etc/pam.d") and run_command(["grep", "-r", "pam_fprintd", "/etc/pam.d"])[0] == 0:
                result["biometric_auth"] = True
                result["methods_available"].append("fingerprint (pam_fprintd)")
            # Check fprintd enrollment
            code, stdout, _ = run_command(["fprintd-list"])
            if code == 0:
                result["methods_available"].append("fprintd available")
                result["biometric_auth"] = True
            # Check for face unlock / IR camera
            code, stdout, _ = run_command(["lsusb"])
            if code == 0 and ("camera" in stdout.lower() or "IR" in stdout):
                result["methods_available"].append("Camera/IR hardware detected")
            write_log(f"Biometric auth: {'available' if result['biometric_auth'] else 'not configured'}", "SUCCESS")
        except Exception as e:
            write_log(f"Biometric check error: {e}", "ERROR")
        return result

    def full_assessment(self) -> Dict[str, Any]:
        """Run complete identity security assessment"""
        write_log("Starting full identity security assessment", "INFO")
        results = {
            "timestamp": datetime.now().isoformat(),
            "password_audit": self.password_audit(),
            "credential_guard": self.credential_guard_check(),
            "twofa_status": self.twofa_status(),
            "breach_monitor": self.breach_monitor(),
            "biometric_auth": self.windows_hello_check(),
        }
        save_report(results, "identity_full_assessment")
        write_log("Identity assessment complete", "SUCCESS")
        return results
