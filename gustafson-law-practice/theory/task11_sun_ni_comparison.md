# Task 11 - Gustafson vs. the Sun-Ni Memory-Bounded Model

> Reference to verify yourself: X.-H. Sun and L. Ni, "Scalable problems and memory-bounded speedup," JPDC 19(1), 1993.

## 1. One framework, three laws
Let the sequential work fraction be f (of the 1-processor, original-size run) and G(P) be the factor by
which the **parallel** workload grows when P processors (and P times the memory) are available.

Sun-Ni memory-bounded speedup:

  S*(P) = [ f + (1-f) G(P) ] / [ f + (1-f) G(P) / P ]

| G(P) | Meaning | Result |
|---|---|---|
| 1 | no growth (fixed size) | S = 1 / (f + (1-f)/P) -> **Amdahl** |
| P | work grows linearly with P (fixed time) | S = f + (1-f)P -> **Gustafson** (f here is the 1-core fraction) |
| G(P) = P^(3/2) (e.g. GEMM, memory-bounded) | work grows faster than P | S* > Gustafson, approaching (but never exceeding) P as G grows |
| G(P) < P | work grows slower than P | S* between Amdahl and Gustafson |

Check: G = P gives numerator f + (1-f)P, denominator f + (1-f) = 1 -> S = f + (1-f)P. OK.

## 2. What G(P) is: memory-bounded growth
If memory M(N) of a problem of size N and work W(N) are related by W = g(M) (e.g. for GEMM
M ~ N^2, W ~ N^3, so W = M^(3/2)), then filling P times the memory gives
  G(P) = g(P M_1)/g(M_1)
For GEMM G(P) = P^(3/2). For a stencil (W ~ M) G(P) = P. For a sort (W ~ M log M) G(P) ~ P log P / log-correction.

## 3. When does Gustafson over/under-estimate?
**Underestimates** (real throughput of the *memory-filling* run is better than Gustafson predicts) when
G(P) > P: work per byte rises with problem size (GEMM, dense LU, N-body direct). Each processor does *more* than
a fixed amount of work and the serial fraction is diluted even faster. Caveat: the run time then **grows** (T ~ G/P),
so this is a different guarantee from Gustafson's fixed time. The speedup is high, but the user waits longer.

**Overestimates** when:
1. G(P) < P: work per byte falls (e.g. algorithms whose useful work grows more slowly than memory),
2. Memory per node is not the limit but **time** is - Gustafson's problem size is infeasible under the
   memory cap of the node count (a "memory wall"); i.e. the required W(P) > capacity.
3. alpha is not constant: serial section or communication grows with the enlarged problem (O(W) I/O, global reductions, Task 12).
4. Problem growth changes the algorithm's cost (iteration counts, Task 13).
5. Load imbalance appears at scale.

## 4. Worked comparison (f = 0.05, P = 64)
| Model | Computation | S |
|---|---|---|
| Amdahl (G=1) | 1/(0.05+0.95/64) | 15.42 |
| Gustafson (G=P) | 0.05 + 0.95 x 64 | 60.85 |
| Sun-Ni, G = P^1.5 = 512 | (0.05+0.95x512)/(0.05+0.95x512/64) = 486.45/7.65 | 63.59 |

(Numerator 0.05 + 0.95 x 512 = 486.45; denominator 0.05 + 0.95 x 512/64 = 7.65.)
Note S* < P always: the denominator is at least (1-f)G/P, so S* < P. Sun-Ni speedup approaches P as G -> infinity.
Sun-Ni with G = P^1.5 gives 63.6, the highest, because the serial part is diluted most.

## 5. Take-away
Gustafson is the special case G(P) = P of the memory-bounded model, and the three laws are views of the same formula with different
assumptions about how the workload grows. Pick G(P) from the algorithm's work/memory relationship, then check what happens to *time*.
