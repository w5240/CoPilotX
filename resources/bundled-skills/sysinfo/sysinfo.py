#!/usr/bin/env python3
"""
System Information Query Tool
Query CPU, memory, disk, network, and process information.
"""

import sys
import subprocess
import platform
import os
from datetime import datetime


def run_command(cmd: str) -> str:
    """
    Run a shell command and return the output.

    Args:
        cmd: Command to run

    Returns:
        Command output as string
    """
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Command timeout"
    except Exception as e:
        return f"Error: {str(e)}"


def get_system_info() -> dict:
    """
    Get basic system information.

    Returns:
        Dictionary with system info
    """
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'hostname': platform.node(),
        'python_version': platform.python_version()
    }


def get_cpu_info() -> str:
    """
    Get CPU information.

    Returns:
        Formatted CPU info string
    """
    system = platform.system()

    if system == 'Darwin':  # macOS
        cpu_count = os.cpu_count()
        cpu_info = run_command("sysctl -n machdep.cpu.brand_string")
        cpu_cores = run_command("sysctl -n hw.ncpu")
        cpu_freq = run_command("sysctl -n hw.cpufrequency")
        cpu_load = run_command("sysctl -n vm.loadavg")

        return f"""CPU Information:
----------------
CPU Model: {cpu_info}
CPU Cores: {cpu_cores}
Logical CPUs: {cpu_count}
CPU Frequency: {int(int(cpu_freq) / 1000000)} MHz
Load Average: {cpu_load}
"""

    elif system == 'Linux':
        cpu_info = run_command("lscpu | grep 'Model name' | cut -d':' -f2 | xargs")
        cpu_cores = run_command("nproc")
        cpu_load = run_command("uptime | awk -F'load average:' '{print $2}'")

        return f"""CPU Information:
----------------
CPU Model: {cpu_info}
CPU Cores: {cpu_cores}
Load Average: {cpu_load}
"""

    else:  # Windows
        cpu_info = run_command("wmic cpu get name")
        cpu_cores = run_command("wmic cpu get NumberOfCores")

        return f"""CPU Information:
----------------
{cpu_info}
Cores: {cpu_cores}
"""


def get_memory_info() -> str:
    """
    Get memory information.

    Returns:
        Formatted memory info string
    """
    system = platform.system()

    if system == 'Darwin':  # macOS
        total_mem = run_command("sysctl -n hw.memsize")
        used_mem = run_command("vm_stat | grep 'Pages free' | awk '{print $3}' | sed 's/\\.//'")
        page_size = run_command("vm_stat | head -1 | awk '{print $2}' | sed 's/\\.//'")

        total_gb = int(total_mem) / (1024**3)
        free_pages = int(used_mem) if used_mem.isdigit() else 0
        free_gb = (free_pages * int(page_size)) / (1024**3)
        used_gb = total_gb - free_gb
        usage_percent = (used_gb / total_gb) * 100

        return f"""Memory Information:
------------------
Total Memory: {total_gb:.2f} GB
Used Memory: {used_gb:.2f} GB
Free Memory: {free_gb:.2f} GB
Usage: {usage_percent:.1f}%
"""

    elif system == 'Linux':
        mem_info = run_command("free -h | grep Mem")

        return f"""Memory Information:
------------------
{mem_info}
"""

    else:  # Windows
        mem_info = run_command("wmic OS get TotalVisibleMemorySize,FreePhysicalMemory")

        return f"""Memory Information:
------------------
{mem_info}
"""


def get_disk_info() -> str:
    """
    Get disk information.

    Returns:
        Formatted disk info string
    """
    system = platform.system()

    if system == 'Darwin':  # macOS
        disk_info = run_command("df -h / | tail -1")
        parts = disk_info.split()

        if len(parts) >= 5:
            total = parts[1]
            used = parts[2]
            available = parts[3]
            usage = parts[4]

            return f"""Disk Information:
----------------
Filesystem: /
Total: {total}
Used: {used}
Available: {available}
Usage: {usage}
"""

    elif system == 'Linux':
        disk_info = run_command("df -h / | tail -1")

        return f"""Disk Information:
----------------
Filesystem: /
{disk_info}
"""

    else:  # Windows
        disk_info = run_command("wmic logicaldisk get size,freespace,caption")

        return f"""Disk Information:
----------------
{disk_info}
"""

    return "Disk information not available"


def get_network_info() -> str:
    """
    Get network information.

    Returns:
        Formatted network info string
    """
    system = platform.system()

    if system == 'Darwin':  # macOS
        ip_info = run_command("ifconfig | grep 'inet ' | grep -v 127.0.0.1 | head -1 | awk '{print $2}'")
        gateway = run_command("route -n get default | grep 'gateway' | awk '{print $2}'")

        return f"""Network Information:
-------------------
IP Address: {ip_info if ip_info else 'N/A'}
Gateway: {gateway if gateway else 'N/A'}
"""

    elif system == 'Linux':
        ip_info = run_command("hostname -I | awk '{print $1}'")
        gateway = run_command("ip route | grep default | awk '{print $3}'")

        return f"""Network Information:
-------------------
IP Address: {ip_info if ip_info else 'N/A'}
Gateway: {gateway if gateway else 'N/A'}
"""

    else:  # Windows
        ip_info = run_command("ipconfig | findstr IPv4")

        return f"""Network Information:
-------------------
{ip_info}
"""


def get_process_info() -> str:
    """
    Get process information.

    Returns:
        Formatted process info string
    """
    system = platform.system()

    if system == 'Darwin':  # macOS
        processes = run_command("ps aux | sort -rk 3 | head -10")

        return f"""Top 10 Processes (by CPU):
---------------------------
{processes}
"""

    elif system == 'Linux':
        processes = run_command("ps aux --sort=-%cpu | head -10")

        return f"""Top 10 Processes (by CPU):
---------------------------
{processes}
"""

    else:  # Windows
        processes = run_command("tasklist | head -10")

        return f"""Top Processes:
-------------
{processes}
"""


def get_summary() -> str:
    """
    Get system summary.

    Returns:
        Formatted summary string
    """
    system_info = get_system_info()
    cpu_info = get_cpu_info().split('\n')[1:3]
    mem_info = get_memory_info().split('\n')[1:3]

    return f"""System Summary:
===============
Platform: {system_info['platform']} {system_info['platform_release']}
Hostname: {system_info['hostname']}
Architecture: {system_info['architecture']}

{chr(10).join(cpu_info)}

{chr(10).join(mem_info)}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""


def main():
    """
    Main entry point.
    """
    if len(sys.argv) < 2:
        print("Usage: sysinfo <command>")
        print("Commands: all, cpu, memory, disk, network, processes, summary")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == 'all':
        print("=" * 60)
        print("SYSTEM INFORMATION")
        print("=" * 60)
        print()
        print(get_system_info())
        print()
        print(get_cpu_info())
        print(get_memory_info())
        print(get_disk_info())
        print(get_network_info())
        print(get_process_info())

    elif command == 'cpu':
        print(get_cpu_info())

    elif command == 'memory':
        print(get_memory_info())

    elif command == 'disk':
        print(get_disk_info())

    elif command == 'network':
        print(get_network_info())

    elif command == 'processes':
        print(get_process_info())

    elif command == 'summary':
        print(get_summary())

    else:
        print(f"Unknown command: {command}")
        print("Available commands: all, cpu, memory, disk, network, processes, summary")
        sys.exit(1)


if __name__ == '__main__':
    main()
