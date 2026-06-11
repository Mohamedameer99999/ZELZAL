"""
ZELZAL Cloud Security Module v5.0
Real tools: awscli, az, gcloud, prowler, scoutsuite, cloudsploit, s3scanner
"""

import json
from datetime import datetime
from typing import Dict, Any

from core import write_log, run_command, save_report, check_dependencies


class CloudSecurity:
    """Multi-cloud security posture assessment (AWS, Azure, GCP)"""

    def __init__(self):
        self.name = "cloud_security"
        self.dependencies = {
            "aws": "aws",
            "azure": "az",
            "gcloud": "gcloud",
            "prowler": "prowler",
            "scoutsuite": "scout",
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

    def _check_aws_cli(self) -> bool:
        code, _, _ = run_command("aws --version")
        return code == 0

    def _check_azure_cli(self) -> bool:
        code, _, _ = run_command("az --version")
        return code == 0

    def _check_gcloud_cli(self) -> bool:
        code, _, _ = run_command("gcloud --version")
        return code == 0

    def aws_audit(self) -> Dict[str, Any]:
        write_log("Running AWS security audit", "info")
        result = {"status": "ok", "checks": [], "iam_users": 0, "s3_buckets": [], "security_groups": []}

        if not self._check_aws_cli():
            result["status"] = "error"
            result["error"] = "AWS CLI not installed or not configured"
            return result

        code, out, _ = run_command("aws sts get-caller-identity --output json 2>/dev/null")
        if code != 0:
            result["status"] = "error"
            result["error"] = "AWS credentials not configured"
            return result

        try:
            identity = json.loads(out) if out.strip() else {}
            result["account"] = identity.get("Account", "unknown")
            result["arn"] = identity.get("Arn", "unknown")
        except json.JSONDecodeError:
            result["account"] = "unknown"

        code, out, _ = run_command("aws iam list-users --output json 2>/dev/null")
        if code == 0 and out.strip():
            try:
                users = json.loads(out).get("Users", [])
                result["iam_users"] = len(users)
                result["checks"].append({"check": "IAM Users", "count": len(users), "secure": True})
            except json.JSONDecodeError:
                pass

        code, out, _ = run_command("aws s3api list-buckets --output json 2>/dev/null")
        if code == 0 and out.strip():
            try:
                buckets = json.loads(out).get("Buckets", [])
                for b in buckets:
                    name = b["Name"]
                    code2, acl_out, _ = run_command(f"aws s3api get-bucket-acl --bucket {name} --output json 2>/dev/null")
                    public = False
                    if code2 == 0 and acl_out.strip():
                        try:
                            grants = json.loads(acl_out).get("Grants", [])
                            for g in grants:
                                uri = g.get("Grantee", {}).get("URI", "")
                                if "AllUsers" in uri or "AuthenticatedUsers" in uri:
                                    public = True
                                    break
                        except json.JSONDecodeError:
                            pass
                    result["s3_buckets"].append({"name": name, "public": public})
                result["checks"].append({
                    "check": "S3 Buckets",
                    "count": len(buckets),
                    "public_buckets": sum(1 for b in result["s3_buckets"] if b["public"]),
                    "secure": not any(b["public"] for b in result["s3_buckets"]),
                })
            except json.JSONDecodeError:
                pass

        code, out, _ = run_command("aws ec2 describe-security-groups --output json 2>/dev/null")
        if code == 0 and out.strip():
            try:
                sgs = json.loads(out).get("SecurityGroups", [])
                open_sgs = 0
                for sg in sgs:
                    for perm in sg.get("IpPermissions", []):
                        for ip_range in perm.get("IpRanges", []):
                            if ip_range.get("CidrIp") == "0.0.0.0/0":
                                open_sgs += 1
                                break
                result["security_groups"] = sgs[:5]
                result["checks"].append({
                    "check": "Security Groups",
                    "total": len(sgs),
                    "open_to_world": open_sgs,
                    "secure": open_sgs == 0,
                })
            except json.JSONDecodeError:
                pass

        code, out, _ = run_command("aws iam list-users --output json 2>/dev/null")
        if code == 0 and out.strip():
            try:
                users = json.loads(out).get("Users", [])
                no_mfa = 0
                for u in users:
                    uname = u["UserName"]
                    code3, mfa_out, _ = run_command(f"aws iam list-mfa-devices --user-name {uname} --output json 2>/dev/null")
                    if code3 == 0 and mfa_out.strip():
                        mfa_devices = json.loads(mfa_out).get("MFADevices", [])
                        if not mfa_devices:
                            no_mfa += 1
                    else:
                        no_mfa += 1
                result["checks"].append({
                    "check": "MFA Status",
                    "users_without_mfa": no_mfa,
                    "secure": no_mfa == 0,
                })
            except json.JSONDecodeError:
                pass

        return result

    def azure_audit(self) -> Dict[str, Any]:
        write_log("Running Azure security audit", "info")
        result = {"status": "ok", "checks": [], "subscriptions": 0}

        if not self._check_azure_cli():
            result["status"] = "error"
            result["error"] = "Azure CLI not installed or not configured"
            return result

        code, out, _ = run_command("az account show --output json 2>/dev/null")
        if code != 0:
            result["status"] = "error"
            result["error"] = "Azure not logged in"
            return result

        try:
            account = json.loads(out) if out.strip() else {}
            result["subscription"] = account.get("name", "unknown")
            result["subscription_id"] = account.get("id", "unknown")
        except json.JSONDecodeError:
            pass

        code, out, _ = run_command("az account list --output json 2>/dev/null")
        if code == 0 and out.strip():
            try:
                subs = json.loads(out)
                result["subscriptions"] = len(subs)
                result["checks"].append({"check": "Subscriptions", "count": len(subs), "secure": True})
            except json.JSONDecodeError:
                pass

        code, out, _ = run_command("az role assignment list --output json 2>/dev/null")
        if code == 0 and out.strip():
            try:
                roles = json.loads(out)
                admin_roles = sum(1 for r in roles if "Owner" in str(r.get("roleDefinitionName", "")))
                result["checks"].append({
                    "check": "RBAC Roles",
                    "total_assignments": len(roles),
                    "owner_assignments": admin_roles,
                    "secure": admin_roles <= 1,
                })
            except json.JSONDecodeError:
                pass

        return result

    def gcp_audit(self) -> Dict[str, Any]:
        write_log("Running GCP security audit", "info")
        result = {"status": "ok", "checks": [], "projects": 0}

        if not self._check_gcloud_cli():
            result["status"] = "error"
            result["error"] = "GCloud CLI not installed or not configured"
            return result

        code, out, _ = run_command("gcloud projects list --format json 2>/dev/null")
        if code != 0:
            result["status"] = "error"
            result["error"] = "GCP not authenticated"
            return result

        if out.strip():
            try:
                projects = json.loads(out)
                result["projects"] = len(projects)
                result["checks"].append({"check": "GCP Projects", "count": len(projects), "secure": True})
                if projects:
                    proj_id = projects[0].get("projectId", "")
                    code2, iam_out, _ = run_command(f"gcloud projects get-iam-policy {proj_id} --format json 2>/dev/null")
                    if code2 == 0 and iam_out.strip():
                        try:
                            policy = json.loads(iam_out)
                            bindings = policy.get("bindings", [])
                            all_users = sum(1 for b in bindings if "allUsers" in str(b.get("members", [])) or "allAuthenticatedUsers" in str(b.get("members", [])))
                            result["checks"].append({
                                "check": "IAM Public Access",
                                "public_bindings": all_users,
                                "secure": all_users == 0,
                            })
                        except json.JSONDecodeError:
                            pass
            except json.JSONDecodeError:
                pass

        return result

    def prowler_scan(self) -> Dict[str, Any]:
        code, _, _ = run_command("which prowler 2>/dev/null")
        if code != 0:
            return {"module": "prowler", "available": False, "error": "prowler not installed"}
        code, out, err = run_command("prowler --version 2>/dev/null", timeout=30)
        version = out.strip() or err.strip() if code == 0 else "unknown"
        result = {"module": "prowler", "available": True, "version": version}
        code, out, err = run_command("prowler aws --quick-inventory --output-modes json 2>/dev/null", timeout=120)
        if code == 0 and out.strip():
            try:
                data = json.loads(out)
                result["findings"] = data[:10] if isinstance(data, list) else [data]
                result["total_findings"] = len(data) if isinstance(data, list) else 1
            except json.JSONDecodeError:
                result["output"] = out[:500]
        return result

    def scoutsuite_scan(self) -> Dict[str, Any]:
        code, _, _ = run_command("which scout 2>/dev/null")
        if code != 0:
            return {"module": "scoutsuite", "available": False, "error": "ScoutSuite not installed"}
        result = {"module": "scoutsuite", "available": True}
        code, out, err = run_command("scout --help 2>&1 | head -5", timeout=15)
        result["description"] = out.strip()[:200] if out.strip() else err.strip()[:200]
        return result

    def cloud_posture_assessment(self) -> Dict[str, Any]:
        write_log("Running full cloud posture assessment", "info")
        result = {"timestamp": datetime.now().isoformat(), "module": self.name}
        result["aws"] = self.aws_audit()
        result["azure"] = self.azure_audit()
        result["gcp"] = self.gcp_audit()
        result["prowler"] = self.prowler_scan()
        result["scoutsuite"] = self.scoutsuite_scan()
        save_path = save_report(result, "cloud_security_report")
        result["report_path"] = save_path
        write_log(f"Cloud security report saved: {save_path}", "info")
        return result

    def full_assessment(self) -> Dict[str, Any]:
        return self.cloud_posture_assessment()
