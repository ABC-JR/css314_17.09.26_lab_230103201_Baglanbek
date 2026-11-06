# Task 16 - Dense GEMM Under Fixed-Time Scaling

## Proof
Work W(N) = 2N^3 flops (O(N^3)). Fixed runtime with P processors at fixed per-processor rate r:
  W(N)/(P r) = T0 = W(N1)/r    (T0 = runtime of the baseline N1 on one processor)
  2N^3 / P = 2 N1^3
  N^3 = P N1^3
  **N(P) = N1 P^(1/3)**

Doubling N needs 8x the processors.

## Table (N1 = 1000, doubles, one matrix shown)
| P | P^(1/3) | N(P) | one matrix, total (MB) | one matrix, per processor (MB) | N if memory-bounded: N1 sqrt(P) (Sun-Ni, Task 11) |
|---|---|---|---|---|---|
| 1 | 1.000 | 1,000 | 8.0 | 8.00 | 1,000 |
| 8 | 2.000 | 2,000 | 32.0 | 4.00 | 2,828 |
| 64 | 4.000 | 4,000 | 128.0 | 2.00 | 8,000 |
| 512 | 8.000 | 8,000 | 512.0 | 1.00 | 22,627 |
| 4,096 | 16.000 | 16,000 | 2,048.0 | 0.50 | 64,000 |
| 32,768 | 32.000 | 32,000 | 8,192.0 | 0.25 | 181,019 |

(Multiply memory by 3 for A, B and C.)

## Key consequences
1. Memory per processor *shrinks*: N^2/P = N1^2 P^(-1/3). GEMM is compute-bound, so under fixed
   time memory is **not** the limit (unlike the stencil in Task 10 where memory per node is constant).
2. If you instead fill memory (N ~ sqrt(P)), runtime grows as N^3/P = P^(1/2): fixed-time breaks (Task 11).
3. Communication: 2D algorithms (SUMMA) move ~ N^2/sqrt(P) words per processor. With N ~ P^(1/3):
   N^2/sqrt(P) ~ P^(2/3 - 1/2) = **P^(1/6)**. It grows slowly (4096x more processors -> 4x more
   words per rank), so alpha is not perfectly constant, but the drift is mild.
4. GEMM therefore weak-scales well in the Gustafson sense, with N growing only as the cube root of P.
