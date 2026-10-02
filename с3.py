import time
import numpy as np
from numba import njit, prange

DTYPE = np.float32


@njit(parallel=True)
def heat_step(u, u_next, alpha=0.20):
    rows, cols = u.shape
    for i in prange(1, rows - 1):
        for j in range(1, cols - 1):
            u_next[i, j] = u[i, j] + alpha * (
                u[i + 1, j] + u[i - 1, j] + u[i, j + 1] + u[i, j - 1] - 4.0 * u[i, j]
            )


GRID_SIZE = 1500
STEPS = 300

u = np.zeros((GRID_SIZE, GRID_SIZE), dtype=DTYPE)
u_next = np.zeros_like(u)

u[0, :] = 100.0
u[:, 0] = 100.0
u_next[0, :] = 100.0
u_next[:, 0] = 100.0

# Warmup
heat_step(u, u_next)

start = time.perf_counter()
for step in range(STEPS):
    heat_step(u, u_next)
    u, u_next = u_next, u
elapsed = time.perf_counter() - start

cells_per_sec = (GRID_SIZE * GRID_SIZE * STEPS) / elapsed / 1e6
print(f"dtype: {np.dtype(DTYPE).name}")
print(f"Heat Diffusion Complete: {elapsed:.3f} s")
print(f"Throughput: {cells_per_sec:.2f} Megacells/sec")
#
#  python с3.py
# dtype: float64
# Heat Diffusion Complete: 0.685 s
# Throughput: 984.93 Megacells/sec
# (.venv) PS C:\Users\User\PycharmProjects\Scripts>



#
# C:\Users\User\PycharmProjects\Scripts\.venv\Scripts\python.exe C:\Users\User\PycharmProjects\Scripts\с3.py
# dtype: float32
# Heat Diffusion Complete: 0.239 s
# Throughput: 2827.55 Megacells/sec
#
# Process finished with exit code 0
