
import sys
import time
import multiprocessing as mp
from multiprocessing import Array

MOD = 1_000_000_007


def collatz_steps(n: int) -> int:
    steps = 0
    while n > 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps


# ---------- Phase 2: Sequential baseline ----------
def run_sequential(N: int):
    max_steps = 0
    checksum = 0
    hits_over_100 = 0

    t0 = time.perf_counter()
    for i in range(1, N + 1):
        s = collatz_steps(i)
        if s > max_steps:
            max_steps = s
        checksum = (checksum + s) % MOD
        if s > 100:
            hits_over_100 += 1
    t1 = time.perf_counter()

    print(f"[SEQ] N={N} max_steps={max_steps} checksum={checksum} "
          f"hits_over_100={hits_over_100} time={t1 - t0:.6f} s")


# ---------- Chunk worker for multiprocessing ----------
def _chunk_worker(args):
    lo, hi = args
    max_steps = 0
    checksum = 0
    for i in range(lo, hi + 1):
        s = collatz_steps(i)
        if s > max_steps:
            max_steps = s
        checksum = (checksum + s) % MOD
    return max_steps, checksum


def _make_static_chunks(N: int, k: int):
    """Divide [1, N] into k roughly equal contiguous chunks (like schedule(static))."""
    chunk_size = N // k
    chunks = []
    start = 1
    for t in range(k):
        end = N if t == k - 1 else start + chunk_size - 1
        chunks.append((start, end))
        start = end + 1
    return chunks


# ---------- Phase 3: Parallel scaling ----------
def run_parallel(N: int, k: int):
    chunks = _make_static_chunks(N, k)

    t0 = time.perf_counter()
    with mp.Pool(processes=k) as pool:
        results = pool.map(_chunk_worker, chunks)
    t1 = time.perf_counter()

    max_steps = max(r[0] for r in results)
    checksum = sum(r[1] for r in results) % MOD

    print(f"[PAR k={k}] N={N} max_steps={max_steps} checksum={checksum} "
          f"time={t1 - t0:.6f} s")


# ---------- Experiment A, Variant 1: shared-memory counter contention ----------
_shared_hit_arr = None  # set inside each worker process by _init_false_sharing_worker


def _init_false_sharing_worker(shared_arr):
    # Runs once per worker process when the Pool starts. This is the
    # Windows-safe way to hand a multiprocessing.Array to workers --
    # passing it through pool.map()'s per-task arguments fails on Windows
    # because Windows uses the 'spawn' start method (no fork), and
    # multiprocessing.Array can only cross into a new process via
    # inheritance at process-creation time, not via pickling per task.
    global _shared_hit_arr
    _shared_hit_arr = shared_arr


def _false_sharing_worker(args):
    lo, hi, idx = args
    local_hits = 0
    for i in range(lo, hi + 1):
        s = collatz_steps(i)
        if s > 100:
            # Writing directly to the shared array on every hit maximizes
            # IPC/synchronization overhead — the closest Python analogy to
            # false sharing, though the mechanism differs from real MESI
            # cache-line contention (see module docstring).
            with _shared_hit_arr.get_lock():
                _shared_hit_arr[idx] += 1
            local_hits += 1
    return local_hits


def run_false_sharing(N: int, k: int):
    chunks = _make_static_chunks(N, k)
    shared_arr = Array('i', k)  # shared memory, one slot per worker

    args = [(lo, hi, idx) for idx, (lo, hi) in enumerate(chunks)]

    t0 = time.perf_counter()
    with mp.Pool(processes=k, initializer=_init_false_sharing_worker,
                 initargs=(shared_arr,)) as pool:
        pool.map(_false_sharing_worker, args)
    t1 = time.perf_counter()

    total = sum(shared_arr)
    print(f"[FALSE_SHARING k={k}] N={N} hits_over_100={total} time={t1 - t0:.6f} s")


# ---------- Experiment A, Variant 2: local counters + reduction at the end ----------
def _reduction_worker(args):
    lo, hi = args
    hits = 0
    for i in range(lo, hi + 1):
        s = collatz_steps(i)
        if s > 100:
            hits += 1  # purely local, no shared memory touched per-hit
    return hits


def run_reduction(N: int, k: int):
    chunks = _make_static_chunks(N, k)

    t0 = time.perf_counter()
    with mp.Pool(processes=k) as pool:
        results = pool.map(_reduction_worker, chunks)
    t1 = time.perf_counter()

    total = sum(results)
    print(f"[REDUCTION k={k}] N={N} hits_over_100={total} time={t1 - t0:.6f} s")


# ---------- Experiment B: scheduling comparison ----------
def _make_dynamic_chunks(N: int, chunk: int):
    """Break [1, N] into small chunks for dynamic-style scheduling."""
    chunks = []
    start = 1
    while start <= N:
        end = min(start + chunk - 1, N)
        chunks.append((start, end))
        start = end + 1
    return chunks


def run_scheduling(N: int, k: int, mode: str, chunk: int):
    if mode == "static":
        chunks = _make_static_chunks(N, k)
    elif mode == "dynamic":
        if chunk <= 0:
            print("dynamic mode requires a positive chunk size", file=sys.stderr)
            sys.exit(1)
        chunks = _make_dynamic_chunks(N, chunk)
    else:
        print(f"Unknown mode: {mode} (use 'static' or 'dynamic')", file=sys.stderr)
        sys.exit(1)

    t0 = time.perf_counter()
    with mp.Pool(processes=k) as pool:
        # imap_unordered lets the pool pull the next chunk as soon as a
        # worker frees up -- analogous to OpenMP's dynamic work queue.
        results = list(pool.imap_unordered(_chunk_worker, chunks))
    t1 = time.perf_counter()

    max_steps = max(r[0] for r in results)
    checksum = sum(r[1] for r in results) % MOD

    print(f"[SCHED mode={mode} chunk={chunk} k={k}] N={N} max_steps={max_steps} "
          f"checksum={checksum} time={t1 - t0:.6f} s")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    N = int(sys.argv[2])

    if cmd == "seq":
        run_sequential(N)
    elif cmd == "par":
        k = int(sys.argv[3])
        run_parallel(N, k)
    elif cmd == "falsesharing":
        k = int(sys.argv[3])
        run_false_sharing(N, k)
    elif cmd == "reduction":
        k = int(sys.argv[3])
        run_reduction(N, k)
    elif cmd == "sched":
        k = int(sys.argv[3])
        mode = sys.argv[4]
        chunk = int(sys.argv[5]) if len(sys.argv) > 5 else 0
        run_scheduling(N, k, mode, chunk)
    else:
        print(f"Unknown command: {cmd}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()