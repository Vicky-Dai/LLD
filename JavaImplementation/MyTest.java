import java.util.concurrent.ArrayBlockingQueue;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

/**
 * 演示：多线程下用 synchronized + wait/notifyAll 协调「存钱」与「取钱」。
 * <p>
 * 编译运行（在 JavaImplementation 目录下）：
 * {@code javac MyTest.java && java MyTest}
 */
public class MyTest {

    public static void main(String[] args) {
        Account account = new Account();
        ExecutorService executorService = new ThreadPoolExecutor(
                5,
                5,
                0,
                TimeUnit.SECONDS,
                new ArrayBlockingQueue<>(10),
                Executors.defaultThreadFactory(),
                new ThreadPoolExecutor.AbortPolicy());

        Callable<Integer> saveCallable = () -> {
            while (true) {
                account.saveMoney(10);
                Thread.sleep(200);
            }
        };

        Callable<Integer> drawCallable = () -> {
            while (true) {
                account.drawMoney(10);
                Thread.sleep(200);
            }
        };

        for (int i = 0; i < 3; i++) {
            executorService.submit(saveCallable);
        }
        for (int i = 0; i < 2; i++) {
            executorService.submit(drawCallable);
        }
        // 注意：这里 main 结束但线程池里的任务死循环，JVM 不会退出（非 daemon 线程）。
    }
}

class Account {
    int money = 0;

    /**
     * 取钱：余额不够时在锁上 wait，避免「透支」。
     */
    public void drawMoney(int num) {
        synchronized (this) {
            // 必须用 while：被唤醒后要再次检查条件（虚假唤醒 / 别的线程先改了余额）。
            while (num > money) {
                try {
                    // wait 前 notifyAll：尽量叫醒「存钱」方，避免大家都卡在 wait 上（视策略而定）。
                    notifyAll();
                    wait();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
            money -= num;
            System.out.println(Thread.currentThread().getName() + " 取钱, 剩余 " + money);
            notifyAll();
        }
    }

    /**
     * 存钱：这里约定「只有余额为 0 才能存」，相当于缓冲区最多只保留一笔存款的语义。
     */
    public void saveMoney(int num) {
        synchronized (this) {
            while (money > 0) {
                try {
                    notifyAll();
                    wait();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
            money += num;
            System.out.println(Thread.currentThread().getName() + " 存钱, 剩余 " + money);
            notifyAll();
        }
    }
}
