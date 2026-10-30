
import time
import math
from multiprocessing import Pool


def heavy_math(n):
    """Perform CPU-intensive mathematical calculations."""
    return sum(
        math.sin(i) * math.cos(i)
        for i in range(1, n)
    )


def run_experiment(workers, total_chunks=16, chunk_size=2_000_000):
    """Run parallel computation with an intentional serial delay."""

    t0 = time.perf_counter()

    # Intentional sequential bottleneck
    time.sleep(0.40)

    with Pool(processes=workers) as pool:
        pool.map(
            heavy_math,
            [chunk_size] * total_chunks
        )

    return time.perf_counter() - t0


if __name__ == "__main__":

    cores = [1, 2, 4]
    runtimes = {}

    print("=" * 60)
    print("EXPERIMENT A: THE STUBBORN SERIAL TAIL")
    print("=" * 60)

    for p in cores:
        print(f"\nRunning experiment with P={p}...")

        runtime = run_experiment(p)
        runtimes[p] = runtime

        print(f"Runtime: {runtime:.3f} seconds")

    t1 = runtimes[1]

    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)

    print(f"{'P':<10}{'Runtime':<15}{'Speedup':<15}{'Karp-Flatt':<15}")

    for p in cores:
        tp = runtimes[p]
        speedup = t1 / tp

        if p == 1:
            print(f"{p:<10}{tp:<15.3f}{speedup:<15.3f}{'N/A':<15}")
        else:
            e = ((p * tp / t1) - 1) / (p - 1)

            print(
                f"{p:<10}"
                f"{tp:<15.3f}"
                f"{speedup:<15.3f}"
                f"{e:<15.3f}"
            )

    print("=" * 60)
