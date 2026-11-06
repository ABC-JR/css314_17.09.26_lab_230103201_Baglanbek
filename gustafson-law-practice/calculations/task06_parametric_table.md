# Task 06 - Parametric Speedup, alpha = 0.04

Formulas: S(P) = P - alpha(P-1); E(P) = S(P)/P = 1 - alpha(P-1)/P.

| P | S(P) | E(P) | Efficiency lost 1-E |
|---|---|---|---|
| 16 | 15.4000 | 0.962500 | 0.037500 |
| 64 | 61.4800 | 0.960625 | 0.039375 |
| 256 | 245.8000 | 0.960156 | 0.039844 |
| 1,024 | 983.0800 | 0.960039 | 0.039961 |
| 4,096 | 3,932.2000 | 0.960010 | 0.039990 |
| 16,384 | 15,728.6800 | 0.960002 | 0.039998 |

## Worked example (P = 1024)
S = 1024 - 0.04 x 1023 = 1024 - 40.92 = 983.08
E = 983.08 / 1024 = 0.96008

## Evaluation
* Efficiency does **not** collapse as P grows exponentially. It falls from 0.9625 (P=16)
  and converges to the asymptote **1 - alpha = 0.96**; going from P=1024 to P=16384
  changes E only in the fifth decimal place.
* The only "degradation" happens in the first few doublings: the loss term alpha(P-1)/P
  is already 96% of its limit alpha at P=16.
* Speedup grows linearly in P with slope (1 - alpha) = 0.96; every added core
  buys 0.96 cores of useful throughput. That is the practical meaning of weak scaling.
* This assumes alpha is *constant*. Real systems see alpha grow with P through
  communication (see Task 12), so measured efficiency will fall faster than this table.
