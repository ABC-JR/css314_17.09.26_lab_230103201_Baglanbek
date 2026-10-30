
import csv
import time
from pathlib import Path

import numpy as np


def benchmark_stride(data, stride):
    """Measure sequential memory access with a given stride."""

    start = time.perf_counter_ns()

    total = np.sum(data[::stride], dtype=np.float64)

    end = time.perf_counter_ns()

    elapsed_ns = end - start
    elements_touched = len(data[::stride])

    latency = elapsed_ns / elements_touched

    return elapsed_ns, elements_touched, latency, float(total)


def main():
    project_root = Path(__file__).resolve().parent.parent
    results_dir = project_root / "results"
    results_dir.mkdir(exist_ok=True)

    # Allocate 2^24 double-precision elements (~128 MiB)
    data = np.ones(16_777_216, dtype=np.float64)

    strides = [1, 2, 4, 8, 16, 32, 64, 128]

    results = []

    for stride in strides:
        print(f"Benchmarking stride={stride}...")

        # 5 warmup iterations
        for _ in range(5):
            benchmark_stride(data, stride)

        # 5 recorded iterations
        measurements = []

        for _ in range(5):
            measurements.append(benchmark_stride(data, stride))

        median_time = float(np.median(
            [item[0] for item in measurements]
        ))

        elements_touched = measurements[0][1]

        latency = median_time / elements_touched

        checksum = measurements[0][3]

        results.append({
            "stride": stride,
            "elements_touched": elements_touched,
            "median_time_ns": int(median_time),
            "latency_ns_per_element": latency,
            "checksum": checksum
        })

        print(
            f"Stride: {stride}, "
            f"Latency: {latency:.4f} ns/element"
        )

    # Save TSV
    output_file = results_dir / "stride_results.tsv"

    with open(output_file, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys(),
            delimiter="\t"
        )

        writer.writeheader()
        writer.writerows(results)

    print(f"\nResults saved to: {output_file}")

    print("\nBenchmark summary:")

    for result in results:
        print(
            f"Stride {result['stride']:3}: "
            f"{result['latency_ns_per_element']:.4f} ns/element"
        )


if __name__ == "__main__":
    main()
