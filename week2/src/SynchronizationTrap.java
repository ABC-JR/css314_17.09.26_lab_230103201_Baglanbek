import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;

public class SynchronizationTrap {
    static final long TOTAL_POINTS = 50_000_000L;
    static final int NUM_THREADS = 4;

    // Thread-safe counter: every increment is a CAS (compare-and-swap) operation
    static AtomicLong totalHits = new AtomicLong(0);

    public static void main(String[] args) throws InterruptedException {
        // ---- Multi-threaded, race-free version ----
        long pointsPerThread = TOTAL_POINTS / NUM_THREADS;
        Thread[] threads = new Thread[NUM_THREADS];

        long startMulti = System.nanoTime();
        for (int t = 0; t < NUM_THREADS; t++) {
            threads[t] = new Thread(() -> {
                ThreadLocalRandom rnd = ThreadLocalRandom.current();
                for (long i = 0; i < pointsPerThread; i++) {
                    double x = rnd.nextDouble();
                    double y = rnd.nextDouble();
                    if (x * x + y * y <= 1.0) {
                        totalHits.incrementAndGet(); // safe, but every call fights over one cache line
                    }
                }
            });
        }
        for (Thread th : threads) th.start();
        for (Thread th : threads) th.join();
        long elapsedMulti = System.nanoTime() - startMulti;
        double piMulti = 4.0 * totalHits.get() / TOTAL_POINTS;

        // ---- Single-threaded baseline (no locks, no contention) ----
        long singleHits = 0;
        ThreadLocalRandom rnd = ThreadLocalRandom.current();
        long startSingle = System.nanoTime();
        for (long i = 0; i < TOTAL_POINTS; i++) {
            double x = rnd.nextDouble();
            double y = rnd.nextDouble();
            if (x * x + y * y <= 1.0) {
                singleHits++;
            }
        }
        long elapsedSingle = System.nanoTime() - startSingle;
        double piSingle = 4.0 * singleHits / TOTAL_POINTS;

        System.out.println("=== Multi-threaded (AtomicLong, 4 threads) ===");
        System.out.printf("Pi: %.6f | Time: %.3f ms%n", piMulti, elapsedMulti / 1_000_000.0);
        System.out.println("=== Single-threaded baseline ===");
        System.out.printf("Pi: %.6f | Time: %.3f ms%n", piSingle, elapsedSingle / 1_000_000.0);
        System.out.printf("Slowdown Factor (Multi / Single): %.2fx%n",
                (double) elapsedMulti / elapsedSingle);
    }
}