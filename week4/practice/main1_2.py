from concurrent.futures import ThreadPoolExecutor
import threading
import time
import csv
import os

def worker_task(thread_id: int, team_size: int):
    return threading.get_native_id()

def run_team(num_threads: int, trials: int = 5):
    times = []
    for _ in range(trials):
        t0 = time.perf_counter()
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(worker_task, tid, num_threads) for tid in range(num_threads)]
            for f in futures:
                f.result()
        t1 = time.perf_counter()
        times.append(t1 - t0)
    return times

if __name__ == "__main__":
    print(f"Logical CPU cores detected: {os.cpu_count()}\n")

    P_values = [1, 2, 4, 8, 16, 32, 64]
    results = []

    for P in P_values:
        times = run_team(P, trials=5)
        avg_time = sum(times) / len(times)
        results.append((P, avg_time, times))
        print(f"P = {P:3d} | Avg Time = {avg_time*1000:.3f} ms | Trials(ms) = {[round(t*1000,3) for t in times]}")

    with open("task1_2_oversubscription.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["P", "avg_time_ms", "trial1_ms", "trial2_ms", "trial3_ms", "trial4_ms", "trial5_ms"])
        for P, avg_time, times in results:
            writer.writerow([P, round(avg_time*1000, 4)] + [round(t*1000, 4) for t in times])

    print("\nSaved results to task1_2_oversubscription.csv")