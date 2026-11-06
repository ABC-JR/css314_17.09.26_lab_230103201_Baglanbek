## Results and interpretation (my machine)
Measured with 5 runs per configuration, P = 1, 2, 4, 8, 16 (16 hardware threads).
Scaled speedup was 0.98, 1.59, 3.03, 4.28 and 4.98 respectively, so weak-scaling
efficiency fell to 0.31 at P = 16. The least-squares fit gives
alpha_observed = 0.69 +/- 0.05 (R^2 = 0.96). This is far above the ~3% serial
phase built into the benchmark, so alpha here is not a true serial fraction: it
lumps together everything that makes the parallel run slower than ideal. Parallel
wall-clock time grew from 1.6 s (P=1) to 5.9 s (P=16) although per-worker work
was constant, and run-to-run variance was large at P=2 and above. Likely causes,
which I did not isolate: the all-core clock being lower than the single-core turbo
clock, power/thermal limits on a laptop, hyper-threads sharing physical cores
beyond the physical-core count, and OS scheduling noise on Windows. A first run
that included process start-up (results_with_startup.csv) gave alpha = 0.90,
showing how much Windows process spawning inflates the apparent serial fraction.
Gustafson's formula is a poor fit here (the free-intercept slope 0.26 vs 0.31
predicted), because the model assumes constant per-worker speed and no overhead
that grows with P.


