# Task 01 - Strong Scaling vs. Weak Scaling Foundations

## 1. The two models in one table

| | Amdahl (1967) | Gustafson-Barsis (1988) |
|---|---|---|
| Question asked | "How fast can I solve **this** problem on P processors?" | "How big a problem can I solve in **this** time on P processors?" |
| Held constant | Problem size W | Wall-clock time T_P |
| Free variable | Time | Problem size W(P) |
| Serial fraction defined on | 1-processor run: s = T_ser / T_1 | P-processor run: alpha = T_ser / T_P |
| Speedup | S_A = 1 / (s + (1-s)/P) | S_G = P - alpha(P-1) = alpha + (1-alpha)P |
| Limit as P -> inf | 1/s (hard ceiling) | unbounded, slope (1 - alpha) |
| Scaling regime | strong scaling | weak scaling |
| Typical user | someone with one job to finish sooner | someone who wants more resolution/fidelity/samples in a fixed budget |

## 2. Problem dimension as P -> infinity
* **Amdahl:** W is constant. Per-processor work W(1-s)/P -> 0. Eventually the run is nothing but the
  constant serial time sW, so T_P -> sT_1 and speedup saturates at 1/s. Example: s = 0.05 caps speedup at 20 no matter how many cores.
* **Gustafson:** T_P is constant. The parallel work per processor is constant, so total parallel work
  grows as P: W(P) = alpha W_0 + (1-alpha) P W_0 -> infinity linearly. The serial time stays a fixed
  absolute amount, so it is a vanishing fraction of the *1-core equivalent* run (Task 03: f = alpha/S).

## 3. Why "fixed-size" vs "fixed-time"
* Amdahl's Law is **fixed-size** because its derivation compares T_1(W) with T_P(W) for the *same W*;
  the only thing that changes is how many workers share it. The unit of comparison is the problem.
* Gustafson's Law is **fixed-time** because its derivation fixes T_P = s + p = 1 and asks how much work an
  *ideal single processor* would need to match what the P-processor machine did in that time. The unit of comparison is the time budget.

## 4. Philosophical / physical divergence
* Amdahl's view treats the computer as a **tool to shorten an existing task**; it reflects an era of fixed
  workloads and gives a pessimistic outlook for massive parallelism.
* Gustafson's view treats the computer as a **capability that expands the task**. In practice scientists do
  not run the 1987 mesh on a 2024 machine; they refine the mesh, add physics, or run more ensemble members until the run takes about an hour again.
* Physically: the serial part (setup, I/O, global coordination) is mostly independent of resolution, while
  the parallel part (grid sweeps, particle updates) grows with resolution. A growing problem therefore dilutes the serial part.
* They are **not contradictory laws** - they answer different questions and are algebraically linked (Task 03).
  Using the wrong one is a modelling error: Amdahl for a strong-scaling study, Gustafson when the workload truly scales.
* Honest caveat: Gustafson's optimism depends on W being able to grow without changing the algorithm's
  cost structure (see Tasks 11, 13). Not every user has a bigger problem to solve.

*Historical references to check yourself: G. Amdahl, "Validity of the single processor approach to achieving
large scale computing capabilities," AFIPS 1967; J. Gustafson, "Reevaluating Amdahl's Law," CACM 31(5), 1988.*
