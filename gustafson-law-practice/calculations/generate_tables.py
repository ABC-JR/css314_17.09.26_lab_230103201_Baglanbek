#!/usr/bin/env python3
"""Generates the numeric Markdown deliverables for Tasks 06-10, 16, 17.
Run:  python3 calculations/generate_tables.py   (from repo root)
All numbers in the .md files come from this script, not hand arithmetic."""
import math, pathlib
out = pathlib.Path(__file__).parent

def S_g(P, a): return P - a * (P - 1)
def E_g(P, a): return S_g(P, a) / P
def S_a(P, s): return 1.0 / (s + (1 - s) / P)

# ---------------- Task 06 ----------------
a = 0.04
rows = "\n".join(f"| {P:,} | {S_g(P,a):,.4f} | {E_g(P,a):.6f} | {1-E_g(P,a):.6f} |"
                 for P in (16, 64, 256, 1024, 4096, 16384))
(out / "task06_parametric_table.md").write_text(f"""# Task 06 - Parametric Speedup, alpha = 0.04

Formulas: S(P) = P - alpha(P-1); E(P) = S(P)/P = 1 - alpha(P-1)/P.

| P | S(P) | E(P) | Efficiency lost 1-E |
|---|---|---|---|
{rows}

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
""")

# ---------------- Task 07 ----------------
P, Sreq = 8192, 7500
amax = (P - Sreq) / (P - 1)
(out / "task07_tolerable_serial.md").write_text(f"""# Task 07 - Maximum Tolerable Serial Fraction

Given P = {P:,}, requirement S(P) >= {Sreq:,}.

## Derivation
S(P) = P - alpha(P-1) >= S_req
-alpha(P-1) >= S_req - P
alpha(P-1) <= P - S_req          (multiply by -1, inequality flips)
alpha <= (P - S_req)/(P - 1)

## Numeric result
alpha_max = ({P} - {Sreq}) / ({P} - 1) = {P-Sreq} / {P-1} = **{amax:.6f}**  (~ {100*amax:.3f} %)

## Verification
S(P) at alpha_max = {P} - {amax:.9f} x {P-1} = {S_g(P, amax):.4f}  (exactly {Sreq}).
At alpha = 0.09: S = {S_g(P,0.09):.2f} < {Sreq} -> fails. At alpha = 0.08: S = {S_g(P,0.08):.2f} -> passes.

Implied efficiency floor: E >= {Sreq}/{P} = {Sreq/P:.4f}.
""")

# ---------------- Task 08 ----------------
P, s = 128, 0.08
sa, sg = S_a(P, s), S_g(P, s)
rows = "\n".join(f"| {p:,} | {S_a(p,s):,.3f} | {S_g(p,s):,.3f} | {S_g(p,s)/S_a(p,s):.2f} |"
                 for p in (4, 16, 64, 128, 1024, 16384))
(out / "task08_cross_divergence.md").write_text(f"""# Task 08 - Amdahl vs Gustafson, s = alpha = 0.08, P = 128

## Amdahl (fixed size)
S_A = 1 / (s + (1-s)/P) = 1 / (0.08 + 0.92/128) = 1 / (0.08 + {0.92/128:.6f}) = 1 / {s+0.92/128:.7f} = **{sa:.3f}**
Hard ceiling as P -> inf: 1/s = {1/s:.2f}.

## Gustafson (scaled)
S_G = P - alpha(P-1) = 128 - 0.08 x 127 = 128 - 10.16 = **{sg:.2f}**

## Discrepancy
* Absolute difference: {sg-sa:.2f}
* Gustafson / Amdahl = {sg/sa:.2f}x
* Gustafson is {100*(sg-sa)/sa:.1f} % higher than Amdahl (percentage relative to Amdahl)
* Amdahl is {100*(sg-sa)/sg:.1f} % lower than Gustafson (relative to Gustafson)
State which base you use; the first is the usual "discrepancy" reading.

## Divergence with P
| P | Amdahl | Gustafson | ratio G/A |
|---|---|---|---|
{rows}

## Why they diverge
1. Amdahl holds work fixed: the parallel part shrinks as 1/P until the constant serial time dominates -> bounded by 1/s.
2. Gustafson holds *time* fixed: parallel work grows ~ P, serial time stays constant, so the serial
   share of the **parallel** run stays alpha. Speedup is unbounded, slope (1-alpha).
3. The same numeric value 0.08 means different things: a fraction of the 1-core run (Amdahl) vs a
   fraction of the P-core run (Gustafson). The mapping between them (Task 03) is f = alpha / S_G(P).
   Here f = {s/sg:.5f}, i.e. only {100*s/sg:.2f} % of the 1-core *scaled* run is serial.
""")

