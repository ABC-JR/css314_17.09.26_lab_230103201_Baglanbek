from concurrent.futures import ThreadPoolExecutor
import threading
import time
import numpy as np
import csv

SQRT_COUNT = 10_000_000

def worker_task_numpy(thread_id: int, team_size: int):
    native_tid = threading.get_native_id()
    arr = np.arange(SQRT_COUNT, dtype=np.float64)
    result = np.sqrt(arr).sum()  # GIL released during this C-level call
    return native_tid, result

def run_team(num_threads: int):
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_task_numpy, tid, num_threads) for tid in range(num_threads)]
        results = [f.result() for f in futures]
    t1 = time.perf_counter()
    return t1 - t0, results

if __name__ == "__main__":
    P_values = [1, 2, 4, 8, 16]
    results_log = []

    print("Starting CPU saturation test (NumPy / GIL-released variant).")
    print("Open Task Manager NOW and watch per-core CPU usage.\n")
    time.sleep(3)

    for P in P_values:
        print(f"--- Running P = {P} threads, {SQRT_COUNT:,} sqrt ops each (NumPy) ---")
        elapsed, _ = run_team(P)
        print(f"P = {P:3d} | Elapsed Time = {elapsed:.4f} s\n")
        results_log.append((P, elapsed))
        time.sleep(2)

    with open("task1_3_cpu_saturation_numpy.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["P", "elapsed_time_s"])
        for P, elapsed in results_log:
            writer.writerow([P, round(elapsed, 4)])

    print("Saved results to task1_3_cpu_saturation_numpy.csv")
