# Task 20 - Parallel Graph Traversal and Irregular Workloads

## Why regular dense kernels weak-scale and graphs do not
Dense GEMM or a stencil have: fixed work per rank, predictable access, balanced loads, surface-to-volume communication
(Task 16/17). BFS and PageRank on power-law graphs break each of these premises.

| Gustafson premise | Dense LA / stencil | BFS / PageRank on power-law graphs |
|---|---|---|
| Work per rank is balanced | yes, by geometry | no: hub vertices with degree ~10^5-10^6 concentrate edges; random vertex partitioning balances vertices, not edges |
| Work per rank per step constant | yes | BFS frontier size swings by orders of magnitude between levels (tiny, then ~30-50 % of the graph, then tiny) |
| Communication ~ surface, local | yes (neighbour halos) | small-world graph has **no good partition**: edge cut stays a large fraction of E, so communication volume ~ O(E/P x cut fraction) per rank and goes to *all* ranks |
| Memory access predictable, high arithmetic intensity | blocking, prefetch, cache reuse | pointer chasing, ~1 flop per cache line or fewer; latency/bandwidth bound, no reuse |
| Number of synchronous steps fixed | iteration count independent of size (stencil) | BFS levels ~ diameter ~ O(log N) for small-world graphs (grows slowly) with a global barrier per level |
| Serial fraction constant | yes | frontier/termination checks (allreduce each level), load-balancing metadata, degree-sorted preprocessing: alpha grows |
| Compute dominates | yes | communication and memory latency dominate; TEPS is the metric, not flops |

## Specific failure modes
1. **Frontier imbalance.** At a given level some ranks hold most of the frontier, so time per level is set by the slowest rank (max not mean): idle time is effectively serial.
2. **Hub contention.** Updating a high-degree vertex's state (atomics in shared memory; many-to-one messages in distributed) serializes.
3. **Irregular memory access.** Each edge traversal is a random access (cache miss, TLB miss); performance scales with memory-system *concurrency* (outstanding requests), not core count, and saturates memory controllers.
4. **Data-dependent synchronization.** Level-synchronous BFS needs a barrier and a global "is the frontier empty?" reduction every level: alpha grows with the number of levels, and graph diameter does not shrink as the graph grows.
5. **Weak scaling definition is ambiguous.** Growing a graph by 2x vertices at fixed average degree changes the degree distribution tail (max degree grows), so work per rank is not truly "constant"; with Graph500's R-MAT generator at edge factor 16 the structure changes with scale.
6. **PageRank**: each iteration is a sparse matrix-vector product with a global exchange of rank values; iteration count to a tolerance is roughly size-independent (good), but the SpMV communication is an irregular all-to-all-ish pattern (bad).

## What practitioners do about it
* 2D (edge-based) partitioning instead of 1D vertex partitioning: communication ~ O(N/sqrt(P)) rather than O(N).
* Direction-optimizing BFS (top-down for small frontiers, bottom-up for huge ones) to cut work.
* Degree-aware delegation of hub vertices; vertex reordering; communication aggregation and message coalescing; asynchronous / bulk-asynchronous traversal; one-sided RDMA operations.
* Measure TEPS and report **weak-scaling efficiency of time**, not only speedup (cf. Task 13).

## Verdict
Gustafson's law is a good model when the parallel part is *regular* and the serial part is *constant*. Power-law graph analytics violates
balance, constant per-step work, locality, and constant synchronization count simultaneously. The result: weak-scaling efficiency can
degrade markedly at large scale (how much depends on graph, partitioning and machine; measure it), and the effective alpha(P) grows with P, so the
modified models of Task 12 and the isoefficiency view of Task 14 are the right tools.
