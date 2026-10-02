import time
import numpy as np
import numba
from numba import njit, prange

MAXT = numba.config.NUMBA_NUM_THREADS
print(f"Hardware Threads Detected: {MAXT}")


@njit(parallel=True)
def monte_carlo_pi(n_samples):
    inside_circle = 0
    for i in prange(n_samples):
        x = np.random.uniform(0.0, 1.0)
        y = np.random.uniform(0.0, 1.0)
        if x * x + y * y <= 1.0:
            inside_circle += 1
    return (4.0 * inside_circle) / n_samples


# JIT warmup
_ = monte_carlo_pi(10_000)

SAMPLES = 120_000_000
thread_counts = sorted(set(t for t in [1, 2, 4, 8, MAXT] if t <= MAXT))

print(f"{'Threads':<10} | {'Time (s)':<12} | {'Speedup':<10} | {'Efficiency (%)':<15}")
print("-" * 55)

t1_baseline = None
for t in thread_counts:
    numba.set_num_threads(t)
    start = time.perf_counter()
    pi_est = monte_carlo_pi(SAMPLES)
    elapsed = time.perf_counter() - start
    if t == 1:
        t1_baseline = elapsed
        speedup = 1.0
        efficiency = 100.0
    else:
        speedup = t1_baseline / elapsed
        efficiency = (speedup / t) * 100.0
    print(f"{t:<10} | {elapsed:<12.4f} | {speedup:<9.2f}x | {efficiency:<15.1f}")
#
# C:\Users\User\PycharmProjects\Scripts\.venv\Scripts\python.exe C:\Users\User\PycharmProjects\Scripts\с1.py
# Hardware Threads Detected: 16
# Threads    | Time (s)     | Speedup    | Efficiency (%)
# -------------------------------------------------------
# 1          | 3.4577       | 1.00     x | 100.0
# 2          | 2.1924       | 1.58     x | 78.9
# 4          | 1.1453       | 3.02     x | 75.5
# 8          | 0.6691       | 5.17     x | 64.6
# 16         | 0.4271       | 8.10     x | 50.6
#
# Process finished with exit code 0
