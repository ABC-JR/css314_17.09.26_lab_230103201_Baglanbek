# Task 10 - Memory Ceiling and Maximum 3D Grid Dimension

## Formulation
Weak scaling: W(P) = P W(1). Memory: M(P) = c P, where c = bytes per node actually used.
Per-node cap: 32 GiB = 34,359,738,368 bytes. Aggregate capacity: M_max(P) = 32 GiB x P.

Grid with N^3 points, b bytes per point (b = bytes/array x number of arrays; **state this assumption**):
  b N^3 <= 32 GiB x P  =>  N_max(P) = (32 GiB x P / b)^(1/3) = N_max(1) x P^(1/3)

Per-node subdomain side: n = N/P^(1/3) = (32 GiB / b)^(1/3). For b = 8: n = 1,625.

## Results
| Memory per grid point | Nodes | Aggregate memory | N_max | N_max^3 points |
|---|---|---|---|---|
| 1 double array (8 B/pt) | 1 | 32 GiB | 1,625 | 4.295e+09 |
| 1 double array (8 B/pt) | 64 | 2,048 GiB | 6,502 | 2.749e+11 |
| 1 double array (8 B/pt) | 512 | 16,384 GiB | 13,004 | 2.199e+12 |
| 5 double arrays (40 B/pt) | 1 | 32 GiB | 951 | 8.590e+08 |
| 5 double arrays (40 B/pt) | 64 | 2,048 GiB | 3,802 | 5.498e+10 |
| 5 double arrays (40 B/pt) | 512 | 16,384 GiB | 7,605 | 4.398e+11 |
| 10 double arrays (80 B/pt) | 1 | 32 GiB | 754 | 4.295e+08 |
| 10 double arrays (80 B/pt) | 64 | 2,048 GiB | 3,018 | 2.749e+10 |
| 10 double arrays (80 B/pt) | 512 | 16,384 GiB | 6,036 | 2.199e+11 |

Headline answer (b = 8 B, one double array): **N_max(64) ~ 6,502, N_max(512) ~ 13,004**.

## Observations
* 8x more nodes -> 8x more grid points -> only **2x** larger N (cube root).
* Memory-bound weak scaling is consistent with Gustafson only if work per grid point is constant.
  For a stencil that holds (work ~ N^3 ~ P). For GEMM it does not (Task 16): work grows faster than memory.
* Real solvers need several arrays, halos and buffers; use b = 40-80 B for a more realistic ceiling
  (N_max(512) ~ 7,605-6,036).
