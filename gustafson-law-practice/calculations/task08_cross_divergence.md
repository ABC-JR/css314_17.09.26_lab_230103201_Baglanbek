# Task 08 - Amdahl vs Gustafson, s = alpha = 0.08, P = 128

## Amdahl (fixed size)
S_A = 1 / (s + (1-s)/P) = 1 / (0.08 + 0.92/128) = 1 / (0.08 + 0.007188) = 1 / 0.0871875 = **11.470**
Hard ceiling as P -> inf: 1/s = 12.50.

## Gustafson (scaled)
S_G = P - alpha(P-1) = 128 - 0.08 x 127 = 128 - 10.16 = **117.84**

## Discrepancy
* Absolute difference: 106.37
* Gustafson / Amdahl = 10.27x
* Gustafson is 927.4 % higher than Amdahl (percentage relative to Amdahl)
* Amdahl is 90.3 % lower than Gustafson (relative to Gustafson)
State which base you use; the first is the usual "discrepancy" reading.

## Divergence with P
| P | Amdahl | Gustafson | ratio G/A |
|---|---|---|---|
| 4 | 3.226 | 3.760 | 1.17 |
| 16 | 7.273 | 14.800 | 2.04 |
| 64 | 10.596 | 58.960 | 5.56 |
| 128 | 11.470 | 117.840 | 10.27 |
| 1,024 | 12.361 | 942.160 | 76.22 |
| 16,384 | 12.491 | 15,073.360 | 1206.72 |

## Why they diverge
1. Amdahl holds work fixed: the parallel part shrinks as 1/P until the constant serial time dominates -> bounded by 1/s.
2. Gustafson holds *time* fixed: parallel work grows ~ P, serial time stays constant, so the serial
   share of the **parallel** run stays alpha. Speedup is unbounded, slope (1-alpha).
3. The same numeric value 0.08 means different things: a fraction of the 1-core run (Amdahl) vs a
   fraction of the P-core run (Gustafson). The mapping between them (Task 03) is f = alpha / S_G(P).
   Here f = 0.00068, i.e. only 0.07 % of the 1-core *scaled* run is serial.
