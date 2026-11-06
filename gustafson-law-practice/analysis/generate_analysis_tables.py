#!/usr/bin/env python3
"""Generates analysis/task18_nbody_scaling.md and analysis/task19_monte_carlo.md.
Run from repo root: python3 analysis/generate_analysis_tables.py"""
import math, pathlib
out = pathlib.Path(__file__).parent
Ps = (1, 16, 256, 4096, 65536)

# ------------------------------ Task 18 ------------------------------
N1 = 100_000
def bh_N(P):
    target = N1 * math.log2(N1)          # per-P-unit work: N log2 N / P = const
    N = N1 * P
    for _ in range(200):                 # fixed-point iteration N = target*P/log2 N
        N = target * P / math.log2(N)
    return N
rows = []
for P in Ps:
    Nd = N1 * math.sqrt(P)
    Nb = bh_N(P)
    comm_d = Nd                          # all-gather: every rank needs all N positions
    comm_b = (Nb / P) ** (2/3) + math.log2(max(P, 2))   # essential-tree surface + log P
    rows.append(f"| {P:,} | {Nd:,.0f} | {Nd/P:,.0f} | {comm_d:,.0f} | {Nb:,.0f} | {Nb/P:,.0f} | {comm_b:,.0f} |")
(out / "task18_nbody_scaling.md").write_text(f"""# Task 18 - N-Body Scaling: Direct O(N^2) vs Barnes-Hut O(N log N)

## 1. Constant time per iteration => how N must grow
Per-rank time T = (work)/(P r). Baseline: N1 = {N1:,} particles on one rank takes T0.

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

## 3. Numbers (N1 = {N1:,}; units of particles/tree-nodes, order-of-magnitude model)
| P | N direct | N/P direct | comm per rank, direct (~N) | N Barnes-Hut | N/P BH | comm per rank, BH ((N/P)^(2/3) + log2 P) |
|---|---|---|---|---|---|---|
{chr(10).join(rows)}

Reading the table: at P = 65,536 the direct method has grown the problem only to N = {N1*math.sqrt(65536):,.0f}
particles but each rank must handle {N1*math.sqrt(65536):,.0f} communicated positions, 256x the single-rank baseline, while BH has reached
N = {bh_N(65536):,.0f} (about {bh_N(65536)/(N1*65536)*100:.0f} % of perfectly linear growth) with per-rank communication not growing at all (it even shrinks slightly because N/P falls as 1/log N).

## 4. Conclusions
* Gustafson's "problem grows with P" is **much weaker** for O(N^2) algorithms: the problem only grows as sqrt(P).
  A user hoping for 1000x more particles gets only ~32x on 1000 processors at constant time.
* The comm/compute ratio gets worse with P for direct (sqrt P) but stays nearly flat for tree codes (log P).
* Algorithmic improvement beats hardware growth: BH on 1 rank at N log N has far lower work than direct at the same N.
* The serial/parallel ratio shifts upward (worse) for direct, flat-ish (log P) for BH.
""")

# ------------------------------ Task 19 ------------------------------
Tc, s_fixed = 60.0, 0.20           # per-rank compute time (s), fixed serial setup+output time (s)
t_hop, t_msg, t_seed = 50e-6, 5e-6, 2e-6
def row(P):
    # case A: counter-based RNG (O(1) seeding), tree reduction
    RA = t_hop * math.ceil(math.log2(P)) if P > 1 else 0
    TA = Tc + s_fixed + RA
    SA = (P * Tc + s_fixed) / TA
    # case B: sequential seeding (O(P)), linear gather/reduce at root (O(P))
    RB = (t_msg + t_seed) * (P - 1)
    TB = Tc + s_fixed + RB
    SB = (P * Tc + s_fixed) / TB
    aA = (s_fixed + RA) / TA; aB = (s_fixed + RB) / TB
    return f"| {P:,} | {RA*1e3:.3f} | {aA:.5f} | {SA:,.1f} | {SA/P:.4f} | {RB:,.3f} | {aB:.4f} | {SB:,.1f} | {SB/P:.4f} |"
(out / "task19_monte_carlo.md").write_text(f"""# Task 19 - Monte Carlo Path Simulation: The Ideal Weak-Scaling Workload

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

Parameters used: per-rank compute T_c = {Tc:.0f} s; fixed serial setup/output s = {s_fixed} s; t_hop = {t_hop*1e6:.0f} us;
t_msg = {t_msg*1e6:.0f} us; naive seeding {t_seed*1e6:.0f} us per rank. These are **illustrative, not measurements**.

Case A = counter-based RNG + tree reduction. Case B = sequential seeding + linear reduce.

| P | R_tree (ms) | alpha_eff (A) | S (A) | E (A) | seed+linear R (s) | alpha_eff (B) | S (B) | E (B) |
|---|---|---|---|---|---|---|---|---|
{chr(10).join(row(P) for P in (16, 1024, 16384, 262144, 1048576))}

## 4. Analysis
* **Case A:** at one million ranks the tree reduction costs only {t_hop*20*1e3:.0f} ms (20 levels x {t_hop*1e6:.0f} us), far below the
  fixed {s_fixed} s setup/output cost. alpha_eff is dominated by s/T_c (about {s_fixed/(Tc+s_fixed):.4f}), **not** by the reduction. The tree turns the
  P-dependent term into a rounding error: this is why log P is tolerated and P is not.
* **Case B:** an O(P) serial phase eventually costs seconds, e.g. {(t_msg+t_seed)*(1048575):,.1f} s at P = 2^20, i.e. {100*(t_msg+t_seed)*1048575/(Tc+s_fixed+(t_msg+t_seed)*1048575):.0f} % of
  the run, so efficiency drops to 0.89 and keeps falling linearly in P: an Amdahl-like ceiling reappears **inside** a weak-scaling workload.
* The dominant practical lever is the constant s (I/O, setup): halving it matters more than optimizing the tree.
* Efficiency E = S/P ~ 1 - alpha_eff, as in Task 04.
* Caveat: weak scaling here buys *throughput* of samples; the statistical error shrinks only as 1/sqrt(P n).
""")
print("done")