# ---------------- Task 09 ----------------
al_full = 0.02 + 0.06; al_min = 0.02
def blk(al):
    return "\n".join(f"| {p:,} | {S_g(p,al):.2f} | {E_g(p,al):.4f} |" for p in (512, 2048))
(out / "task09_multicomponent.md").write_text(f"""# Task 09 - Multi-Component Workload

| Phase | Share of parallel run time | Classification |
|---|---|---|
| A: disk I/O + parameter broadcast | 2 % | serial (single-stream I/O; broadcast does not shrink with work) |
| B: boundary message passing | 6 % | serial **in the conservative model** (see caveat) |
| C: domain flux computation | 92 % | parallel |

Shares sum to 100 %, as required (they are fractions of the P-core run, Gustafson's frame).

## Case 1 - conservative (A + B serial): alpha = 0.02 + 0.06 = 0.08
| P | S(P) | E(P) |
|---|---|---|
{blk(al_full)}

Check: 512 - 0.08 x 511 = 512 - 40.88 = 471.12;  2048 - 0.08 x 2047 = 2048 - 163.76 = 1884.24

## Case 2 - optimistic (only A serial): alpha = 0.02
| P | S(P) | E(P) |
|---|---|---|
{blk(al_min)}

## Caveat to put in your write-up
Boundary exchange (B) is parallel *communication*, not a serial section: every rank does it
concurrently and, with a constant per-rank subdomain, its cost stays roughly constant (Task 17).
Treating it as alpha is a valid "overhead lumping" and gives a lower bound. The defensible range is
**471-502 at P=512 and 1884-2007 at P=2048**. B becomes a real scalability concern only if
latency/contention make it grow with P (Task 12).
""")

# ---------------- Task 10 ----------------
GiB = 1024**3
cap = 32 * GiB
def N_of(nodes, b): return (nodes * cap / b) ** (1/3)
rows = []
for b, label in ((8, "1 double array"), (40, "5 double arrays"), (80, "10 double arrays")):
    for nodes in (1, 64, 512):
        rows.append(f"| {label} ({b} B/pt) | {nodes} | {nodes*32:,} GiB | {N_of(nodes,b):,.0f} | {N_of(nodes,b)**3:.3e} |")
n1 = N_of(1, 8)
(out / "task10_memory_growth.md").write_text(f"""# Task 10 - Memory Ceiling and Maximum 3D Grid Dimension

## Formulation
Weak scaling: W(P) = P W(1). Memory: M(P) = c P, where c = bytes per node actually used.
Per-node cap: 32 GiB = {cap:,} bytes. Aggregate capacity: M_max(P) = 32 GiB x P.

Grid with N^3 points, b bytes per point (b = bytes/array x number of arrays; **state this assumption**):
  b N^3 <= 32 GiB x P  =>  N_max(P) = (32 GiB x P / b)^(1/3) = N_max(1) x P^(1/3)

Per-node subdomain side: n = N/P^(1/3) = (32 GiB / b)^(1/3). For b = 8: n = {n1:,.0f}.

## Results
| Memory per grid point | Nodes | Aggregate memory | N_max | N_max^3 points |
|---|---|---|---|---|
{chr(10).join(rows)}

Headline answer (b = 8 B, one double array): **N_max(64) ~ {N_of(64,8):,.0f}, N_max(512) ~ {N_of(512,8):,.0f}**.

## Observations
* 8x more nodes -> 8x more grid points -> only **2x** larger N (cube root).
* Memory-bound weak scaling is consistent with Gustafson only if work per grid point is constant.
  For a stencil that holds (work ~ N^3 ~ P). For GEMM it does not (Task 16): work grows faster than memory.
* Real solvers need several arrays, halos and buffers; use b = 40-80 B for a more realistic ceiling
  (N_max(512) ~ {N_of(512,40):,.0f}-{N_of(512,80):,.0f}).
""")

