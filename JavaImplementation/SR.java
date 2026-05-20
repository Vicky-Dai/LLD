import java.util.concurrent.locks.ReentrantLock;

/**
 * 两个最简单的用法对比：synchronized vs ReentrantLock
 * 场景：多个线程同时给共享变量 +1，必须用“锁”保证结果正确。
 */
public class SR {

    // ---------- 示例 1：synchronized ----------
    static class CounterSync {
        private int value = 0;

        /** 方式 A：锁整个方法（锁对象是 this） */
        synchronized void increment() {
            value++;
        }

        /** 方式 B：只锁一小段代码（可指定锁对象） */
        void incrementBlock() {
            synchronized (this) {
                value++;
            }
        }

        int get() {
            return value;
        }
    }

    // ---------- 示例 2：ReentrantLock ----------
    static class CounterLock {
        private final ReentrantLock lock = new ReentrantLock();
        private int value = 0;

        void increment() {
            lock.lock();
            try {
                value++;
            } finally {
                // 必须在 finally 里 unlock，否则异常时锁永远不释放
                lock.unlock();
            }
        }

        int get() {
            return value;
        }
    }

    public static void main(String[] args) throws InterruptedException {
        int threads = 10;
        int perThread = 1000;

        // --- 演示 synchronized ---
        CounterSync cs = new CounterSync();
        Thread[] t1 = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            t1[i] = new Thread(() -> {
                for (int j = 0; j < perThread; j++) {
                    cs.increment();
                }
            });
            t1[i].start();
        }
        for (Thread t : t1) {
            t.join();
        }
        System.out.println("synchronized 结果: " + cs.get()
                + " (期望 " + (threads * perThread) + ")");

        // --- 演示 ReentrantLock ---
        CounterLock cl = new CounterLock();
        Thread[] t2 = new Thread[threads];
        for (int i = 0; i < threads; i++) {
            t2[i] = new Thread(() -> {
                for (int j = 0; j < perThread; j++) {
                    cl.increment();
                }
            });
            t2[i].start();
        }
        for (Thread t : t2) {
            t.join();
        }
        System.out.println("ReentrantLock 结果: " + cl.get()
                + " (期望 " + (threads * perThread) + ")");
    }
}
