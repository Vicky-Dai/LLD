/*
 * 【分布式锁 + Redisson 入门】读本文件前心里要有两件事：
 *
 * 1) JUC 里的 ReentrantLock / synchronized 只对「同一个 JVM」里的线程有效；
 *    多台机器、多个进程要互斥访问共享资源（抢一张优惠券、写一个订单号），就得用「外部的协调者」，
 *    常见就是 Redis（或 etcd、Zookeeper）。锁的「语义」记在 Redis 里，大家抢同一把钥匙。
 *
 * 2) Redis 里自己用 SET key NX EX 也能做简易锁；Redisson 在之上封装了：
 *    可重入（同一线程可多次 lock）、 lease（租约）/ 看门狗续期、tryLock、公平锁选项等，
 *    并让 unlock 更安全（Lua 校验是不是自己的锁）。
 *
 * 运行前：
 * - 本地起 Redis（默认 redis://127.0.0.1:6379）
 * - 在 IDE 或通过 Maven 引入 Redisson，例如：
 *   <dependency>
 *     <groupId>org.redisson</groupId>
 *     <artifactId>redisson</artifactId>
 *     <version>3.39.0</version>
 *   </dependency>
 *
 * 关掉 RedissonClient 后进程退出（见 finally）。
 */

import org.redisson.Redisson;
import org.redisson.api.RLock;
import org.redisson.api.RedissonClient;
import org.redisson.config.Config;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

public class RedissonDistributedLockDemo {

    private static RedissonClient openClient(String redisUrl) {
        Config config = new Config();
        // 单机示例；集群用 config.useClusterServers()...
        config.useSingleServer().setAddress(redisUrl);
        return Redisson.create(config);
    }

    /** 最常用的模式：拿不到就一直等，finally 里必须 unlock（同一线程）。 */
    static void demoBlockingLock(RedissonClient redisson, String lockName) throws InterruptedException {
        RLock lock = redisson.getLock(lockName);
        lock.lock(); // 可重入；默认带「看门狗」不定期续命，直到 unlock
        try {
            // 临界区：假设这里只有持有锁的人才能做
            Thread.sleep(200);
            System.out.println(Thread.currentThread().getName() + " 在执行临界区");
        } finally {
            // 只有自己加的锁才能解（Redisson 内部用 hash + 线程 id 做可重入计数）
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    /**
     * 带租约的 lock：leaseTime 到期后锁自动释放，适合「任务必须在 N 秒内完成」且不想依赖看门狗。
     * 注意：若业务执行超过 leaseTime，锁已被别人抢走，存在并发风险 —— 要合理设时间或用心跳续期。
     */
    static void demoLockWithLease(RedissonClient redisson, String lockName) {
        RLock lock = redisson.getLock(lockName);
        lock.lock(3, TimeUnit.SECONDS);
        try {
            System.out.println("持有锁最多 3 秒");
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    /** tryLock：等一阵子还拿不到就放弃，避免无限阻塞（例如网关请求超时）。 */
    static boolean demoTryLock(RedissonClient redisson, String lockName) throws InterruptedException {
        RLock lock = redisson.getLock(lockName);
        // 最多等待 500ms；拿到后再持有最多 10s（超过自动过期，无看门狗）
        boolean ok = lock.tryLock(500, 10, TimeUnit.MILLISECONDS);
        if (!ok) {
            System.out.println("没抢到锁，直接返回");
            return false;
        }
        try {
            System.out.println("抢到了，做事");
            return true;
        } finally {
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }

    /**
     * 同一 JVM 里开两个线程抢同一把「逻辑锁」：在真实系统里，另一台机器上的服务也会用同一个 lockName
     * 连同一个 Redis，效果一样 —— 只能有一个「实例」进临界区。
     */
    static void demoTwoThreadsOneLock(RedissonClient redisson) throws InterruptedException {
        String lockName = "demo:inventory:sku-1001";
        int threads = 2;
        ExecutorService pool = Executors.newFixedThreadPool(threads);
        CountDownLatch done = new CountDownLatch(threads);
        AtomicInteger concurrentInside = new AtomicInteger(0);
        AtomicInteger maxConcurrent = new AtomicInteger(0);

        Runnable task = () -> {
            RLock lock = redisson.getLock(lockName);
            lock.lock();
            try {
                int n = concurrentInside.incrementAndGet();
                maxConcurrent.updateAndGet(m -> Math.max(m, n));
                Thread.sleep(300); // 拉长临界区，方便看到互斥
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                concurrentInside.decrementAndGet();
                if (lock.isHeldByCurrentThread()) {
                    lock.unlock();
                }
                done.countDown();
            }
        };

        pool.submit(task);
        pool.submit(task);
        done.await();
        pool.shutdown();

        System.out.println("两线程抢一把锁，临界区内同时人数峰值应为 1，实际 = " + maxConcurrent.get());
    }

    public static void main(String[] args) throws Exception {
        String url = System.getProperty("redis.url", "redis://127.0.0.1:6379");
        RedissonClient client = openClient(url);
        try {
            System.out.println("=== 1) 阻塞锁 ===");
            demoBlockingLock(client, "demo:blocking");

            System.out.println("\n=== 2) 租约锁 ===");
            demoLockWithLease(client, "demo:lease");

            System.out.println("\n=== 3) tryLock ===");
            demoTryLock(client, "demo:try");

            System.out.println("\n=== 4) 两线程互斥（理解「分布式」时把另一线程想成另一台机器）===");
            demoTwoThreadsOneLock(client);
        } finally {
            client.shutdown();
        }
    }
}
