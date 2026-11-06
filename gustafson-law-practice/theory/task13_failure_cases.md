# Task 13 - Boundary Cases: When Gustafson Fails

Gustafson needs (a) problem size can grow ~ linearly with P, (b) work per processor stays constant, and (c) the
algorithm's *time per unit work* does not change as W grows. Two algorithms violating (c) are analysed below, plus a bonus.

## Case 1 - Implicit PDE solve with Conjugate Gradient (or explicit time stepping)
**Setup.** 3D Poisson, N^3 grid, N^3 ~ P so each rank keeps n^3 points. Work per CG iteration ~ N^3: per-rank constant. Good so far.

**Why the constant-time premise breaks.**
* The condition number of the discrete Laplacian grows as kappa ~ N^2 (h^-2), and the number of CG iterations
  grows as sqrt(kappa) ~ N. With N ~ P^(1/3), iterations ~ P^(1/3).
  Time to solution T(P) ~ P^(1/3) T(1) - **not constant**.
* Each CG iteration needs 2 global dot products (allreduce, O(log P)) so even per-iteration time rises.
* Explicit time stepping has the CFL restriction dt ~ h ~ 1/N: simulating a fixed physical time needs
  N ~ P^(1/3) more steps, again T ~ P^(1/3).
* Multigrid fixes the iteration growth (O(1) iterations) but the coarse levels have very few points per rank and add O(log P) serial-like latency.

**Quantified**: P = 4096 (16x per dimension): CG iterations grow 16x, so T(4096) = 16 T(1) and weak-scaling
efficiency T(1)/T(P) is 1/16 = 6.25 %. Note the trap: if you compute "scaled speedup" with a serial baseline that
*also* needs 16x more iterations, you still obtain S ~ P and the formula looks fine. The failure only shows up when you look at
wall-clock time versus the constant-time premise. Always report T(P) itself, not just S.

## Case 2 - 3D FFT (spectral methods) with global transpose
**Setup.** N^3 grid, work ~ N^3 log N, N^3 ~ P.
**Why it breaks.**
* Work per point is N^3 log(N^3) / N^3 = 3 log N: it **grows** with N, so fixed-per-rank work no longer means fixed time.
* The pencil/slab decomposition needs an all-to-all transpose: each rank sends/receives ~N^3/P data (constant volume),
  but the messages go to ~sqrt(P) (pencil) or P (slab) partners, and the traffic crosses the machine's **bisection**. Bisection
  bandwidth of a 3D torus scales as P^(2/3), not P, so communication time ~ N^3/ P^(2/3) ~ P^(1/3) per step.
* Result: T(P) grows as P^(1/3) (bisection) and by an additional log factor (arithmetic). Weak scaling efficiency falls steadily, a
  textbook "communication-bound" failure.

## Bonus - lock/synchronization contention
A shared work queue or global counter protected by a lock: critical-section time per task is constant, so the
total serialized time ~ number of tasks ~ P x per-thread tasks, i.e. the serial part **grows with W**. alpha is not constant, and the
runtime grows linearly with P: an Amdahl-like cap returns inside the weak-scaling regime.

## Summary table
| Algorithm | Premise violated | Growth of T(P) under "constant work per rank" |
|---|---|---|
| CG/explicit PDE | iterations or steps depend on N | ~ P^(1/3) |
| 3D FFT | log factor + bisection-bound transpose | ~ P^(1/3) log P (approx) |
| lock-protected queue | serial part grows with W | ~ P |

## Diagnostic checklist
1. Does the iteration/step count depend on problem size? 2. Does work per element depend on N (log N, N^(1/2))?
3. Is communication volume per rank constant, and does network capacity (bisection, links) grow with P?
4. Does any serial or shared resource scale with total work?
