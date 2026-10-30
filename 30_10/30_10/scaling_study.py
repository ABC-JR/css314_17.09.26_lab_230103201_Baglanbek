
import csv
import json
import math
import multiprocessing as mp
import statistics
from multiprocessing import shared_memory
from pathlib import Path
from time import perf_counter_ns

import numpy as np
import psutil


# Shared worker state
_input_shm = None
_output_shm = None
_input_array = None
_output_array = None


def initialize_worker(input_name, output_name, shape):
    """Attach each worker to shared input and output matrices."""
    global _input_shm, _output_shm
    global _input_array, _output_array

    _input_shm = shared_memory.SharedMemory(name=input_name)
    _output_shm = shared_memory.SharedMemory(name=output_name)

    _input_array = np.ndarray(
        shape, dtype=np.float64, buffer=_input_shm.buf
    )

    _output_array = np.ndarray(
        shape, dtype=np.float64, buffer=_output_shm.buf
    )


def stencil_worker(row_range):
    """Calculate stencil values for a range of rows."""
    start, end = row_range

    _output_array[start:end, 1:-1] = (
        _input_array[start - 1:end - 1, 1:-1]
        + _input_array[start + 1:end + 1, 1:-1]
        + _input_array[start:end, :-2]
        + _input_array[start:end, 2:]
    ) * 0.25

    return end - start


def create_chunks(n, processes):
    """Partition interior rows into approximately equal chunks."""
    interior_rows = n - 2

    if interior_rows < processes:
        raise ValueError("Matrix is too small for this process count")

    boundaries = np.linspace(
        1, n - 1, processes + 1, dtype=int
    )

    return [
        (int(boundaries[i]), int(boundaries[i + 1]))
        for i in range(processes)
    ]


def run_study(matrix, processes, repeats):
    """Run a stencil benchmark using shared memory."""

    n = matrix.shape[0]

    input_shm = shared_memory.SharedMemory(
        create=True, size=matrix.nbytes
    )

    output_shm = shared_memory.SharedMemory(
        create=True, size=matrix.nbytes
    )

    input_shared = np.ndarray(
        matrix.shape, dtype=np.float64, buffer=input_shm.buf
    )

    output_shared = np.ndarray(
        matrix.shape, dtype=np.float64, buffer=output_shm.buf
    )

    input_shared[:] = matrix
    output_shared[:] = 0.0

    chunks = create_chunks(n, processes)
    measurements = []

    try:
        # Pool startup and shared-memory attachment are excluded
        # from the kernel timing.
        with mp.Pool(
            processes=processes,
            initializer=initialize_worker,
            initargs=(
                input_shm.name,
                output_shm.name,
                matrix.shape
            )
        ) as pool:

            # Warmup
            pool.map(stencil_worker, chunks)

            # Recorded runs
            for _ in range(repeats):
                start = perf_counter_ns()

                pool.map(stencil_worker, chunks)

                elapsed = perf_counter_ns() - start
                measurements.append(elapsed)

        result = output_shared.copy()

    finally:
        input_shm.close()
        output_shm.close()

        input_shm.unlink()
        output_shm.unlink()

    return statistics.median(measurements), result


def calculate_amdahl(t1, tp, processes):
    if processes <= 1:
        return None

    speedup = t1 / tp

    return (
        (1.0 / speedup) - (1.0 / processes)
    ) / (1.0 - (1.0 / processes))


def reference_stencil(matrix):
    """Single-process NumPy reference."""
    result = np.zeros_like(matrix)

    result[1:-1, 1:-1] = (
        matrix[:-2, 1:-1]
        + matrix[2:, 1:-1]
        + matrix[1:-1, :-2]
        + matrix[1:-1, 2:]
    ) * 0.25

    return result


