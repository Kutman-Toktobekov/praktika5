import matplotlib.pyplot as plt
from scheduler import simulate, calculate_metrics
from sets import set2


def count_switches(intervals):
    # Считаем смену одного работающего процесса другим.
    # Переходы через IDLE не считаем переключениями процессов.
    running = [x["pid"] for x in intervals if x["pid"] is not None]
    return sum(
        running[i] != running[i - 1]
        for i in range(1, len(running))
    )


quanta = list(range(1, 11))
waiting_times = []
switch_counts = []

print(f"{'Квант':>6} {'Среднее ожидание':>20} {'Переключения':>15}")
print("-" * 44)

for quantum in quanta:
    intervals = simulate(set2, "RR", quantum=quantum)
    metrics = calculate_metrics(set2, intervals)

    waiting_times.append(metrics["avg_waiting"])
    switches = count_switches(intervals)
    switch_counts.append(switches)

    print(f"{quantum:>6} {metrics['avg_waiting']:>20.2f} {switches:>15}")

fig, ax1 = plt.subplots(figsize=(9, 5))

ax1.plot(
    quanta, waiting_times,
    marker="o", label="Среднее время ожидания"
)
ax1.set_xlabel("Квант времени")
ax1.set_ylabel("Среднее ожидание")
ax1.set_xticks(quanta)
ax1.grid(True, alpha=0.3)

ax2 = ax1.twinx()
ax2.plot(
    quanta, switch_counts,
    marker="s", linestyle="--", label="Число переключений"
)
ax2.set_ylabel("Число переключений")

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")

plt.title("Round Robin: квант, ожидание и переключения (set2)")
plt.tight_layout()
plt.savefig("rr_quantum.png", dpi=150)
print("\nГрафик сохранён в rr_quantum.png")
