# Task 19 - Monte Carlo Path Simulation: The Ideal Weak-Scaling Workload

## 1. Why Monte Carlo is the best case
Each sample path is independent; per-rank work (n paths) is constant under weak scaling and nothing is exchanged until the end.
So alpha should be close to zero. Everything below is what keeps it from being exactly zero.

## 2. Sources of non-zero serial fraction
| Source | Scaling | Mitigation |
|---|---|---|
| PRNG seeding: handing out independent streams. Naive sequential seeding (seed rank i from rank i-1's stream) | O(P) | counter-based generators (Philox, Threefry), leapfrog / skip-ahead, hashed seeds: O(1) per rank |
| Correlated streams (poor seeding such as seed = rank id with a weak generator) | not a time cost: a **correctness** risk | use generators designed for parallel streams (e.g., L'Ecuyer MRG32k3a streams) |
| Final reduction of estimator (sum, sum of squares) | linear gather O(P); tree O(log P) | tree/butterfly reduction, MPI_Reduce/Allreduce |
| Output serialization / I/O (rank 0 writes results, histograms) | O(P) data if per-rank output, O(1) if reduced first | reduce first, parallel I/O, aggregators |
| Setup: reading model parameters, building tables, broadcasting | O(1) to O(log P) | replicate input, broadcast tree |
| Load imbalance when paths terminate randomly (barrier options, particle absorption) | max over P ranks of random durations ~ sigma sqrt(2 ln P) | dynamic work stealing, batch-wise scheduling |
| Variance / statistical efficiency: the *answer* improves only as 1/sqrt(total samples) | accuracy, not speed | not part of alpha, but limits the *value* of weak scaling |

## 3. Quantifying the reduction tree's effect on S(P)
A binomial-tree reduce takes ceil(log2 P) steps, each costing t_hop (latency + small message):
  R_tree(P) = t_hop ceil(log2 P).
A linear gather at the root takes R_lin(P) = (P-1) t_msg.
Model (consistent with Task 12): T_P = T_c + s + R(P), T_1 = P T_c + s, S = T_1 / T_P, alpha_eff = (s + R)/T_P.

Parameters used: per-rank compute T_c = 60 s; fixed serial setup/output s = 0.2 s; t_hop = 50 us;
t_msg = 5 us; naive seeding 2 us per rank. These are **illustrative, not measurements**.

Case A = counter-based RNG + tree reduction. Case B = sequential seeding + linear reduce.

| P | R_tree (ms) | alpha_eff (A) | S (A) | E (A) | seed+linear R (s) | alpha_eff (B) | S (B) | E (B) |
|---|---|---|---|---|---|---|---|---|
| 16 | 0.200 | 0.00333 | 16.0 | 0.9969 | 0.000 | 0.0033 | 16.0 | 0.9969 |
| 1,024 | 0.500 | 0.00333 | 1,020.6 | 0.9967 | 0.007 | 0.0034 | 1,020.5 | 0.9966 |
| 16,384 | 0.700 | 0.00333 | 16,329.4 | 0.9967 | 0.115 | 0.0052 | 16,298.5 | 0.9948 |
| 262,144 | 0.900 | 0.00334 | 261,269.2 | 0.9967 | 1.835 | 0.0328 | 253,544.6 | 0.9672 |
| 1,048,576 | 1.000 | 0.00334 | 1,045,075.0 | 0.9967 | 7.340 | 0.1116 | 931,515.2 | 0.8884 |

## 4. Analysis
* **Case A:** at one million ranks the tree reduction costs only 1 ms (20 levels x 50 us), far below the
  fixed 0.2 s setup/output cost. alpha_eff is dominated by s/T_c (about 0.0033), **not** by the reduction. The tree turns the
  P-dependent term into a rounding error: this is why log P is tolerated and P is not.
* **Case B:** an O(P) serial phase eventually costs seconds, e.g. 7.3 s at P = 2^20, i.e. 11 % of
  the run, so efficiency drops to 0.89 and keeps falling linearly in P: an Amdahl-like ceiling reappears **inside** a weak-scaling workload.
* The dominant practical lever is the constant s (I/O, setup): halving it matters more than optimizing the tree.
* Efficiency E = S/P ~ 1 - alpha_eff, as in Task 04.
* Caveat: weak scaling here buys *throughput* of samples; the statistical error shrinks only as 1/sqrt(P n).
