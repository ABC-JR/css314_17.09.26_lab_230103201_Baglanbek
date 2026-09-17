
import java.util.concurrent.ThreadLocalRandom;

public class PhantomBug {
    static final long TOTAL_POINTS = 50_000_000L;
    static final int NUM_THREADS = 4;

    // Shared, UNSYNCHRONIZED counter -> classic data race (lost updates)
    static long totalHits = 0;

    public static void main(String[] args) throws InterruptedException {
        long pointsPerThread = TOTAL_POINTS / NUM_THREADS;
        Thread[] threads = new Thread[NUM_THREADS];

        long start = System.nanoTime();
        for (int t = 0; t < NUM_THREADS; t++) {
            threads[t] = new Thread(() -> {
                ThreadLocalRandom rnd = ThreadLocalRandom.current();
                for (long i = 0; i < pointsPerThread; i++) {
                    double x = rnd.nextDouble();
                    double y = rnd.nextDouble();
                    if (x * x + y * y <= 1.0) {
                        totalHits++; // NOT atomic: read-modify-write race across 4 threads
                    }
                }
            });
        }
        for (Thread th : threads) th.start();
        for (Thread th : threads) th.join();
        long elapsed = System.nanoTime() - start;

        double pi = 4.0 * totalHits / TOTAL_POINTS;
        System.out.printf("Total Hits: %d / %d%n", totalHits, TOTAL_POINTS);
        System.out.printf("Estimated Pi: %.6f%n", pi);
        System.out.printf("Elapsed Time: %.3f ms%n", elapsed / 1_000_000.0);
    }
}