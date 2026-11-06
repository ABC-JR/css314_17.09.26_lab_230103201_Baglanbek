# Task 02 - Formal Derivation of Scaled Speedup

## Setup and notation
Run the scaled problem on P processors.
* s = serial time on the parallel machine; p = time spent in the parallel phase (all P busy).
* Normalize: **s + p = 1** (the whole P-processor run takes one time unit). Then alpha = s and p = 1 - alpha.

## Step 1 - Time on the P-processor machine
T_P = s + p = 1.                                            (normalization, line 1)

## Step 2 - Work done during the parallel phase
During p, each of P processors does p time units of work. Total parallel work, measured in
single-processor time units, is **pP**.                     (line 2: P identical processors, perfect balance)

## Step 3 - Equivalent serial time
One processor must perform the serial part once (s) and all of the parallel work (pP):
T_1 = s + pP.                                               (line 3)

Why s appears once and not P times: the serial section is a fixed amount of work (setup, I/O, a
reduction) that does not grow with the problem; one processor performs it exactly as the parallel machine does.
This is the key assumption of the law.

## Step 4 - Scaled speedup
S(P) = T_1 / T_P = (s + pP) / 1 = **s + pP**.                (line 4: the target formula)

## Step 5 - Rewrite in terms of alpha
Substitute s = alpha and p = 1 - alpha:
S(P) = alpha + (1 - alpha)P
     = alpha + P - alpha P
     = P - alpha P + alpha
     = **P - alpha(P - 1)**.                                (line 5)

## Step 6 - Sanity checks
* P = 1: S = 1 - 0 = 1. Correct.
* alpha = 0: S = P. Perfect scaling.
* alpha = 1: S = P - (P-1) = 1. Nothing parallelizes.
* dS/dP = 1 - alpha > 0: linear growth, no ceiling.

## Step 7 - Efficiency
E(P) = S/P = 1 - alpha(P-1)/P = 1 - alpha + alpha/P.

## Assumptions to list in your own write-up
1. Parallel phase scales to P perfectly (no load imbalance, no communication inside p).
2. Serial time s is independent of problem size.
3. The problem can be enlarged to fill the P-processor run, at ~constant per-processor work.
4. The single-processor "equivalent" run is hypothetical (memory and cache effects are ignored).
