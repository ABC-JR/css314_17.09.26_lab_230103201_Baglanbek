# Task 04 - Asymptotic Analysis of Parallel Efficiency

## Gustafson
E_G(P) = S_G/P = [P - alpha(P-1)]/P = 1 - alpha(P-1)/P = 1 - alpha + alpha/P.

**Limit.** lim_{P->inf} alpha/P = 0 (alpha constant, 1/P -> 0), so
  **lim E_G(P) = 1 - alpha.**

Epsilon-style proof: for any eps > 0, |E_G(P) - (1-alpha)| = alpha/P < eps whenever P > alpha/eps.

Monotonicity: dE_G/dP = -alpha/P^2 < 0. Efficiency is strictly decreasing from E(1) = 1 but bounded below by 1 - alpha,
so it converges (monotone bounded sequence). Examples: alpha = 0.04 -> 0.96; alpha = 0.10 -> 0.90; alpha = 0.20 -> 0.80.

## Amdahl
S_A = 1/(s + (1-s)/P), so
E_A(P) = S_A/P = 1 / (sP + (1-s)).

**Limit.** The denominator sP + 1 - s -> infinity for s > 0, hence
  **lim E_A(P) = 0** (for any s > 0).

Rate: E_A ~ 1/(sP): efficiency falls like 1/P. Half-efficiency is reached at sP + 1 - s = 2, i.e. P = (1+s)/s ~ 1/s
(for s = 0.05, P = 21). For s = 0 the limit is 1.

## Contrast
| | Gustafson | Amdahl |
|---|---|---|
| lim E(P) | 1 - alpha (positive plateau) | 0 |
| approach | alpha/P (fast, bounded loss) | 1/(sP) (efficiency vanishes) |
| speedup limit | infinity, slope 1-alpha | 1/s |
| meaning | each added core is ~ (1-alpha) useful | each added core is worth less and less |

## Deductions
1. Under weak scaling the machine can be filled efficiently at any size; the loss is a flat tax of alpha.
2. Under strong scaling you must stop adding cores when marginal efficiency is unacceptable; around P ~ 1/s.
3. Both are consistent with each other (Task 03): Gustafson's plateau is Amdahl's decay with a shrinking f(P).
4. Real caveat: when alpha itself grows with P (communication, Task 12), E_G -> 0 too, just much more slowly than Amdahl.
