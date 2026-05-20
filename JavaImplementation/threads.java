import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.Callable;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.CyclicBarrier;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 面试常见多线程小例子：创建线程、同步、通信、工具类、线程池、中断、ThreadLocal 等。
 * 编译运行（在本目录下）：javac threads.java && java threads
 */
public class threads {

    private static void sep(String title) {
        System.out.println("\n========== " + title + " ==========");
    }

    /** 1）实现 Runnable + Thread：start / join */
    static void demoRunnableJoin() throws InterruptedException {
        sep("1. Runnable + Thread（start / join）");
        Runnable task = () -> System.out.println(Thread.currentThread().getName() + " 执行任务");
        Thread t = new Thread(task, "worker-1");
        t.start();
        t.join();
        System.out.println("main 在 join 之后继续");
    }

    /** 2）synchronized：无锁竞态 vs 有锁正确累加 */
    static void demoSynchronizedCounter() throws InterruptedException {
        sep("2. synchronized 保证临界区互斥");
        class Unsafe {
            int n = 0;
            void inc() { n++; }
        }
        class Safe {
            int n = 0;
            synchronized void inc() { n++; }
        }
        int loops = 100_000;
        Unsafe u = new Unsafe();
        Thread a = new Thread(() -> { for (int i = 0; i < loops; i++) u.inc(); });
        Thread b = new Thread(() -> { for (int i = 0; i < loops; i++) u.inc(); });
        a.start();
        b.start();
        a.join();
        b.join();
        System.out.println("无 synchronized 累加（常小于期望值）: " + u.n + " 期望 " + (2 * loops));

        Safe s = new Safe();
        Thread c = new Thread(() -> { for (int i = 0; i < loops; i++) s.inc(); });
        Thread d = new Thread(() -> { for (int i = 0; i < loops; i++) s.inc(); });
        c.start();
        d.start();
        c.join();
        d.join();
        System.out.println("有 synchronized: " + s.n);
    }

    /** 3）volatile：可见性（一写多读时停止标志） */
    static volatile boolean running = true;

    static void demoVolatileStop() throws InterruptedException {
        sep("3. volatile 可见性（停止标志）");
        running = true;
        Thread worker = new Thread(() -> {
            while (running) {
                Thread.yield();
            }
            System.out.println("worker 看到 running=false，退出循环");
        }, "volatile-worker");
        worker.start();
        Thread.sleep(50);
        running = false;
        worker.join();
    }

