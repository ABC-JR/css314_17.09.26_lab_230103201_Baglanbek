# Weak-scaling benchmark (Task 22)

Requirements: Python >= 3.9, `numpy`, (for plots) `matplotlib`.

    pip install numpy matplotlib

Run (from `benchmarks/weak_scale_bench/`):

    python3 weak_scale_bench.py --out ../results.csv                 # P = 1,2,4,.. up to your core count
    python3 weak_scale_bench.py --threads 1 2 3 4 6 8 --runs 5 --out ../results.csv

* Close other applications, plug in power, and use a fixed CPU governor if you can.
* Choose `--k` so one worker's compute takes roughly 0.5-2 s (default 100,000,000 intervals ~ 0.5-1 s on a laptop).
* You need >= 5 distinct thread counts that are **<= your hardware thread count**; on a 4-core machine use
  e.g. `--threads 1 2 3 4` plus 6 or 8 (hyper-threads/oversubscription, and say so in your analysis).
* Windows/macOS use the `spawn` start method: pool start-up cost is larger (it is counted as parallel overhead on purpose).

What is measured: see the module docstring. `t_serial_baseline_s` is the time one process needs for the *scaled* problem
(P x k intervals), so S = t_serial / t_parallel is the genuine Gustafson scaled speedup.
