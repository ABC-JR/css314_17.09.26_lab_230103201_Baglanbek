# Task 14 - Isoefficiency Relation with Gustafson Scaling

> Reference to verify yourself: A. Grama, A. Gupta, V. Kumar, "Isoefficiency: measuring the scalability of parallel algorithms and architectures," IEEE Parallel & Distributed Technology, 1993.

## 1. Definitions
* W = serial work (time on 1 processor) = T_1.
* Overhead function T_o(W, P) = P T_P - W (total time processors spend not doing useful work).
* Efficiency E = W / (W + T_o) = 1 / (1 + T_o/W).
* Isoefficiency: to hold E fixed at some E0, W must grow so that W = K T_o(W, P) with K = E0/(1-E0).
  The solution W = f_E(P) is the isoefficiency function.

## 2. Gustafson-compliant program
Normalize T_P = 1. Then W = T_1 = alpha + (1-alpha)P (serial time alpha is absolute and constant).
  T_o = P T_P - W = P - alpha - (1-alpha)P = alpha P - alpha = **alpha (P-1)**.
Therefore
  E = W/(W + T_o) = [P - alpha(P-1)] / P = 1 - alpha(P-1)/P - same as Task 04. Consistent.

## 3. The isoefficiency function
In Gustafson's model the serial time t_s (= alpha with T_P = 1) is a constant independent of W, and during it the other
P-1 processors idle. Hence the overhead function is
  T_o(W, P) = (P - 1) t_s,   which is Theta(P) and does not depend on W.

Isoefficiency condition W = K T_o with K = E0/(1 - E0):
  W = K t_s (P - 1)   =>   **W = Theta(P)**.

Consistency check with the scaled run: W = P - alpha(P-1) and T_o = alpha(P-1) give K = W/T_o = P/(alpha(P-1)) - 1,
which tends to (1-alpha)/alpha, i.e. E -> 1 - alpha. So a Gustafson-compliant program keeps efficiency at a constant
only because W grows linearly, and no slower rate could do so. Linear growth is also the lower bound for any program that keeps P
processors busy (W = Omega(P)).

  **Isoefficiency function of a Gustafson-compliant weak-scaling program: f_E(P) = Theta(P) - the best attainable.**

## 4. Meaning
* Linear isoefficiency = **perfectly scalable** system: doubling processors requires only doubling the problem.
* In the general framework, the machine is "highly scalable" if f_E(P) = Theta(P) and poorly scalable
  for f_E(P) = Theta(P^2) or P^(3/2) log P (e.g., FFT, Task 13).
* Gustafson's law *assumes* isoefficiency Theta(P) by decree (T_o = alpha(P-1) linear in P because the serial time is constant).
  Real programs with T_o growing faster have worse isoefficiency. Example: with T_o = c P log P (tree-collective
  overhead), W = K c P log P so W must grow as Theta(P log P) to hold E0, i.e. more than linear: fixed-time scaling gives
  efficiency slowly falling.

## 5. Critique
Isoefficiency is the *inverse question* to Gustafson: "How fast must W grow to keep E?" versus "What E do I get if W grows ~P?".
It reveals what Gustafson hides: weak scaling at constant efficiency is only possible if the algorithm's isoefficiency is
O(P). The memory required to hold W = f(P) must also fit (Task 10): if memory per node is fixed, W is capped at Theta(P) for linear-memory algorithms, so isoefficiency functions
growing faster than P (e.g., P log P) are infeasible without more memory per node.
