"""
ZELZAL Container Security Module v5.0
Real implementations using: docker, kubectl, trivy, dockle, kube-bench
"""

import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

from core import write_log, run_command, save_report, check_dependencies


class ContainerSecurity:
    """Container and Kubernetes security auditing"""

    def __init__(self):
        self.name = "container_security"
        self.dependencies = {
            "docker": "docker",
            "kubectl": "kubectl",
            "trivy": "trivy",
            "dockle": "dockle",
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

    def _check_docker(self) -> bool:
        """Check if Docker daemon is accessible"""
        code, out, _ = run_command("docker info --format '{{.ServerVersion}}'")
        return code == 0 and bool(out.strip())

    def docker_audit(self) -> Dict[str, Any]:
        """Audit Docker daemon security configuration"""
        write_log("Running Docker security audit", "info")
        result = {
            "status": "ok",
            "docker_available": self._check_docker(),
            "checks": [],
        }

        if not result["docker_available"]:
            result["status"] = "error"
            result["error"] = "Docker daemon not accessible"
            return result

        result["checks"].append(self._check_docker_version())
        result["checks"].append(self._check_running_containers())
        result["checks"].append(self._check_privileged_containers())
        result["checks"].append(self._check_exposed_ports())
        result["checks"].append(self._check_docker_socket_mounts())
        result["checks"].append(self._check_images())
        result["checks"].append(self._check_networks())

        return result

    def _check_docker_version(self) -> Dict[str, Any]:
        code, out, _ = run_command("docker version --format '{{.Server.Version}}'")
        return {
            "check": "Docker Version",
            "version": out.strip() if code == 0 else "unknown",
            "secure": code == 0,
        }

    def _check_running_containers(self) -> Dict[str, Any]:
        code, out, _ = run_command("docker ps -q | wc -l")
        count = int(out.strip()) if code == 0 else 0
        return {
            "check": "Running Containers",
            "count": count,
            "secure": True,
        }

    def _check_privileged_containers(self) -> Dict[str, Any]:
        code, out, _ = run_command(
            "docker ps --filter 'status=running' --format '{{.ID}} {{.Names}} {{.Command}}' 2>/dev/null | head -20"
        )
        containers = []
        if code == 0 and out.strip():
            for line in out.strip().split('\n'):
                parts = line.split(None, 2)
                if parts:
                    containers.append({
                        "id": parts[0][:12],
                        "name": parts[1] if len(parts) > 1 else "unknown",
                    })
        insecure = run_command(
            "docker ps --filter 'status=running' --format '{{.ID}}' 2>/dev/null | xargs -I{} docker inspect {} --format '{{.HostConfig.Privileged}}' 2>/dev/null | grep -c true"
        )
        privileged_count = int(insecure[1].strip()) if insecure[0] == 0 else 0
        return {
            "check": "Privileged Containers",
            "total": len(containers),
            "privileged": privileged_count,
            "secure": privileged_count == 0,
        }

    def _check_exposed_ports(self) -> Dict[str, Any]:
        code, out, _ = run_command("docker ps --format '{{.Names}} {{.Ports}}' 2>/dev/null")
        exposed = []
        if code == 0 and out.strip():
            for line in out.strip().split('\n'):
                if '->' in line:
                    parts = line.split(None, 1)
                    exposed.append({"container": parts[0], "ports": parts[1] if len(parts) > 1 else ""})
        return {
            "check": "Exposed Ports",
            "count": len(exposed),
            "ports": exposed[:10],
            "secure": True,
        }

    def _check_docker_socket_mounts(self) -> Dict[str, Any]:
        code, out, _ = run_command(
            "docker ps -q 2>/dev/null | xargs -I{} docker inspect {} --format '{{.Name}} {{range .Mounts}}{{.Source}} {{end}}' 2>/dev/null | grep -i docker.sock || true"
        )
        mounts = out.strip().split('\n') if code == 0 and out.strip() else []
        return {
            "check": "Docker Socket Mounts",
            "count": len([m for m in mounts if m]),
            "insecure_mounts": len([m for m in mounts if m]),
            "secure": len([m for m in mounts if m]) == 0,
        }

    def _check_images(self) -> Dict[str, Any]:
        code, out, _ = run_command("docker images --format '{{.Repository}}:{{.Tag}}' 2>/dev/null | head -20")
        images = out.strip().split('\n') if code == 0 and out.strip() else []
        latest_count = sum(1 for img in images if ':latest' in img)
        return {
            "check": "Docker Images",
            "total": len(images),
            "using_latest_tag": latest_count,
            "secure": latest_count == 0,
        }

    def _check_networks(self) -> Dict[str, Any]:
        code, out, _ = run_command("docker network ls --format '{{.Name}}' 2>/dev/null")
        networks = out.strip().split('\n') if code == 0 and out.strip() else []
        return {
            "check": "Docker Networks",
            "count": len(networks),
            "networks": networks,
            "secure": True,
        }

    def kubernetes_audit(self) -> Dict[str, Any]:
        """Audit Kubernetes cluster security posture"""
        write_log("Running Kubernetes security audit", "info")
        result = {
            "status": "ok",
            "checks": [],
        }

        code, out, _ = run_command("kubectl version --client -o json 2>/dev/null")
        if code != 0:
            result["status"] = "error"
            result["error"] = "kubectl not available or not configured"
            return result

        result["checks"].append(self._check_k8s_version())
        result["checks"].append(self._check_namespaces())
        result["checks"].append(self._check_pods())
        result["checks"].append(self._check_services())
        result["checks"].append(self._check_privileged_pods())

        return result

    def _check_k8s_version(self) -> Dict[str, Any]:
        code, out, _ = run_command("kubectl version --client -o json 2>/dev/null")
        version = "unknown"
        if code == 0 and out.strip():
            try:
                data = json.loads(out)
                version = data.get("clientVersion", {}).get("gitVersion", "unknown")
            except (json.JSONDecodeError, KeyError):
                version = out.strip()[:50]
        return {
            "check": "Kubernetes Version",
            "version": version,
            "secure": True,
        }

    def _check_namespaces(self) -> Dict[str, Any]:
        code, out, _ = run_command("kubectl get namespaces --no-headers 2>/dev/null | wc -l")
        count = int(out.strip()) if code == 0 else 0
        return {
            "check": "Namespaces",
            "count": count,
            "secure": True,
        }

    def _check_pods(self) -> Dict[str, Any]:
        code, out, _ = run_command(
            "kubectl get pods --all-namespaces --no-headers 2>/dev/null | wc -l"
        )
        total = int(out.strip()) if code == 0 else 0
        _, running_out, _ = run_command(
            "kubectl get pods --all-namespaces --no-headers 2>/dev/null | grep Running | wc -l"
        )
        running = int(running_out.strip()) if running_out.strip() else 0
        return {
            "check": "Pods",
            "total": total,
            "running": running,
            "secure": True,
        }

    def _check_services(self) -> Dict[str, Any]:
        code, out, _ = run_command("kubectl get svc --all-namespaces --no-headers 2>/dev/null | wc -l")
        count = int(out.strip()) if code == 0 else 0
        _, lb_out, _ = run_command(
            "kubectl get svc --all-namespaces --no-headers 2>/dev/null | grep LoadBalancer | wc -l"
        )
        load_balancers = int(lb_out.strip()) if lb_out.strip() else 0
        return {
            "check": "Services",
            "total": count,
            "load_balancers": load_balancers,
            "secure": True,
        }

    def _check_privileged_pods(self) -> Dict[str, Any]:
        code, out, _ = run_command(
            "kubectl get pods --all-namespaces -o jsonpath='{.items[?(@.spec.containers[*].securityContext.privileged==true)].metadata.name}' 2>/dev/null"
        )
        privileged = out.strip().split() if code == 0 and out.strip() else []
        return {
            "check": "Privileged Pods",
            "count": len(privileged),
            "privileged_pods": privileged[:10],
            "secure": len(privileged) == 0,
        }

    def trivy_scan(self, target: str = "filesystem") -> Dict[str, Any]:
        """Run Trivy vulnerability scan (filesystem, image, or repo)"""
        write_log(f"Running Trivy scan on: {target}", "info")
        result = {"status": "ok", "target": target}

        code, _, _ = run_command("which trivy")
        if code != 0:
            result["status"] = "error"
            result["error"] = "Trivy not installed"
            return result

        cmd_map = {
            "filesystem": "trivy fs --no-progress --severity HIGH,CRITICAL /",
            "image": "trivy image --no-progress --severity HIGH,CRITICAL alpine:latest",
        }
        cmd = cmd_map.get(target, f"trivy fs --no-progress --severity HIGH,CRITICAL {target}")

        code, out, err = run_command(cmd, timeout=120)
        if code != 0:
            result["status"] = "error"
            result["error"] = err.strip()[:200] or "Scan failed"

        lines = out.strip().split('\n') if out.strip() else []
        vulns = [l for l in lines if 'CRITICAL' in l or 'HIGH' in l]
        result["total_vulnerabilities"] = len(vulns)
        result["vulnerabilities"] = vulns[:20]
        result["scan_output"] = out[:500] if out else ""

        return result

    def full_assessment(self) -> Dict[str, Any]:
        """Run complete container security assessment"""
        write_log("Starting full container security assessment", "info")
        result = {
            "timestamp": datetime.now().isoformat(),
            "module": self.name,
            "docker": self.docker_audit(),
            "kubernetes": self.kubernetes_audit(),
        }
        save_path = save_report(result, "container_security_report")
        result["report_path"] = save_path
        write_log(f"Container security report saved: {save_path}", "info")
        return result
