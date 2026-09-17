import java.util.concurrent.ThreadLocalRandom;

public class ReductionStyle {
    static final long TOTAL_POINTS = 100_000_000L;

    public static void main(String[] args) throws InterruptedException {
        int[] threadCounts = {1, 2, 4, 8, 16, 32};
        long baselineTime = 0;

        System.out.println("Threads | Runtime(ms) | Speedup vs T1 | Efficiency | Pi (sanity check)");
        System.out.println("---------------------------------------------------------------------");

        for (int T : threadCounts) {
            Result r = runReduction(T);
            if (T == 1) baselineTime = r.elapsedMs;
            double speedup = (double) baselineTime / r.elapsedMs;
            double efficiency = speedup / T * 100.0;
            System.out.printf("%7d | %11d | %13.2fx | %9.2f%% | %.6f%n",
                    T, r.elapsedMs, speedup, efficiency, r.pi);
        }
    }

    static class Result {
        long elapsedMs;
        double pi;
    }

    static Result runReduction(int numThreads) throws InterruptedException {
        long pointsPerThread = TOTAL_POINTS / numThreads;
        Thread[] threads = new Thread[numThreads];
        // Each thread writes to its own slot exactly ONCE, after its loop finishes.
        // No shared-memory writes happen inside the hot loop -> no lock, no false sharing.
        final long[] localHits = new long[numThreads];

        long start = System.nanoTime();
        for (int t = 0; t < numThreads; t++) {
            final int idx = t;
            threads[t] = new Thread(() -> {
                long localCount = 0; // pure thread-local variable (register/stack)
                ThreadLocalRandom rnd = ThreadLocalRandom.current();
                for (long i = 0; i < pointsPerThread; i++) {
                    double x = rnd.nextDouble();
                    double y = rnd.nextDouble();
                    if (x * x + y * y <= 1.0) {
                        localCount++;
                    }
                }
                localHits[idx] = localCount; // single write per thread -> the "reduction" step
            });
        }
        for (Thread th : threads) th.start();
        for (Thread th : threads) th.join();
        long elapsed = System.nanoTime() - start;

        long totalHits = 0;
        for (long h : localHits) totalHits += h;

        Result r = new Result();
        r.elapsedMs = elapsed / 1_000_000;
        r.pi = 4.0 * totalHits / (pointsPerThread * (long) numThreads);
        return r;
    }
}