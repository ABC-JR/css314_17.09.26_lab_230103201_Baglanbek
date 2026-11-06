# Task 15 - Energy and Power Proportionality under Scaled Speedup

## 1. Power model (state your assumptions)
* Each powered node draws a static power P_idle at all times.
* While computing it draws an additional dynamic power P_active (so node power during compute = P_idle + P_active; while waiting = P_idle).
* All P nodes stay powered for the whole run; no power gating; communication power ignored.

## 2. P-core scaled run (Gustafson)
Wall-clock T = T_0 (normalized time unit); serial phase alpha T, parallel phase (1-alpha)T.
* Active core-seconds: serial phase 1 core x alpha T + parallel phase P x (1-alpha)T = T[alpha + (1-alpha)P] = **T S(P)**.
* Static energy: P x P_idle x T (all nodes on for T).

  **E_P = T [ P P_idle + P_active S(P) ]**

Work completed: S(P) units (a unit = the baseline problem on 1 core in time T).

## 3. One core, same wall-clock T
Does 1 unit of work: E_1 = T (P_idle + P_active).

## 4. Energy per unit of work
  e_P = E_P / S(P) = T [ P_active + P_idle P/S(P) ] = T [ P_active + P_idle / E(P) ],   E(P) = S/P.
  e_1 = T [ P_active + P_idle ].
  e_P - e_1 = T P_idle (1/E(P) - 1) = T P_idle alpha (P-1) / S(P)  (using 1/E - 1 = (P-S)/S = alpha(P-1)/S)

So energy per unit work **increases** only through the static power wasted on idle cores during the serial phase, scaled by 1/E - 1.
If alpha = 0.04 and P is large: E -> 0.96, so e_P/e_1 -> [P_active + 1.0417 P_idle]/[P_active + P_idle]: a penalty of 4.17 % of P_idle per unit work, not growing with P.

## 5. Equal-work comparison (the fair one)
Solve the scaled problem (S units of work) on 1 core: time S T, energy E_1' = S T (P_idle + P_active).
Ratio: E_P / E_1' = [P P_idle + P_active S] / [S (P_idle + P_active)].
Define P_idle = rho P_active:
  ratio = [rho P + S] / [S (1 + rho)] = [rho/E + 1]/[1 + rho].
Example alpha = 0.04, E = 0.96, rho = 0.5 (static = half of dynamic): ratio = (0.5/0.96 + 1)/1.5 = 1.5208/1.5 = **1.014** - a 1.4 % penalty.
For rho = 2 (static-dominated node): (2.0833 + 1)/3 = 1.028.
Wall-clock: P-core run takes T, 1-core run takes S T (e.g., about 983x longer for P = 1024, alpha = 0.04).

## 6. Findings
* Weak scaling is **energy-neutral to within a few percent** when alpha is small, while time-to-solution
  drops by ~S: a strong argument for scaled parallelism.
* The waste is static power burned during serial phases: it is proportional to alpha P P_idle T. If idle nodes
  could be power-gated (ideal proportionality P_idle -> 0), E_P = E_1' exactly, i.e. no penalty.
* When alpha grows with P (communication, Task 12), E(P) falls and energy per work rises as P_idle/E(P). 
* Design lever: reduce P_idle share, race-to-idle, overlap serial phases (I/O) with computation.
