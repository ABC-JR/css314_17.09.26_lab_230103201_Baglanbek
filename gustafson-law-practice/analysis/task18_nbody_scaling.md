# Task 18 - N-Body Scaling: Direct O(N^2) vs Barnes-Hut O(N log N)

## 1. Constant time per iteration => how N must grow
Per-rank time T = (work)/(P r). Baseline: N1 = 100,000 particles on one rank takes T0.

**Direct all-pairs.** work ~ N^2, so N^2/P = N1^2 => **N(P) = N1 sqrt(P)**.
**Barnes-Hut.** work ~ N log N, so N log N / P = N1 log N1 => N(P) = N1 P log N1 / log N(P), i.e. **N grows almost linearly, N ~ P / log P** after the first-order correction (solved numerically below).

## 2. Serial/parallel ratio shifts
Per-rank compute is fixed by construction in both. What changes is the non-parallel/communication part:

**Direct:** a rank owns N/P particles but needs *all* N positions each step (all-gather or ring pass): per-rank
communication volume ~ N = N1 sqrt(P), **growing as sqrt(P)** while compute per rank is constant.
Hence the communication fraction C(P) grows ~ sqrt(P) (Task 12 row "gamma sqrt P"), so alpha_eff drifts up and efficiency
falls ~ 1/sqrt(P) asymptotically. Memory per rank (if positions replicated) also grows ~ sqrt(P).

**Barnes-Hut:** each rank needs only its locally essential tree: ~ (N/P)^(2/3) (surface-like) plus O(log P) top-tree nodes, and the
global tree build/load balancing (domain decomposition via space-filling curve sorting) costs O(log P) latency-like terms. The
serial-like portion grows only like **log P** (and (N/P)^(2/3) does not grow: N/P actually falls slowly, as 1/log N, under fixed time).
Irregular/clustered distributions introduce load imbalance, which is the practical alpha for BH.

## 3. Numbers (N1 = 100,000; units of particles/tree-nodes, order-of-magnitude model)
| P | N direct | N/P direct | comm per rank, direct (~N) | N Barnes-Hut | N/P BH | comm per rank, BH ((N/P)^(2/3) + log2 P) |
|---|---|---|---|---|---|---|
| 1 | 100,000 | 100,000 | 100,000 | 100,000 | 100,000 | 2,155 |
| 16 | 400,000 | 25,000 | 400,000 | 1,307,920 | 81,745 | 1,888 |
| 256 | 1,600,000 | 6,250 | 1,600,000 | 17,662,362 | 68,994 | 1,690 |
| 4,096 | 6,400,000 | 1,562 | 6,400,000 | 244,167,412 | 59,611 | 1,538 |
| 65,536 | 25,600,000 | 391 | 25,600,000 | 3,436,212,767 | 52,432 | 1,417 |

Reading the table: at P = 65,536 the direct method has grown the problem only to N = 25,600,000
particles but each rank must handle 25,600,000 communicated positions, 256x the single-rank baseline, while BH has reached
N = 3,436,212,767 (about 52 % of perfectly linear growth) with per-rank communication not growing at all (it even shrinks slightly because N/P falls as 1/log N).

## 4. Conclusions
* Gustafson's "problem grows with P" is **much weaker** for O(N^2) algorithms: the problem only grows as sqrt(P).
  A user hoping for 1000x more particles gets only ~32x on 1000 processors at constant time.
* The comm/compute ratio gets worse with P for direct (sqrt P) but stays nearly flat for tree codes (log P).
* Algorithmic improvement beats hardware growth: BH on 1 rank at N log N has far lower work than direct at the same N.
* The serial/parallel ratio shifts upward (worse) for direct, flat-ish (log P) for BH.
