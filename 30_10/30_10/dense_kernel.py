
import json
import time
from pathlib import Path

import numpy as np
from numba import njit


@njit
def naive_ijk(A, B, C, M):
    """Algorithm A: i-j-k loop order."""

    C.fill(0.0)

    for i in range(M):
        for j in range(M):
            total = 0.0

            for k in range(M):
                total += A[i, k] * B[k, j]

            C[i, j] = total


@njit
def interchanged_ikj(A, B, C, M):
    """Algorithm B: i-k-j loop order."""

    C.fill(0.0)

    for i in range(M):
        for k in range(M):

            # Load A[i, k] once
            a = A[i, k]

            # Sequential access to B and C rows
            for j in range(M):
                C[i, j] += a * B[k, j]


def measure_runtime(function, A, B, C, M):
    """Measure function execution time in nanoseconds."""

    start = time.perf_counter_ns()

    function(A, B, C, M)

    end = time.perf_counter_ns()

    return end - start


def main():
    project_root = Path(__file__).resolve().parent.parent

    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)

    # Read salted parameters
    salt_file = results_dir / "salted_params.json"

    with open(salt_file, "r", encoding="utf-8") as file:
        params = json.load(file)

    N = params["N"]
    seed = params["seed"]

    # Execute on half-size sub-block
    M = N // 2

    print(f"Salted N: {N}")
    print(f"Benchmark matrix size M: {M}")
    print(f"Random seed: {seed}")

    # Generate deterministic matrices
    rng = np.random.default_rng(seed)

    A = rng.random((M, M), dtype=np.float64)
    B = rng.random((M, M), dtype=np.float64)

    C_naive = np.zeros((M, M), dtype=np.float64)
    C_interchanged = np.zeros((M, M), dtype=np.float64)

    # Compile both functions before measurement
    print("\nCompiling Numba functions...")

    naive_ijk(A, B, C_naive, M)
    interchanged_ikj(A, B, C_interchanged, M)

    # Verify correctness
    if not np.allclose(
        C_naive,
        C_interchanged,
        rtol=1e-10,
        atol=1e-10
    ):
        raise RuntimeError("Algorithm results do not match!")

    print("Correctness check passed!")

    naive_times = []
    interchanged_times = []

    # Three recorded benchmark runs
    for run in range(3):
        print(f"\nRun {run + 1}/3")

        naive_time = measure_runtime(
            naive_ijk, A, B, C_naive, M
        )

        interchanged_time = measure_runtime(
            interchanged_ikj, A, B, C_interchanged, M
        )

        naive_times.append(naive_time)
        interchanged_times.append(interchanged_time)

        print(f"Naive i-j-k: {naive_time / 1e9:.4f} seconds")
        print(f"Interchanged i-k-j: {interchanged_time / 1e9:.4f} seconds")

    # Calculate median runtime
    naive_median = float(np.median(naive_times))
    interchanged_median = float(np.median(interchanged_times))

    # Calculate speedup
    speedup = naive_median / interchanged_median

    output = {
        "N": N,
        "M": M,
        "seed": seed,
        "matrix_dtype": "float64",
        "algorithm_a": {
            "name": "naive_ijk",
            "loop_order": "i-j-k",
            "runtime_ns": naive_times,
            "median_runtime_ns": naive_median
        },
        "algorithm_b": {
            "name": "interchanged_ikj",
            "loop_order": "i-k-j",
            "runtime_ns": interchanged_times,
            "median_runtime_ns": interchanged_median
        },
        "speedup": speedup,
        "correctness_check": "passed"
    }

    # Save JSON
    output_file = results_dir / "loop_interchange.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=4)

    print("\n========== RESULTS ==========")

    print(f"Naive median: {naive_median / 1e9:.4f} seconds")
    print(f"Interchanged median: {interchanged_median / 1e9:.4f} seconds")
    print(f"Speedup: {speedup:.4f}x")

    print(f"\nResults saved to: {output_file}")


if __name__ == "__main__":
    main()
