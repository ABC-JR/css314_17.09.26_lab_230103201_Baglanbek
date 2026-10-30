
import ctypes
import csv
import multiprocessing as mp
import statistics
import time
from pathlib import Path


ITERATIONS = 5_000_000
PROCESS_COUNTS = [1, 2, 4, 8]
REPEATS = 3


# ==========================================
# TASK 2.1: UNPADDED
# ==========================================

def worker_unpadded(counter_array, worker_id, iterations):
    for _ in range(iterations):
        counter_array[worker_id] += 1


# ==========================================
# TASK 2.2: PADDED
# ==========================================

def worker_padded(counter_array, worker_id, iterations):
    index = worker_id * 8

    for _ in range(iterations):
        counter_array[index] += 1


# ==========================================
# TASK 2.2: PRIVATIZATION
# ==========================================

def worker_privatized(counter_array, worker_id, iterations):
    local_counter = 0

    for _ in range(iterations):
        local_counter += 1

    # One synchronized write after local computation
    with counter_array.get_lock():
        counter_array[worker_id] = local_counter


# ==========================================
# BENCHMARK RUNNER
# ==========================================

def run_benchmark(strategy, processes, iterations):

    if strategy == "unpadded":
        shared_array = mp.Array(
            ctypes.c_int64,
            processes,
            lock=False
        )
        worker = worker_unpadded

    elif strategy == "padded":
        shared_array = mp.Array(
            ctypes.c_int64,
            processes * 8,
            lock=False
        )
        worker = worker_padded

    elif strategy == "privatized":
        shared_array = mp.Array(
            ctypes.c_int64,
            processes,
            lock=True
        )
        worker = worker_privatized

    else:
        raise ValueError("Unknown strategy")

    jobs = []

    start = time.perf_counter_ns()

    for worker_id in range(processes):
        process = mp.Process(
            target=worker,
            args=(shared_array, worker_id, iterations)
        )

        jobs.append(process)
        process.start()

    for process in jobs:
        process.join()

        if process.exitcode != 0:
            raise RuntimeError(
                f"Worker failed with exit code {process.exitcode}"
            )

    elapsed = time.perf_counter_ns() - start

    # Validate counters
    if strategy == "padded":
        values = [
            shared_array[p * 8]
            for p in range(processes)
        ]
    else:
        values = [
            shared_array[p]
            for p in range(processes)
        ]

    expected = iterations

    if any(value != expected for value in values):
        raise RuntimeError(
            f"Incorrect counter values: {values}"
        )

    return elapsed


# ==========================================
# KARP-FLATT METRIC
# ==========================================

def karp_flatt(t1, tp, p):
    if p <= 1:
        return None

    return ((p * tp / t1) - 1) / (p - 1)


# ==========================================
# MAIN
# ==========================================

def main():

    project_root = Path(__file__).resolve().parent.parent
    results_dir = project_root / "results"

    results_dir.mkdir(exist_ok=True)

    strategies = [
        "unpadded",
        "padded",
        "privatized"
    ]

    results = []

    print("=" * 55)
    print("FALSE SHARING BENCHMARK")
    print("=" * 55)

    print(f"Iterations per worker: {ITERATIONS}")
    print(f"Repeats: {REPEATS}")

    for strategy in strategies:

        print(f"\nStrategy: {strategy}")

        strategy_results = {}

        for processes in PROCESS_COUNTS:

            measurements = []

            for run in range(REPEATS):

                elapsed = run_benchmark(
                    strategy,
                    processes,
                    ITERATIONS
                )

                measurements.append(elapsed)

                print(
                    f"P={processes}, "
                    f"Run={run + 1}, "
                    f"Time={elapsed / 1e9:.4f}s"
                )

            median_time = statistics.median(measurements)

            strategy_results[processes] = median_time

            results.append({
                "strategy": strategy,
                "processes": processes,
                "iterations_per_worker": ITERATIONS,
                "run_1_ns": measurements[0],
                "run_2_ns": measurements[1],
                "run_3_ns": measurements[2],
                "median_time_ns": median_time,
                "karp_flatt": None
            })

        # Calculate Karp-Flatt for P = 2, 4, 8
        t1 = strategy_results[1]

        for row in results:

            if row["strategy"] != strategy:
                continue

            p = row["processes"]

            if p > 1:
                row["karp_flatt"] = karp_flatt(
                    t1,
                    strategy_results[p],
                    p
                )

    # ======================================
    # SAVE TSV
    # ======================================

    output_file = results_dir / "false_sharing_karp_flatt.tsv"

    fieldnames = [
        "strategy",
        "processes",
        "iterations_per_worker",
        "run_1_ns",
        "run_2_ns",
        "run_3_ns",
        "median_time_ns",
        "karp_flatt"
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            delimiter="\t"
        )

        writer.writeheader()
        writer.writerows(results)

    # ======================================
    # SUMMARY
    # ======================================

    print("\n" + "=" * 55)
    print("KARP-FLATT RESULTS")
    print("=" * 55)

    for row in results:

        print(
            f"{row['strategy']:12} "
            f"P={row['processes']} "
            f"Median={row['median_time_ns'] / 1e9:.4f}s "
            f"e(P)={row['karp_flatt']}"
        )

    print(f"\nSaved: {output_file}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
