# Parallel Computing Performance
## Empirical Scalability Diagnostics: The Karp–Flatt Metric

## 1. Hardware Profile

- CPU: AMD Ryzen 7 7735HS
- Physical Cores: 8
- Logical Cores: 16
- Operating System: Windows 11 Pro
- Python Version: [Fill in using `python --version`]

## 2. Experiment A — Serial Tail

| Workers | Runtime (s) | Speedup | Karp–Flatt |
|---:|---:|---:|---:|
| 1 | 8.178 | 1.000 | N/A |
| 2 | 4.674 | 1.750 | 0.143 |
| 4 | 2.937 | 2.785 | 0.145 |

**Architectural Diagnosis:**

The Karp–Flatt values remain nearly constant as the number of workers increases. This indicates a fixed sequential fraction in the program, caused by the intentional 0.40-second serial delay.

The ratio e(4)/e(2) is approximately 1.014, which is within the required range of 0.80–1.25.

## 3. Experiment B — Lock Contention

| Workers | Runtime (s) | Speedup | Karp–Flatt |
|---:|---:|---:|---:|
| 1 | 4.826 | 1.000 | N/A |
| 2 | 29.388 | 0.164 | 11.179 |
| 4 | 22.750 | 0.212 | 5.952 |

**Architectural Diagnosis:**

The shared counter requires a lock for every increment. This creates heavy synchronization overhead when multiple processes compete for access to the shared resource.

The parallel executions are significantly slower than the single-process execution. The Karp–Flatt values are much higher than in Experiment A, demonstrating severe lock contention.

## 4. Experiment C — Privatized State

| Workers | Runtime (s) | Speedup | Karp–Flatt |
|---:|---:|---:|---:|
| 1 | 1.398 | 1.000 | N/A |
| 2 | 0.686 | 2.037 | -0.018 |
| 4 | 0.449 | 3.117 | 0.094 |

**Parallel Efficiency:**

E(4) = 3.117 / 4 × 100% = 77.9%

**Architectural Diagnosis:**

Each worker maintains its own local counter without using a shared lock. The partial results are combined once at the end of execution.

The four-worker execution is faster than the single-worker execution, achieving a speedup of 3.117x and parallel efficiency of approximately 77.9%.

The measured e(4) is 0.094, which is higher than the expected target. However, the measured runtime and parallel efficiency satisfy the final Experiment C verification criteria.

## 5. Overall Conclusion

The experiments demonstrate three different scalability behaviors:

1. Experiment A: A fixed sequential portion limits parallel speedup.
2. Experiment B: Shared-state synchronization introduces severe lock contention and reduces performance.
3. Experiment C: Privatizing state and combining results at the end restores effective parallel execution.

The results show that parallel performance depends not only on the number of workers but also on how shared resources and synchronization are managed.