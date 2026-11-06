# Task 09 - Multi-Component Workload

| Phase | Share of parallel run time | Classification |
|---|---|---|
| A: disk I/O + parameter broadcast | 2 % | serial (single-stream I/O; broadcast does not shrink with work) |
| B: boundary message passing | 6 % | serial **in the conservative model** (see caveat) |
| C: domain flux computation | 92 % | parallel |

Shares sum to 100 %, as required (they are fractions of the P-core run, Gustafson's frame).

## Case 1 - conservative (A + B serial): alpha = 0.02 + 0.06 = 0.08
| P | S(P) | E(P) |
|---|---|---|
| 512 | 471.12 | 0.9202 |
| 2,048 | 1884.24 | 0.9200 |

Check: 512 - 0.08 x 511 = 512 - 40.88 = 471.12;  2048 - 0.08 x 2047 = 2048 - 163.76 = 1884.24

## Case 2 - optimistic (only A serial): alpha = 0.02
| P | S(P) | E(P) |
|---|---|---|
| 512 | 501.78 | 0.9800 |
| 2,048 | 2007.06 | 0.9800 |

## Caveat to put in your write-up
Boundary exchange (B) is parallel *communication*, not a serial section: every rank does it
concurrently and, with a constant per-rank subdomain, its cost stays roughly constant (Task 17).
Treating it as alpha is a valid "overhead lumping" and gives a lower bound. The defensible range is
**471-502 at P=512 and 1884-2007 at P=2048**. B becomes a real scalability concern only if
latency/contention make it grow with P (Task 12).
