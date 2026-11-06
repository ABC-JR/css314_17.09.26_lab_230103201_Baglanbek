#!/bin/sh
# Collects the hardware facts needed for analysis/task24_hardware_audit.md.  Run on the SAME machine as the benchmark.
echo "== CPU =="; lscpu 2>/dev/null || sysctl -a 2>/dev/null | grep -E "machdep.cpu|hw\.(ncpu|memsize|l[123]|cachelinesize)"
echo "== Memory =="; free -h 2>/dev/null; (dmidecode -t memory 2>/dev/null | grep -E "Speed|Size|Locator" ) || true
echo "== NUMA =="; numactl --hardware 2>/dev/null || lscpu | grep -i numa
echo "== Governor / frequency =="; cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null; grep MHz /proc/cpuinfo 2>/dev/null | head -4
echo "== Cache =="; lscpu -C 2>/dev/null || lscpu | grep -i cache
echo "== Thermal =="; sensors 2>/dev/null | head -20
echo "== OS =="; uname -a
