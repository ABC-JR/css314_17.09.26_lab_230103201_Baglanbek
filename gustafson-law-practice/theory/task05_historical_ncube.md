# Task 05 - The nCUBE 10 Experiment and the "Amdahl's Pessimism" Fallacy

> **Citation warning.** I reconstructed this from memory and have no database access here. Verify the figures
> against the primary sources: J. L. Gustafson, G. R. Montry, R. E. Benner, "Development of Parallel Methods
> for a 1024-Processor Hypercube," SIAM J. Sci. Stat. Comput. 9(4), 1988; and J. L. Gustafson, "Reevaluating Amdahl's Law," CACM 31(5), 1988.

## Context
* In the 1980s, Amdahl's argument (1967) was widely read as proof that massive parallelism was futile:
  a 1 % serial fraction caps speedup at 100, so 1000 processors seemed absurd. Some prominent claims suggested
  speedup beyond a few tens was unrealistic.
* Researchers at Sandia National Laboratories (Gustafson, Montry, Benner) had a 1024-node nCUBE/ten hypercube
  with distributed memory (about 512 KB per node) and ran three real applications.

## The experiments (as I recall them; check exact figures)
Three production-style codes: (1) beam strain analysis (finite elements), (2) surface wave simulation (finite
differences), (3) unstable fluid flow through a channel (flux-corrected transport). They were reported with
scaled speedups of roughly 1000+ on 1024 processors, i.e. efficiency above 97-99 %.

## Why Amdahl "forbids" this
If the serial fraction were s = 0.004 (0.4 %) on the *fixed* problem:
  S_A(1024) = 1 / (0.004 + 0.996/1024) = 1 / 0.004973 = 201.
Observed ~1000 is five times the "ceiling" at that P.

## How problem expansion removes the ceiling
1. The authors did not shrink a fixed problem; they gave each processor a fixed-size subdomain, so the
   problem grew in step with P (fixed time, not fixed size).
2. The serial part (set-up, I/O, global coordination) is roughly independent of problem size, so its
   share of the 1024-node run was tiny: s + p = 1 with s ~ 0.004.
3. Applying Gustafson's formula: S = 1024 - 0.004 x 1023 = 1024 - 4.092 = **1019.9**. This matches the
   order of what was measured.
4. The one-processor memory (~512 KB) could not even hold the scaled problem, so the one-core baseline
   could not be measured directly. The speedup was estimated by timing serial phases and extrapolating. This is a legitimate but model-dependent method, and a point to mention critically.

## Lessons
* Amdahl's Law is correct for fixed-size problems. The error was in applying it to **all** uses of a parallel machine.
* The serial fraction depends on problem size; as W grows, the parallel part grows faster than the serial part.
* The key conceptual step: **measure the serial fraction on the parallel run**, not the single-processor run.
* Limitations (honest): the three codes had regular, nearest-neighbour communication - the friendly case (Task 17).
  Irregular codes (Task 20) did not repeat this success, and the estimated-baseline method has been criticized.
