
import time
from multiprocessing import Process, Value, Lock


def increment_counter(counter, lock, increments):

    for _ in range(increments):
        with lock:
            counter.value += 1


def run_experiment(workers, total_increments=2_000_000):
    counter = Value('i', 0, lock=False)
    lock = Lock()

    increments_per_worker = total_increments // workers

    processes = []

    start_time = time.perf_counter()

    for _ in range(workers):
        process = Process(
            target=increment_counter,
            args=(counter, lock, increments_per_worker)
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    runtime = time.perf_counter() - start_time

    # Проверяем правильность результата
    print(f"Counter: {counter.value}")
    print(f"Expected: {total_increments}")

    return runtime


if __name__ == "__main__":
    worker_counts = [1, 2, 4]
    runtimes = {}

    print("EXPERIMENT B: LOCK CONTENTION")
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
