from concurrent.futures import ThreadPoolExecutor
import threading
import time
import math
import csv

SQRT_COUNT = 10_000_000

def worker_task(thread_id: int, team_size: int):
    native_tid = threading.get_native_id()
    # Artificial CPU-bound workload
    total = 0.0
    for i in range(SQRT_COUNT):
        total += math.sqrt(i)
    return native_tid, total

def run_team(num_threads: int):
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = [executor.submit(worker_task, tid, num_threads) for tid in range(num_threads)]
        results = [f.result() for f in futures]
    t1 = time.perf_counter()
    return t1 - t0, results

if __name__ == "__main__":
    P_values = [1, 2, 4, 8, 16]
    results_log = []

    print("Starting CPU saturation test.")
    print("IMPORTANT: Open Task Manager (Performance tab, or per-core CPU view) NOW")
    print("and watch core utilization while each P value runs.\n")
    time.sleep(3)  # gives you time to switch to Task Manager

    for P in P_values:
        print(f"--- Running P = {P} threads, {SQRT_COUNT:,} sqrt ops each ---")
        elapsed, _ = run_team(P)
        print(f"P = {P:3d} | Elapsed Time = {elapsed:.4f} s\n")
        results_log.append((P, elapsed))
        time.sleep(2)  # pause between runs so you can screenshot Task Manager per P

    with open("task1_3_cpu_saturation.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["P", "elapsed_time_s"])
        for P, elapsed in results_log:
            writer.writerow([P, round(elapsed, 4)])

    print("Saved results to task1_3_cpu_saturation.csv")