# ---------------- Task 16 ----------------
N1 = 1000
rows = "\n".join(
    f"| {p:,} | {p**(1/3):.3f} | {N1*p**(1/3):,.0f} | {(N1*p**(1/3))**2*8/1e6:,.1f} | {(N1*p**(1/3))**2*8/p/1e6:,.2f} | {N1*p**0.5:,.0f} |"
    for p in (1, 8, 64, 512, 4096, 32768))
(out / "task16_gemm_scaling.md").write_text(f"""# Task 16 - Dense GEMM Under Fixed-Time Scaling

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
{rows}

(Multiply memory by 3 for A, B and C.)

## Key consequences
1. Memory per processor *shrinks*: N^2/P = N1^2 P^(-1/3). GEMM is compute-bound, so under fixed
   time memory is **not** the limit (unlike the stencil in Task 10 where memory per node is constant).
2. If you instead fill memory (N ~ sqrt(P)), runtime grows as N^3/P = P^(1/2): fixed-time breaks (Task 11).
3. Communication: 2D algorithms (SUMMA) move ~ N^2/sqrt(P) words per processor. With N ~ P^(1/3):
   N^2/sqrt(P) ~ P^(2/3 - 1/2) = **P^(1/6)**. It grows slowly (4096x more processors -> 4x more
   words per rank), so alpha is not perfectly constant, but the drift is mild.
4. GEMM therefore weak-scales well in the Gustafson sense, with N growing only as the cube root of P.
""")

# ---------------- Task 17 ----------------
n = 128
rows = []
Nfix = 2048
for p in (1, 8, 64, 512, 4096):
    side = round(p ** (1/3))
    Nw = n * side
    ns = Nfix / side
    rows.append(f"| {p:,} | {Nw:,} | {n} | {6*n*n:,} | {6/n:.4f} | {Nfix:,} | {ns:,.0f} | {6/ns:.4f} |")
(out / "task17_stencil_scaling.md").write_text(f"""# Task 17 - 7-point 3D Stencil: Surface-to-Volume Under Weak Scaling

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

## Table (n0 = 128 per-rank block; strong-scaling N fixed at {Nfix})
| P | N (weak) | n (weak) | halo pts/rank (weak) | rho (weak) | N (strong) | n (strong) | rho (strong) |
|---|---|---|---|---|---|---|---|
{chr(10).join(rows)}

## Verdict
The ratio **stays constant** (neither improves nor degrades) under ideal weak scaling; it degrades as P^(1/3) under strong scaling.

## What can still break it (why measured alpha > 0)
* Message **latency**: 6 messages/step regardless of n; matters when n is small.
* Network **hop count / contention** as the machine grows (diameter ~ P^(1/3) on a 3D torus), and
  global reductions (e.g. residual norm) cost O(log P).
* Boundary ranks have fewer neighbours (slightly *less* communication than interior ranks).
* For explicit time stepping the CFL limit forces dt ~ h ~ 1/N, so a fixed *simulated* time needs
  more steps as N grows: constant wall-clock per step is not constant time-to-solution (Task 13).
""")
print("ok")