def main():
    root = Path(__file__).resolve().parent.parent
    results_dir = root / "results"
    results_dir.mkdir(exist_ok=True)

    # Read Milestone 0 parameters
    with open(
        results_dir / "salted_params.json",
        "r",
        encoding="utf-8"
    ) as file:
        params = json.load(file)

    N = params["N"]
    seed = params["seed"]

    # Physical cores only
    physical_cores = psutil.cpu_count(logical=False) or 1

    process_counts = []
    p = 1

    while p <= physical_cores:
        process_counts.append(p)
        p *= 2

    if process_counts[-1] != physical_cores:
        process_counts.append(physical_cores)

    # Remove duplicates and sort
    process_counts = sorted(set(process_counts))

    repeats = 3

    print("Strong and Weak Scaling Study")
    print("Salted N:", N)
    print("Physical cores:", physical_cores)
    print("Process counts:", process_counts)

    rng = np.random.default_rng(seed)

    # ==========================================
    # STRONG SCALING
    # ==========================================

    print("\n========== STRONG SCALING ==========")

    strong_matrix = rng.random((N, N), dtype=np.float64)

    strong_reference = reference_stencil(strong_matrix)

    strong_results = {}

    for processes in process_counts:

        runtime, output = run_study(
            strong_matrix, processes, repeats
        )

        if not np.allclose(
            output, strong_reference,
            rtol=1e-12, atol=1e-12
        ):
            raise RuntimeError(
                f"Strong scaling validation failed for P={processes}"
            )

        strong_results[processes] = runtime

        print(
            f"P={processes}: "
            f"{runtime / 1e9:.6f} seconds"
        )

    t1_strong = strong_results[1]

    # ==========================================
    # WEAK SCALING
    # ==========================================

    print("\n========== WEAK SCALING ==========")

    weak_results = {}

    for processes in process_counts:

        dimension = math.ceil(N * math.sqrt(processes))

        weak_matrix = rng.random(
            (dimension, dimension),
            dtype=np.float64
        )

        runtime, output = run_study(
            weak_matrix, processes, repeats
        )

        weak_reference = reference_stencil(weak_matrix)

        if not np.allclose(
            output, weak_reference,
            rtol=1e-12, atol=1e-12
        ):
            raise RuntimeError(
                f"Weak scaling validation failed for P={processes}"
            )

        weak_results[processes] = {
            "runtime": runtime,
            "dimension": dimension
        }

        print(
            f"P={processes}, N={dimension}: "
            f"{runtime / 1e9:.6f} seconds"
        )

    # ==========================================
    # METRICS
    # ==========================================

    rows = []

    work_1 = (N - 2) ** 2

    serial_fractions = []

    for processes in process_counts:

        strong_time = strong_results[processes]

        strong_speedup = t1_strong / strong_time

        strong_efficiency = (
            strong_speedup / processes
        ) * 100.0

        serial_fraction = calculate_amdahl(
            t1_strong, strong_time, processes
        )

        if serial_fraction is not None:
            serial_fractions.append(serial_fraction)

        weak = weak_results[processes]

        weak_time = weak["runtime"]
        weak_n = weak["dimension"]

        work_p = (weak_n - 2) ** 2

        scaled_speedup = (
            processes * work_1 * t1_strong
        ) / (work_p * weak_time)

        rows.append({
            "processes": processes,
            "strong_dimension": N,
            "strong_time_ns": strong_time,
            "strong_speedup": strong_speedup,
            "strong_efficiency_percent": strong_efficiency,
            "amdahl_serial_fraction": serial_fraction,
            "weak_dimension": weak_n,
            "weak_time_ns": weak_time,
            "weak_work_cells": work_p,
            "weak_scaled_speedup": scaled_speedup
        })

    # Mean empirical serial fraction across P > 1
    avg_serial = (
        statistics.mean(serial_fractions)
        if serial_fractions else None
    )

    theoretical_max = (
        1.0 / avg_serial
        if avg_serial is not None and avg_serial > 0
        else None
    )

    # ==========================================
    # SAVE TSV
    # ==========================================

    output_tsv = results_dir / "scaling_metrics.tsv"

    with open(
        output_tsv,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys(),
            delimiter="\t"
        )

        writer.writeheader()
        writer.writerows(rows)

    # ==========================================
    # ROOFLINE ANALYSIS
    # ==========================================

    # Four additions and one multiplication = 5 FLOPs
    # per output cell.
    #
    # Conservative traffic:
    # Four float64 reads + one float64 write = 40 bytes.
    #
    # Ideal reuse:
    # One float64 input read + one float64 output write = 16 bytes.

    flops_per_cell = 5
    conservative_bytes = 40
    ideal_bytes = 16

    ai_conservative = flops_per_cell / conservative_bytes
    ai_ideal = flops_per_cell / ideal_bytes

    with open(
        results_dir / "host_profile.json",
        "r",
        encoding="utf-8"
    ) as file:
        host = json.load(file)

    cache = host.get("cache", {})

    roofline = {
        "kernel": "2D five-point stencil",
        "floating_point_operations_per_cell": flops_per_cell,
        "conservative_bytes_per_cell": conservative_bytes,
        "ideal_bytes_per_cell": ideal_bytes,
        "arithmetic_intensity_flops_per_byte": {
            "conservative": ai_conservative,
            "ideal_with_cache_reuse": ai_ideal
        },
        "cache_sizes": cache,
        "cpu_model": host["cpu"]["model_name"],
        "physical_cores": physical_cores,
        "peak_memory_bandwidth_gb_s": None,
        "bandwidth_note": (
            "Not measured. Exact peak bandwidth requires "
            "verified memory type, channel count and transfer rate."
        ),
        "likely_regime": "Memory-bandwidth sensitive",
        "classification_note": (
            "Low arithmetic intensity suggests memory sensitivity. "
            "A definitive Roofline classification requires measured "
            "sustained memory bandwidth and CPU peak FLOPs."
        ),
        "amdahl": {
            "mean_empirical_serial_fraction": avg_serial,
            "theoretical_max_speedup": theoretical_max
        }
    }

    output_json = results_dir / "roofline_summary.json"

    with open(
        output_json,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(roofline, file, indent=4)

    print("\n========== FINAL SUMMARY ==========")

    print("Mean Amdahl serial fraction:", avg_serial)
    print("Theoretical maximum speedup:", theoretical_max)

    print("Arithmetic intensity (conservative):", ai_conservative)
    print("Arithmetic intensity (ideal):", ai_ideal)

    print("\nSaved:", output_tsv)
    print("Saved:", output_json)


if __name__ == "__main__":
    mp.freeze_support()
    main()
