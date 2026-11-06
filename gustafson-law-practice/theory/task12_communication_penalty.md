# Task 12 - Gustafson's Law with a Communication-Overhead Term

## 1. Baseline problem
Classical Gustafson keeps alpha constant. Real machines add communication whose cost grows with P
(tree collectives ~ log P, 2D mesh/halo-latency ~ sqrt(P)).

## 2. Model
Normalize the **ideal** per-processor run to s + p = 1 as before (alpha = s). Add a communication/synchronization
time C(P), expressed as a fraction of that unit. C(1) = 0 (no communication on one processor).

  T_P = s + p + C(P) = 1 + C(P)
  T_1 = s + pP          (a single processor does the full scaled work and **no communication**)

**Modified scaled speedup**

  S_C(P) = [alpha + (1-alpha) P] / [1 + C(P)] = [P - alpha(P-1)] / [1 + C(P)]

Efficiency: E_C(P) = [1 - alpha(P-1)/P] / [1 + C(P)].

Note: one could lump C(P) into an "effective alpha", but communication is concurrent across ranks, not serial,
so the quotient form above is the one that matches the model exactly. Prefer it.

## 3. Asymptotics for common forms of C(P)
| C(P) | S_C(P) as P -> inf | E_C(P) -> |
|---|---|---|
| 0 | (1-alpha)P | 1 - alpha |
| gamma log2 P | ~ (1-alpha) P / (gamma log2 P) | ~ (1-alpha)/(gamma log2 P) -> 0 slowly |
| gamma sqrt(P) | ~ (1-alpha) sqrt(P)/gamma | ~ (1-alpha)/(gamma sqrt P) -> 0 |
| gamma P (naive all-to-one) | -> (1-alpha)/gamma (bounded!) | ~ 1/P |

So a linear communication term brings back an Amdahl-like ceiling even under weak scaling.

## 4. Numerical illustration (alpha = 0.04, gamma = 0.01)
| P | S_Gustafson | S_C log | S_C sqrt |
|---|---|---|---|
| 64 | 61.48 | 61.48/1.06 = 58.0 | 61.48/1.08 = 56.9 |
| 1024 | 983.08 | 983.08/1.10 = 893.7 | 983.08/1.32 = 744.8 |
| 16384 | 15728.7 | 15728.7/1.14 = 13797 | 15728.7/2.28 = 6898 |

(1 + 0.01 log2 64 = 1.06; 1 + 0.01 sqrt64 = 1.08; log2 1024 = 10 -> 1.10; sqrt 1024 = 32 -> 1.32;
log2 16384 = 14 -> 1.14; sqrt 16384 = 128 -> 2.28.)

## 5. Bridging to latency-bandwidth (alpha-beta) models
For a collective on P ranks with message size m: C(P) = (t_s log2 P + t_w m (P-1)/P) / T_unit
(recursive-doubling allreduce). The latency term gives log P growth; the bandwidth term saturates.
Halo exchange: C = (6 t_s + 6 t_w n^2) / T_unit, constant in P except for contention.

## 6. Design implications
* Use tree/hierarchical collectives (log P instead of P).
* Overlap communication with computation to push C(P)'s *visible* part toward zero.
* Keep per-rank work large enough that gamma (the comm/compute ratio) stays small.
* Measure C(P) empirically: fit S_meas(P)(1 + C(P)) vs P - alpha(P-1) and select the C family with smallest residual.
