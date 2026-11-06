# Gustafson's Law & Weak Scaling - Practice Repository

Parallel & Distributed Computing Architecture - practice sheet (instructor: Sufyan bin Uzayr), ungraded.

> **Honest status.** Everything here is complete **except the real benchmark data**. Tasks 22-24 need a multi-core machine; the
> sandbox this was built on has one core, so `benchmarks/results.csv`, `plots/scaling_comparison.*` and Part B of
> the hardware audit are produced by *you* in 5 minutes (commands below). Please also read and re-derive the theory tasks yourself before submitting; the drafts are meant to be understood, not just copied.

## Table of contents
1. [Core results](#1-core-results)  2. [When to design for weak scaling](#2-when-to-design-for-gustafson-weak-scaling)
3. [How to run](#3-how-to-run)  4. [Artifact index](#4-artifact-index)  5. [Items you must complete](#5-items-you-must-complete)

## 1. Core results
| Quantity | Formula |
|---|---|
| Scaled speedup (Gustafson) | S(P) = P - alpha(P-1) = alpha + (1-alpha)P |
| Efficiency | E(P) = 1 - alpha(P-1)/P  ->  1 - alpha as P -> infinity |
| Amdahl (fixed size) | S_A(P) = 1/(s + (1-s)/P);  E_A -> 0;  ceiling 1/s |
| Bridge between the two | uniprocessor serial fraction f = alpha/S(P);  Amdahl(f) == Gustafson (Task 03) |
| Max tolerable alpha | alpha_max = (P - S_req)/(P - 1) |
| Memory-bounded (Sun-Ni) | S* = (f + (1-f)G(P)) / (f + (1-f)G(P)/P); G=1 Amdahl, G=P Gustafson |
| With communication | S_C = [P - alpha(P-1)] / [1 + C(P)] |
| Isoefficiency of a Gustafson program | W = Theta(P) |

Headline numbers: alpha = 0.04 gives E -> 0.96 at any scale (Task 06); alpha_max = 0.0845 for S >= 7500 on 8192 cores (Task 07);
s = alpha = 0.08, P = 128: Amdahl 11.47 vs Gustafson 117.84, a 10.3x gap (Task 08).

Main lessons: (1) the two laws answer different questions; (2) alpha must be stated with its frame of reference and problem size;
(3) Gustafson's optimism holds only if serial time stays constant *and* the algorithm's cost per unit of work stays constant (Tasks 12, 13, 18, 20);
(4) report wall-clock time T(P), not just speedup.

## 2. When to design for Gustafson (weak-scaling) principles
Use it when: the science/product gets better with a bigger problem (resolution, ensemble size, samples); work per rank is regular
(stencils, GEMM, Monte Carlo); communication follows surface-to-volume (Task 17); the serial part (I/O, setup) is size-independent or tree-reducible.
Do **not** rely on it when: the job size is fixed (use strong scaling and Amdahl); iterations or steps grow with N (CG, CFL, Task 13);
algorithmic complexity is superlinear in memory (direct N-body, Task 18); communication crosses the bisection (FFT); the workload is irregular (graphs, Task 20); or serial
work grows with data size (O(N) output).
Checklist: fix per-rank problem size; measure alpha on the parallel run; track T(P); model C(P); check memory per node (Task 10); use tree collectives.

## 3. How to run
```bash
pip install numpy matplotlib
python3 calculations/generate_tables.py            # Tasks 06-10, 16, 17
python3 analysis/generate_analysis_tables.py       # Tasks 18, 19
python3 benchmarks/simulator.py                    # Task 21 -> benchmarks/simulator_output.csv, plots/simulator_overlay.*
cd benchmarks/weak_scale_bench
python3 weak_scale_bench.py --out ../results.csv   # Task 22 (>= 5 thread counts; see its README)
cd ..
python3 fit_gustafson.py                           # Task 23 -> summary.csv, fit.json, prints alpha_observed
python3 plot_scaling.py                            # Task 24 -> ../plots/scaling_comparison.png/.pdf
sh collect_hw.sh > hw.txt                          # then fill Part B of analysis/task24_hardware_audit.md
```

## 4. Artifact index
| Task | Artifact | Task | Artifact |
|---|---|---|---|
| 01 | theory/task01_scaling_models.md | 14 | theory/task14_isoefficiency.md |
| 02 | theory/task02_derivation.md | 15 | theory/task15_energy_scaling.md |
| 03 | theory/task03_serial_invariance.md | 16 | calculations/task16_gemm_scaling.md |
| 04 | theory/task04_asymptotic_limits.md | 17 | calculations/task17_stencil_scaling.md |
| 05 | theory/task05_historical_ncube.md | 18 | analysis/task18_nbody_scaling.md |
| 06 | calculations/task06_parametric_table.md | 19 | analysis/task19_monte_carlo.md |
| 07 | calculations/task07_tolerable_serial.md | 20 | analysis/task20_graph_processing.md |
| 08 | calculations/task08_cross_divergence.md | 21 | benchmarks/simulator.py, simulator_output.csv, plots/simulator_overlay.* |
| 09 | calculations/task09_multicomponent.md | 22 | benchmarks/weak_scale_bench/ |
| 10 | calculations/task10_memory_growth.md | 23 | benchmarks/fit_gustafson.py, results.csv (**you generate**) |
| 11 | theory/task11_sun_ni_comparison.md | 24 | benchmarks/plot_scaling.py, analysis/task24_hardware_audit.md, plots/scaling_comparison.* (**you generate**) |
| 12 | theory/task12_communication_penalty.md | 25 | this README |
| 13 | theory/task13_failure_cases.md | | |

Also included: `benchmarks/results_sandbox_1core.csv`, `fit_sandbox_1core.json`, `plots/sandbox_1core_smoke_test.*` - a **pipeline smoke test on a 1-core VM** (speedup < 1, alpha > 1, non-physical). Do not submit as results.

## 5. Items you must complete
1. Run the benchmark on a multi-core machine (Tasks 22-23), then the fit and plot scripts (Task 24).
2. Fill Part B of the hardware audit and write 1-2 paragraphs interpreting your own alpha_observed.
3. Verify all literature citations (Amdahl 1967, Gustafson 1988, Gustafson-Montry-Benner 1988, Sun-Ni 1993, Grama-Gupta-Kumar 1993). They were written from memory without database access and may contain errors; the nCUBE figures in Task 05 especially.
4. Task 09: decide and defend whether phase B (communication) counts toward alpha.
5. Commit one task at a time: `feat: complete task NN <name>`.
