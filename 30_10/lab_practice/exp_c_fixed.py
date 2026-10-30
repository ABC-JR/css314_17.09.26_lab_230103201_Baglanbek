
import time
from multiprocessing import Pool


def local_counter(increments):

    counter = 0

    for _ in range(increments):
        counter += 1

    return counter


def run_experiment(workers, total_increments=20_000_000):
    increments_per_worker = total_increments // workers

    start_time = time.perf_counter()

    with Pool(processes=workers) as pool:
        results = pool.map(
            local_counter,
            [increments_per_worker] * workers
        )


    total = sum(results)

    runtime = time.perf_counter() - start_time

    print(f"Counter: {total}")
    print(f"Expected: {total_increments}")

    return runtime


if __name__ == "__main__":
    worker_counts = [1, 2, 4]
    runtimes = {}

    print("EXPERIMENT C: PRIVATIZATION")
    print("=" * 45)

    for workers in worker_counts:
        print(f"\nRunning with P={workers}...")

        runtime = run_experiment(workers)
        runtimes[workers] = runtime

        print(f"Runtime: {runtime:.3f} seconds")

    t1 = runtimes[1]

    print("\nRESULTS")
    print("=" * 45)

    for workers in worker_counts:
        tp = runtimes[workers]
        speedup = t1 / tp

        if workers == 1:
            efficiency = "N/A"
        else:
            efficiency = (
                (workers * tp / t1 - 1) / (workers - 1)
            )

        print(
            f"P={workers} | "
            f"Runtime={tp:.3f}s | "
            f"Speedup={speedup:.3f} | "
            f"Karp-Flatt={efficiency}"
        )
