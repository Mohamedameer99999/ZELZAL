"""
ZELZAL Forensics & Steganography Module v5.0
Real tools: volatility, binwalk, foremost, steghide, exiftool, bulk_extractor,
strings, outguess, snow, stegsolve, zsteg
"""
import os
import json
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

from core import write_log, run_command, save_report, check_dependencies, is_root

MODULE_NAME = "forensics"

class Forensics:
    def __init__(self):
        self.name = MODULE_NAME
        self.deps = ["volatility", "binwalk", "foremost", "steghide",
                      "exiftool", "bulk_extractor", "outguess", "stegsolve", "zsteg"]

    def check_status(self) -> Dict[str, Any]:
        available = [d for d in self.deps if check_dependencies([d]).get(d, False)]
        return {
            "module": self.name,
            "status": "available" if len(available) > len(self.deps) // 2 else "limited",
            "tools_found": available,
            "tools_missing": [d for d in self.deps if d not in available],
            "timestamp": datetime.now().isoformat(),
        }

    def volatility_check(self, image_path: str = "") -> Dict[str, Any]:
        result = {"module": "volatility", "image": image_path or "none", "profiles": []}
        if image_path and os.path.exists(image_path):
            code, out, err = run_command(
                ["volatility", "-f", image_path, "imageinfo"], timeout=60
            )
            if code == 0:
                for line in out.split("\n"):
                    if "Profile" in line or "Suggested" in line:
                        result["profiles"].append(line.strip())
            else:
                result["error"] = err or "volatility analysis failed"
        else:
            code, out, err = run_command(["volatility", "--info"], timeout=30)
            if code == 0:
                for line in out.split("\n"):
                    if "Profiles" in line or "Profile" in line:
                        result["profiles"].append(line.strip())
                result["note"] = "No image provided; showing available profiles"
            else:
                result["error"] = err or "volatility not available"
        return result

    def binwalk_scan(self, image_path: str = "") -> Dict[str, Any]:
        result = {"module": "binwalk", "image": image_path or "none", "findings": []}
        if not image_path or not os.path.exists(image_path):
            result["error"] = "No image file provided"
            return result
        code, out, err = run_command(
            ["binwalk", "-Meq", "--directory=/tmp/binwalk_zelzal", image_path],
            timeout=120
        )
        if code == 0:
            for line in out.split("\n"):
                if "DECIMAL" in line or "ELF" in line or "filesystem" in line.lower() or "archive" in line.lower():
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "binwalk not available"
        return result

    def foremost_recover(self, image_path: str = "", output_dir: str = "/tmp/foremost_zelzal") -> Dict[str, Any]:
        result = {"module": "foremost", "image": image_path or "none", "recovered_files": 0}
        if not image_path or not os.path.exists(image_path):
            result["error"] = "No image file provided"
            return result
        os.makedirs(output_dir, exist_ok=True)
        code, out, err = run_command(
            ["foremost", "-t", "all", "-i", image_path, "-o", output_dir, "-q"],
            timeout=120
        )
        if code == 0:
            for line in out.split("\n"):
                if "files" in line.lower() and "saved" in line.lower():
                    parts = line.split()
                    for p in parts:
                        if p.isdigit():
                            result["recovered_files"] = int(p)
                            break
        else:
            result["error"] = err or "foremost not available"
        return result

    def steghide_extract(self, image_path: str = "", passphrase: str = "") -> Dict[str, Any]:
        result = {"module": "steghide", "image": image_path or "none", "extracted": False}
        if not image_path or not os.path.exists(image_path):
            result["error"] = "No image file provided"
            return result
        code, out, err = run_command(
            ["steghide", "extract", "-sf", image_path, "-p", passphrase or "",
             "-f", "-q"], timeout=30
        )
        if code == 0:
            result["extracted"] = True
            result["output"] = out.strip() if out else "data extracted"
        else:
            result["error"] = err or "steghide: no hidden data or wrong passphrase"
        return result

    def exiftool_analyze(self, file_path: str = "") -> Dict[str, Any]:
        result = {"module": "exiftool", "file": file_path or "none", "metadata": {}}
        if not file_path or not os.path.exists(file_path):
            result["error"] = "No file provided"
            return result
        code, out, err = run_command(
            ["exiftool", "-json", file_path], timeout=15
        )
        if code == 0:
            try:
                parsed = json.loads(out)
                if parsed:
                    result["metadata"] = parsed[0]
            except json.JSONDecodeError:
                for line in out.split("\n"):
                    if ":" in line:
                        k, v = line.split(":", 1)
                        result["metadata"][k.strip()] = v.strip()
        else:
            result["error"] = err or "exiftool not available"
        return result

    def bulk_extractor_scan(self, image_path: str = "", output_dir: str = "/tmp/bulk_zelzal") -> Dict[str, Any]:
        result = {"module": "bulk_extractor", "image": image_path or "none", "findings": {}}
        if not image_path or not os.path.exists(image_path):
            result["error"] = "No image file provided"
            return result
        os.makedirs(output_dir, exist_ok=True)
        code, out, err = run_command(
            ["bulk_extractor", "-o", output_dir, image_path], timeout=120
        )
        if code == 0:
            for fname in os.listdir(output_dir):
                fpath = os.path.join(output_dir, fname)
                if os.path.isfile(fpath) and fname.endswith(".txt"):
                    with open(fpath) as f:
                        lines = f.readlines()[:10]
                    result["findings"][fname] = [l.strip() for l in lines if l.strip()]
        else:
            result["error"] = err or "bulk_extractor not available"
        return result

    def strings_analysis(self, file_path: str = "", min_len: int = 8) -> Dict[str, Any]:
        result = {"module": "strings", "file": file_path or "none", "strings_found": 0, "samples": []}
        if not file_path or not os.path.exists(file_path):
            result["error"] = "No file provided"
            return result
        code, out, err = run_command(
            ["strings", "-n", str(min_len), file_path], timeout=30
        )
        if code == 0:
            lines = [l.strip() for l in out.split("\n") if l.strip()]
            result["strings_found"] = len(lines)
            result["samples"] = lines[:20]
        else:
            result["error"] = err or "strings not available"
        return result

    def outguess_extract(self, image_path: str = "", passphrase: str = "") -> Dict[str, Any]:
        result = {"module": "outguess", "image": image_path or "none", "extracted": False}
        if not image_path or not os.path.exists(image_path):
            result["error"] = "No image file provided"
            return result
        outfile = "/tmp/outguess_zelzal_output.txt"
        code, out, err = run_command(
            ["outguess", "-r", image_path, outfile, "-p", passphrase or ""],
            timeout=30
        )
        if code == 0 and os.path.exists(outfile):
            with open(outfile) as f:
                content = f.read().strip()
            result["extracted"] = bool(content)
            result["data"] = content[:500] if content else ""
        else:
            result["error"] = err or "outguess: no hidden data or not available"
        return result

    def snow_extract(self, text_file: str = "", passphrase: str = "") -> Dict[str, Any]:
        result = {"module": "snow", "file": text_file or "none", "extracted": False}
        if not text_file or not os.path.exists(text_file):
            result["error"] = "No text file provided"
            return result
        code, out, err = run_command(
            ["snow", "-C", "-p", passphrase or "", text_file], timeout=15
        )
        if code == 0 and out.strip():
            result["extracted"] = True
            result["data"] = out.strip()[:500]
        else:
            result["error"] = err or "snow: no hidden data or not available"
        return result

    def stegsolve_check(self) -> Dict[str, Any]:
        result = {"module": "stegsolve", "available": False}
        code, out, err = run_command(["stegsolve"], timeout=5)
        if code == 0 or code is None:
            result["available"] = True
        else:
            stegsolve_jar = "/usr/share/stegsolve/stegsolve.jar"
            if os.path.exists(stegsolve_jar):
                result["available"] = True
                result["path"] = stegsolve_jar
            else:
                result["error"] = "stegsolve not available (GUI tool)"
        return result

    def zsteg_analyze(self, image_path: str = "") -> Dict[str, Any]:
        result = {"module": "zsteg", "image": image_path or "none", "findings": []}
        if not image_path or not os.path.exists(image_path):
            result["error"] = "No image file provided"
            return result
        code, out, err = run_command(
            ["zsteg", "-a", image_path], timeout=30
        )
        if code == 0:
            for line in out.split("\n"):
                if line.strip() and "bmp" not in line and ":" in line:
                    result["findings"].append(line.strip())
        else:
            result["error"] = err or "zsteg not available"
        return result

    def full_assessment(self, image_path: str = "") -> Dict[str, Any]:
        timestamp = datetime.now().isoformat()
        report = {
            "module": self.name,
            "timestamp": timestamp,
            "volatility": self.volatility_check(image_path),
            "exiftool": self.exiftool_analyze(image_path),
            "strings": self.strings_analysis(image_path),
            "binwalk": self.binwalk_scan(image_path) if image_path else {"error": "No image"},
            "foremost": self.foremost_recover(image_path) if image_path else {"error": "No image"},
            "steghide": self.steghide_extract(image_path) if image_path else {"error": "No image"},
            "outguess": self.outguess_extract(image_path) if image_path else {"error": "No image"},
            "zsteg": self.zsteg_analyze(image_path) if image_path else {"error": "No image"},
            "bulk_extractor": self.bulk_extractor_scan(image_path) if image_path else {"error": "No image"},
            "stegsolve": self.stegsolve_check(),
        }
        save_report(report, self.name)
        return report
