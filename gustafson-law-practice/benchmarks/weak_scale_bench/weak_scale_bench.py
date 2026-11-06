#!/usr/bin/env python3
"""Task 22 - Empirical weak-scaling benchmark (Python multiprocessing).

Workload: midpoint-rule integration of 4/(1+x^2) on [0,1]  (= pi), plus a small
fixed *serial* phase that does not grow with the problem (stand-in for setup / I/O).

Weak scaling: each of P workers integrates k intervals, so the total problem has n = P*k
intervals and the parallel wall-clock time should stay ~constant if alpha is small.

For every P and every run we time
  t_parallel : serial phase + pool start-up + P workers x k intervals + reduction
  t_serial   : serial phase + ONE process integrating all P*k intervals
Scaled speedup is then S(P) = t_serial / t_parallel  (the actual Gustafson definition:
time the one-processor machine would need for the scaled problem).

Usage
  python3 weak_scale_bench.py                        # P = 1,2,4,... up to os.cpu_count()
  python3 weak_scale_bench.py --threads 1 2 4 8 --runs 5 --k 100000000
  python3 weak_scale_bench.py --out ../results.csv
"""
import argparse, csv, math, os, statistics, sys, time
import multiprocessing as mp

import numpy as np

CHUNK = 32_768  # 256 KB per temporary array: stays cache-resident, so the kernel is compute-bound, not DRAM-bound


def serial_phase(m):
    """Fixed-size serial work, independent of P and k (python loop: cannot be vectorized away)."""
    x = 0.0
    for i in range(m):
        x += (i % 7) * 1e-12
    return x


def integrate(args):
    """Midpoint rule for intervals [start, start+count) of n total intervals."""
    start, count, n = args
    h = 1.0 / n
    total = 0.0
    done = 0
    while done < count:
        c = min(CHUNK, count - done)
        x = (np.arange(start + done, start + done + c, dtype=np.float64) + 0.5) * h
        total += float(np.sum(4.0 / (1.0 + x * x)))
        done += c
    return total * h


def run_parallel(P, k, m):
    t0 = time.perf_counter()
    serial_phase(m)
    n = P * k
    jobs = [(i * k, k, n) for i in range(P)]
    if P == 1:
        res = [integrate(jobs[0])]
        # P=1: no pool, identical to serial baseline (so S(1) = 1 exactly in expectation)
    else:
        with mp.Pool(processes=P) as pool:
            res = pool.map(integrate, jobs, chunksize=1)
    val = math.fsum(res)
    return time.perf_counter() - t0, val


def run_serial(P, k, m):
    t0 = time.perf_counter()
    serial_phase(m)
    val = integrate((0, P * k, P * k))
    return time.perf_counter() - t0, val


def default_threads():
    mx = os.cpu_count() or 1
    ts, p = [], 1
    while p < mx:
        ts.append(p)
        p *= 2
    ts.append(mx)
    return ts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--threads", type=int, nargs="*", default=None, help="worker counts (default: powers of 2 up to cpu_count)")
    ap.add_argument("--runs", type=int, default=5, help="independent runs per configuration")
    ap.add_argument("--k", type=int, default=100_000_000, help="intervals per worker (kept constant: weak scaling)")
    ap.add_argument("--serial-work", type=int, default=500_000, help="iterations of the fixed serial phase")
    ap.add_argument("--out", default="results.csv")
    ap.add_argument("--no-warmup", action="store_true")
    a = ap.parse_args()
    threads = a.threads or default_threads()
    print(f"cpu_count={os.cpu_count()}  threads={threads}  k={a.k:,}  runs={a.runs}", flush=True)
    if len(threads) < 5:
        print("WARNING: fewer than 5 distinct thread counts; Task 23 needs >= 5.", file=sys.stderr)
    if max(threads) > (os.cpu_count() or 1):
        print("WARNING: more workers than hardware threads -> oversubscription; "
              "results will not show scaling.", file=sys.stderr)
    if not a.no_warmup:
        run_parallel(1, a.k // 10, a.serial_work)
    rows = []
    for P in threads:
        for r in range(1, a.runs + 1):
            tp, vp = run_parallel(P, a.k, a.serial_work)
            ts, vs = run_serial(P, a.k, a.serial_work)
            err = max(abs(vp - math.pi), abs(vs - math.pi))
            rows.append((P, r, tp, ts, err))
            print(f"P={P:3d} run={r}  t_par={tp:8.4f}s  t_ser={ts:8.4f}s  S={ts/tp:6.3f}  |pi err|={err:.1e}", flush=True)
    with open(a.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["P", "run", "t_parallel_s", "t_serial_baseline_s", "abs_error_vs_pi"])
        for row in rows:
            w.writerow([row[0], row[1], f"{row[2]:.6f}", f"{row[3]:.6f}", f"{row[4]:.3e}"])
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
