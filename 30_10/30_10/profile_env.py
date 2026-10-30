
import argparse
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

import psutil

from salt import get_student_params


def run_command(command):
    """Execute a system command and return its output."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_windows_cpu():
    """Get CPU information using Windows PowerShell."""
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-CimInstance Win32_Processor | "
        "Select-Object -First 1 Name, NumberOfCores, "
        "NumberOfLogicalProcessors, MaxClockSpeed | "
        "ConvertTo-Json -Compress"
    ]

    output = run_command(command)

    if not output:
        return {}

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        return {}


def get_windows_cache():
    """Get CPU cache information using Windows CIM."""
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-CimInstance Win32_CacheMemory | "
        "Select-Object Level, InstalledSize, MaxCacheSize | "
        "ConvertTo-Json -Compress"
    ]

    output = run_command(command)

    if not output:
        return []

    try:
        result = json.loads(output)
        return result if isinstance(result, list) else [result]
    except json.JSONDecodeError:
        return []


def get_linux_cpu():
    """Read CPU information from /proc/cpuinfo."""
    info = {}

    try:
        with open("/proc/cpuinfo", "r") as file:
            content = file.read()

        for line in content.splitlines():
            if ":" in line:
                key, value = line.split(":", 1)
                info.setdefault(key.strip(), value.strip())

    except OSError:
        pass

    return info


def get_macos_value(key):
    """Read a value using macOS sysctl."""
    return run_command(["sysctl", "-n", key])


def get_cache_info():
    """Collect CPU cache information."""

    cache = {
        "L1_data": None,
        "L2": None,
        "L3": None,
        "cache_line_size_bytes": 64
    }

    system = platform.system()

    if system == "Linux":
        base = Path("/sys/devices/system/cpu/cpu0/cache")

        if base.exists():
            for index in base.glob("index*"):
                try:
                    level = (index / "level").read_text().strip()
                    cache_type = (index / "type").read_text().strip()
                    size = (index / "size").read_text().strip()

                    if cache_type == "Data" and level == "1":
                        cache["L1_data"] = size

                    elif level == "2":
                        cache["L2"] = size

                    elif level == "3":
                        cache["L3"] = size

                    line_file = index / "coherency_line_size"

                    if line_file.exists():
                        cache["cache_line_size_bytes"] = int(
                            line_file.read_text().strip()
                        )

                except (OSError, ValueError):
                    continue

    elif system == "Windows":
        for item in get_windows_cache():
            level = item.get("Level")
            size = item.get("InstalledSize") or item.get("MaxCacheSize")

            if not size:
                continue

            size_kb = int(size)
            formatted = f"{size_kb} KB"

            if level == 3:
                cache["L3"] = formatted
            elif level == 2:
                cache["L2"] = formatted
            elif level == 1:
                cache["L1_data"] = formatted

    elif system == "Darwin":
        for key, cache_key in [
            ("hw.l1dcachesize", "L1_data"),
            ("hw.l2cachesize", "L2"),
            ("hw.l3cachesize", "L3")
        ]:
            value = get_macos_value(key)

            if value.isdigit():
                cache[cache_key] = f"{int(value) // 1024} KB"

        line = get_macos_value("hw.cachelinesize")

        if line.isdigit():
            cache["cache_line_size_bytes"] = int(line)

    return cache


def get_cpu_info():
    """Collect CPU information across operating systems."""

    system = platform.system()

    cpu = {
        "model_name": platform.processor() or "Unknown",
        "microarchitecture": platform.machine() or "Unknown",
        "base_frequency_mhz": None,
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True)
    }

    if system == "Windows":
        data = get_windows_cpu()

        if data:
            cpu["model_name"] = data.get("Name", cpu["model_name"])
            cpu["base_frequency_mhz"] = data.get("MaxClockSpeed")
            cpu["physical_cores"] = data.get(
                "NumberOfCores", cpu["physical_cores"]
            )
            cpu["logical_cores"] = data.get(
                "NumberOfLogicalProcessors", cpu["logical_cores"]
            )

        # Architecture is reported separately from CPU model.
        cpu["microarchitecture"] = platform.machine()

    elif system == "Linux":
        data = get_linux_cpu()

        cpu["model_name"] = (
            data.get("model name")
            or data.get("Hardware")
            or cpu["model_name"]
        )

        family = data.get("cpu family")
        model = data.get("model")

        if family and model:
            cpu["microarchitecture"] = (
                f"CPU family {family}, model {model} "
                f"(exact microarchitecture not identified)"
            )

        frequency = data.get("cpu MHz")

        if frequency:
            cpu["base_frequency_mhz"] = float(frequency)

    elif system == "Darwin":
        model = get_macos_value("machdep.cpu.brand_string")

        if model:
            cpu["model_name"] = model

        frequency = get_macos_value("hw.cpufrequency")

        if frequency.isdigit():
            cpu["base_frequency_mhz"] = int(frequency) / 1_000_000

        cpu["microarchitecture"] = platform.machine()

    return cpu


def main():
    parser = argparse.ArgumentParser(
        description="Host Topology Profiling and Student ID Salting"
    )

    parser.add_argument(
        "--student-id",
        required=True,
        help="Your 9-digit Student ID"
    )

    args = parser.parse_args()

    # Project directories
    project_root = Path(__file__).resolve().parent.parent
    results_dir = project_root / "results"

    results_dir.mkdir(parents=True, exist_ok=True)

    # Collect hardware information
    cpu = get_cpu_info()
    cache = get_cache_info()

    host_profile = {
        "cpu": cpu,
        "cache": cache,
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "kernel_version": platform.release()
        },
        "python": {
            "implementation": platform.python_implementation(),
            "version": platform.python_version(),
            "compiler": platform.python_compiler(),
            "executable": sys.executable
        }
    }

    # Calculate salted parameters
    salted_params = get_student_params(args.student_id)

    # Save JSON files
    host_path = results_dir / "host_profile.json"
    salt_path = results_dir / "salted_params.json"

    with open(host_path, "w", encoding="utf-8") as file:
        json.dump(host_profile, file, indent=4, ensure_ascii=False)

    with open(salt_path, "w", encoding="utf-8") as file:
        json.dump(salted_params, file, indent=4, ensure_ascii=False)

    print("Host profiling completed!")
    print(f"Host profile: {host_path}")
    print(f"Salted parameters: {salt_path}")

    print("\nCPU:", cpu["model_name"])
    print("Physical cores:", cpu["physical_cores"])
    print("Logical cores:", cpu["logical_cores"])
    print("Salted N:", salted_params["N"])
    print("Seed:", salted_params["seed"])


if __name__ == "__main__":
    main()
