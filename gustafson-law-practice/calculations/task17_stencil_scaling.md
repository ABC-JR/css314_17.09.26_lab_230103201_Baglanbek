# Task 17 - 7-point 3D Stencil: Surface-to-Volume Under Weak Scaling

## Setup
Global domain N^3, 3D block decomposition on P = q^3 ranks. Per-rank block is n x n x n with n = N/q = N/P^(1/3).
* Computation per rank per step: ~ c_f n^3 (about 8 flops per point for a 7-point stencil)
* Halo exchange per rank per step: 6 faces x n^2 points = 6 n^2 (interior rank)
* Communication-to-computation ratio rho = 6 n^2 / n^3 = 6/n

## Weak scaling (Gustafson): volume scales with P
N^3 = P n0^3  =>  N = n0 P^(1/3)  =>  **n = n0 stays constant**  =>  rho = 6/n0 = constant.
Per-rank compute and per-rank halo volume are both independent of P, so the *volume* term of
communication does not grow. Runtime stays flat, as Gustafson requires.

## Strong scaling (Amdahl), fixed N for contrast
n = N/P^(1/3) shrinks, rho = 6 P^(1/3)/N *grows* as P^(1/3): surface-to-volume degrades.

## Table (n0 = 128 per-rank block; strong-scaling N fixed at 2048)
| P | N (weak) | n (weak) | halo pts/rank (weak) | rho (weak) | N (strong) | n (strong) | rho (strong) |
|---|---|---|---|---|---|---|---|
| 1 | 128 | 128 | 98,304 | 0.0469 | 2,048 | 2,048 | 0.0029 |
| 8 | 256 | 128 | 98,304 | 0.0469 | 2,048 | 1,024 | 0.0059 |
| 64 | 512 | 128 | 98,304 | 0.0469 | 2,048 | 512 | 0.0117 |
| 512 | 1,024 | 128 | 98,304 | 0.0469 | 2,048 | 256 | 0.0234 |
| 4,096 | 2,048 | 128 | 98,304 | 0.0469 | 2,048 | 128 | 0.0469 |

## Verdict
The ratio **stays constant** (neither improves nor degrades) under ideal weak scaling; it degrades as P^(1/3) under strong scaling.

## What can still break it (why measured alpha > 0)
* Message **latency**: 6 messages/step regardless of n; matters when n is small.
* Network **hop count / contention** as the machine grows (diameter ~ P^(1/3) on a 3D torus), and
  global reductions (e.g. residual norm) cost O(log P).
* Boundary ranks have fewer neighbours (slightly *less* communication than interior ranks).
* For explicit time stepping the CFL limit forces dt ~ h ~ 1/N, so a fixed *simulated* time needs
  more steps as N grows: constant wall-clock per step is not constant time-to-solution (Task 13).
