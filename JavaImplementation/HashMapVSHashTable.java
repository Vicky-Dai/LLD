import java.util.Enumeration;
import java.util.HashMap;
import java.util.Hashtable;
import java.util.Map;

/**
 * HashMap vs Hashtable：用法对比与常见差异说明。
 *
 * 主要区别（面试常考）：
 * 1. 线程安全：Hashtable 公开方法基本都用 synchronized，是线程安全的遗留类；
 *    HashMap 非线程安全，多线程并发修改需 ConcurrentHashMap 或自行同步。
 * 2. null：HashMap 允许一个 null 键、多个 null 值；Hashtable 不允许 null 键和 null 值。
 * 3. 性能：单线程场景通常 HashMap 更快（无方法级全局锁）。
 * 4. API 年代：Hashtable 自 JDK 1.0；HashMap 自 1.2，更常用；新代码优先 HashMap / ConcurrentHashMap。
 *
 * 可运行观察线程安全：见 {@link #demoConcurrentMerge()}（多线程对同一 key 做 merge 累加）。
 */
public class HashMapVSHashTable {

    static void demoBasic() {
        System.out.println("=== 基本 put/get ===");
        HashMap<String, Integer> hm = new HashMap<>();
        hm.put("a", 1);
        hm.put("b", 2);
        System.out.println("HashMap: " + hm);

        Hashtable<String, Integer> ht = new Hashtable<>();
        ht.put("a", 1);
        ht.put("b", 2);
        System.out.println("Hashtable: " + ht);
    }

    static void demoNull() {
        System.out.println("\n=== null 键值 ===");
        HashMap<String, Integer> hm = new HashMap<>();
        hm.put(null, 0);
        hm.put("x", null);
        System.out.println("HashMap 允许 null 键/值: " + hm);

        Hashtable<String, Integer> ht = new Hashtable<>();
        try {
            ht.put(null, 1);
        } catch (NullPointerException e) {
            System.out.println("Hashtable.put(null, v) -> NullPointerException（预期）");
        }
        try {
            ht.put("y", null);
        } catch (NullPointerException e) {
            System.out.println("Hashtable.put(k, null) -> NullPointerException（预期）");
        }
    }

    /** Hashtable 还保留了 Enumeration 风格遍历（遗留 API）。 */
    static void demoEnumeration() {
        System.out.println("\n=== Hashtable.keys() / elements()（Enumeration）===");
        Hashtable<String, Integer> ht = new Hashtable<>();
        ht.put("k1", 10);
        ht.put("k2", 20);
        Enumeration<String> keys = ht.keys();
        while (keys.hasMoreElements()) {
            String k = keys.nextElement();
            System.out.println("  key=" + k + " value=" + ht.get(k));
        }
    }

    /** 单线程下两者行为类似；多线程写 Hashtable 仍可能死锁/性能差，高并发用 ConcurrentHashMap。 */
    static void demoThreadSafetyNote() {
        System.out.println("\n=== 线程安全（概念）===");
        System.out.println("Hashtable：方法级 synchronized，多线程可同时读但写会串行，粒度粗。");
        System.out.println("HashMap：无内置锁，多线程同时 put/remove 可能丢更新或死循环（JDK8+ 结构破坏风险），需外部同步或换 ConcurrentHashMap。");
        System.out.println("（下面 merge 演示用运行结果对比，比纯文字更直观。）");
    }

    /**
     * 多线程对同一 key 并发 {@code merge}：在 JDK 里 Hashtable.merge 是 synchronized 方法，
     * 一次 merge 读改写在同一把锁内完成，累加不丢；HashMap.merge 无内置锁，并发下大量丢更新。
     * <p>
     * 注意：若是「先 get 再 put」两段分开调用，Hashtable 也可能丢更新（两次加锁之间可被别的线程插队）；
     * 本例特意用 merge，才能稳定看出 Hashtable「单方法内同步」的效果。
     */
    static void demoConcurrentMerge() throws InterruptedException {
        System.out.println("\n=== 并发 merge 同一键（肉眼对比线程安全）===");
        final int nThreads = 8;
        final int perThread = 10_000;
        final long expected = (long) nThreads * perThread;

        HashMap<String, Integer> hm = new HashMap<>();
        hm.put("k", 0);
        Thread[] hmWorkers = new Thread[nThreads];
        for (int t = 0; t < nThreads; t++) {
            hmWorkers[t] = new Thread(() -> {
                for (int i = 0; i < perThread; i++) {
                    hm.merge("k", 1, Integer::sum);
                }
            });
        }
        for (Thread w : hmWorkers) {
            w.start();
        }
        for (Thread w : hmWorkers) {
            w.join();
        }
        System.out.println("期望: " + expected + "（" + nThreads + " 线程 × 每线程 merge +" + perThread + "）");
        System.out.println("HashMap 实际 get(k): " + hm.get("k") + "  ← 通常远小于期望（并发丢更新）");

        Hashtable<String, Integer> ht = new Hashtable<>();
        ht.put("k", 0);
        Thread[] htWorkers = new Thread[nThreads];
        for (int t = 0; t < nThreads; t++) {
            htWorkers[t] = new Thread(() -> {
                for (int i = 0; i < perThread; i++) {
                    ht.merge("k", 1, Integer::sum);
                }
            });
        }
        for (Thread w : htWorkers) {
            w.start();
        }
        for (Thread w : htWorkers) {
            w.join();
        }
        System.out.println("Hashtable 实际 get(k): " + ht.get("k") + "  ← 应与期望一致");
    }

    public static void main(String[] args) throws InterruptedException {
        demoBasic();
        demoNull();
        demoEnumeration();
        demoThreadSafetyNote();
        demoConcurrentMerge();

        System.out.println("\n=== 同一套泛型 Map 操作（多态）===");
        Map<String, Integer> m1 = new HashMap<>();
        Map<String, Integer> m2 = new Hashtable<>();
        m1.put("n", 1);
        m2.put("n", 1);
        System.out.println("HashMap as Map: " + m1);
        System.out.println("Hashtable as Map: " + m2);
    }
}
