# Task 03 - The Serial Fraction Invariance Paradox

## The apparent paradox
Amdahl: any serial fraction s > 0 caps speedup at 1/s. Gustafson: with alpha = 0.04 you can
get S = 983 on 1024 cores. Both use "serial fraction" but reach opposite conclusions.

## Resolution: the two fractions have different denominators
* Amdahl's s = T_ser / T_1, **measured on the uniprocessor**, for a fixed problem.
* Gustafson's alpha = T_ser / T_P, **measured on the parallel machine**, for the scaled problem.

## Analytical proof of equivalence
Let the parallel run have serial time alpha and parallel time 1 - alpha, T_P = 1. Then T_1 = alpha + (1-alpha)P = S(P).
The uniprocessor serial fraction of this *scaled* problem is
  f(P) = alpha / T_1 = alpha / S(P) = alpha / (alpha + (1-alpha)P).

Feed f into Amdahl's formula:
  1 - f = (S - alpha)/S = (1-alpha)P / S
  f + (1-f)/P = alpha/S + (1-alpha)/S = 1/S
  S_Amdahl(P; f) = 1 / (1/S) = **S**.

So Gustafson's result is **exactly Amdahl's Law applied to a problem whose uniprocessor serial
fraction shrinks as the problem grows**: f(P) ~ alpha / ((1-alpha)P) -> 0 as P -> inf. There is no
contradiction: Amdahl's ceiling 1/f(P) grows with P, because f is not constant across the scaled family of problems.

## Numbers (alpha = 0.04)
| P | S_G | f = alpha / S | Amdahl ceiling 1/f |
|---|---|---|---|
| 16 | 15.40 | 0.00260 | 385 |
| 256 | 245.80 | 0.000163 | 6,145 |
| 4096 | 3932.2 | 0.0000102 | 98,305 |

(Compute: 0.04/15.4 = 0.0026; 0.04/245.8 = 0.000163; 0.04/3932.2 = 0.0000102.)

## Frame-of-reference memo
1. Measuring serial overhead **on the uniprocessor** tells you about *this* problem size: it is the right
   number for predicting strong scaling.
2. Measuring it **on the parallel machine at the scaled size** tells you the constant that governs weak
   scaling: the absolute serial time does not grow with W, so a growing parallel part dilutes it.
3. The pitfall: quoting a single number "5 % serial" without saying where it was measured and at what problem size is meaningless.
4. Practical consequence: serial overhead is "invariant" in *absolute time*, but its *fraction* depends on the observer's frame.
   That is why the parallel-machine measurement removes the throttle on scaling.
5. Limit of the argument: it assumes the serial **time** really stays constant when W grows. If serial
   work grows with W (e.g., a sequential output phase proportional to data size, O(W) I/O), then alpha is not constant and the paradox dissolves the other way (Task 12/13).