    /** 4）wait / notify：两个线程交替打印 1~10（按轮次，避免 notify 丢失死锁） */
    static void demoWaitNotifyOddEven() throws InterruptedException {
        sep("4. wait / notify 交替打印（1~10，两线程轮流）");
        final Object lock = new Object();
        final int max = 10;
        final int[] next = {1}; // 下一个要打印的数
        Thread odd = new Thread(() -> {
            try {
                synchronized (lock) {
                    while (next[0] <= max) {
                        while (next[0] % 2 == 0) {
                            lock.wait();
                        }
                        if (next[0] > max) {
                            break;
                        }
                        System.out.println("线程A 打印: " + next[0]);
                        next[0]++;
                        lock.notifyAll();
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        Thread even = new Thread(() -> {
            try {
                synchronized (lock) {
                    while (next[0] <= max) {
                        while (next[0] % 2 != 0) {
                            lock.wait();
                        }
                        if (next[0] > max) {
                            break;
                        }
                        System.out.println("线程B 打印: " + next[0]);
                        next[0]++;
                        lock.notifyAll();
                    }
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        odd.start();
        even.start();
        odd.join();
        even.join();
    }

    /** 5）ReentrantLock + Condition：三个线程按序循环打印 A B C（各 3 轮） */
    static void demoLockConditionABC() throws InterruptedException {
        sep("5. ReentrantLock + Condition（按序打印 ABC）");
        ReentrantLock lk = new ReentrantLock();
        Condition ca = lk.newCondition();
        Condition cb = lk.newCondition();
        Condition cc = lk.newCondition();
        AtomicInteger turn = new AtomicInteger(0); // 0=A 1=B 2=C
        int rounds = 3;

        Runnable printA = () -> {
            lk.lock();
            try {
                for (int i = 0; i < rounds; i++) {
                    while (turn.get() != 0) {
                        ca.await();
                    }
                    System.out.print("A ");
                    turn.set(1);
                    cb.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lk.unlock();
            }
        };
        Runnable printB = () -> {
            lk.lock();
            try {
                for (int i = 0; i < rounds; i++) {
                    while (turn.get() != 1) {
                        cb.await();
                    }
                    System.out.print("B ");
                    turn.set(2);
                    cc.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lk.unlock();
            }
        };
        Runnable printC = () -> {
            lk.lock();
            try {
                for (int i = 0; i < rounds; i++) {
                    while (turn.get() != 2) {
                        cc.await();
                    }
                    System.out.print("C ");
                    turn.set(0);
                    ca.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lk.unlock();
            }
        };

        Thread ta = new Thread(printA, "A");
        Thread tb = new Thread(printB, "B");
        Thread tc = new Thread(printC, "C");
        ta.start();
        tb.start();
        tc.start();
        ta.join();
        tb.join();
        tc.join();
        System.out.println();
    }

    /** 6）CountDownLatch：主线程等待多个子任务完成 */
    static void demoCountDownLatch() throws InterruptedException {
        sep("6. CountDownLatch（等子线程）");
        int n = 3;
        CountDownLatch done = new CountDownLatch(n);
        for (int i = 0; i < n; i++) {
            final int id = i;
            new Thread(() -> {
                System.out.println("任务 " + id + " 完成");
                done.countDown();
            }).start();
        }
        done.await();
        System.out.println("main：全部子任务已 countDown");
    }

    /** 7）CyclicBarrier：多线程到齐后一起执行下一步 */
    static void demoCyclicBarrier() throws Exception {
        sep("7. CyclicBarrier（到齐再打印）");
        int parties = 3;
        CyclicBarrier barrier = new CyclicBarrier(parties, () ->
                System.out.println("--- 全员到齐，本轮开始 ---"));
        Runnable worker = () -> {
            try {
                String name = Thread.currentThread().getName();
                System.out.println(name + " 到达屏障");
                barrier.await();
                System.out.println(name + " 继续执行");
            } catch (Exception e) {
                Thread.currentThread().interrupt();
            }
        };
        for (int i = 0; i < parties; i++) {
            new Thread(worker, "p-" + i).start();
        }
        Thread.sleep(200);
    }

    /** 8）Semaphore：限流（同时最多 2 个在“临界打印区”） */
    static void demoSemaphore() throws InterruptedException {
        sep("8. Semaphore（最多 2 个并发打印）");
        Semaphore sem = new Semaphore(2);
        Runnable job = () -> {
            String name = Thread.currentThread().getName();
            try {
                sem.acquire();
                System.out.println(name + " 进入");
                Thread.sleep(100);
                System.out.println(name + " 离开");
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                sem.release();
            }
        };
        for (int i = 0; i < 5; i++) {
            new Thread(job, "sem-" + i).start();
        }
        Thread.sleep(500);
    }

    /** 9）BlockingQueue：生产者-消费者（简化打印） */
    static void demoProducerConsumer() throws InterruptedException {
        sep("9. BlockingQueue 生产者-消费者");
        BlockingQueue<Integer> q = new ArrayBlockingQueue<>(2);
        Thread producer = new Thread(() -> {
            try {
                for (int i = 1; i <= 5; i++) {
                    q.put(i);
                    System.out.println("生产: " + i);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "producer");
        Thread consumer = new Thread(() -> {
            try {
                for (int i = 0; i < 5; i++) {
                    int v = q.take();
                    System.out.println("消费: " + v);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }, "consumer");
        producer.start();
        consumer.start();
        producer.join();
        consumer.join();
    }

    /** 10）线程池 + Callable / Future */
    static void demoExecutorFuture() throws ExecutionException, InterruptedException {
        sep("10. ExecutorService + Callable / Future");
        ExecutorService pool = Executors.newFixedThreadPool(2);
        Callable<String> task = () -> {
            Thread.sleep(50);
            return "子线程结果";
        };
        Future<String> f = pool.submit(task);
        System.out.println("Future.get: " + f.get());
        pool.shutdown();
    }

    /** 11）interrupt：协作式中断 */
    static void demoInterrupt() throws InterruptedException {
        sep("11. interrupt（协作式）");
        Thread t = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                System.out.println("worker 运行中…");
                try {
                    Thread.sleep(300);
                } catch (InterruptedException e) {
                    System.out.println("sleep 中收到中断，清中断标志并退出");
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        });
        t.start();
        Thread.sleep(500);
        t.interrupt();
        t.join();
        System.out.println("main：worker 已结束");
    }

    /** 12）ThreadLocal：每个线程自己的变量 */
    static final ThreadLocal<Integer> TL = ThreadLocal.withInitial(() -> 0);

    static void demoThreadLocal() throws InterruptedException {
        sep("12. ThreadLocal");
        Runnable r = () -> {
            int v = (int) (Math.random() * 100);
            TL.set(v);
            System.out.println(Thread.currentThread().getName() + " TL=" + TL.get());
        };
        Thread x = new Thread(r, "t1");
        Thread y = new Thread(r, "t2");
        x.start();
        y.start();
        x.join();
        y.join();
    }

    public static void main(String[] args) throws Exception {
        demoRunnableJoin();
        demoSynchronizedCounter();
        demoVolatileStop();
        demoWaitNotifyOddEven();
        demoLockConditionABC();
        demoCountDownLatch();
        demoCyclicBarrier();
        demoSemaphore();
        demoProducerConsumer();
        demoExecutorFuture();
        demoInterrupt();
        demoThreadLocal();
        System.out.println("\n全部 demo 跑完。");
    }
}
