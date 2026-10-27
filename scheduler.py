from collections import deque
from statistics import mean


def simulate(processes, algorithm, **params):
    """Возвращает интервалы выполнения: start, end, pid."""
    algorithm = algorithm.upper()
    supported = {"FCFS", "SJF", "SRTF", "PRIORITY", "RR"}

    if algorithm not in supported:
        raise ValueError(f"Неизвестный алгоритм: {algorithm}")
    if not processes:
        return []

    jobs = []
    for i, p in enumerate(processes):
        job = dict(p)
        job.setdefault("pid", f"P{i + 1}")
        if job["arrival"] < 0 or job["burst"] <= 0:
            raise ValueError("arrival должен быть >= 0, burst должен быть > 0")
        if algorithm == "PRIORITY" and "priority" not in job:
            raise ValueError("Для Priority требуется поле priority")
        jobs.append(job)

    quantum = params.get("quantum", 2)
    if algorithm == "RR" and quantum <= 0:
        raise ValueError("Квант должен быть положительным")

    n = len(jobs)
    remaining = [p["burst"] for p in jobs]
    completed = set()
    first_start = [None] * n
    intervals = []
    ready = deque()
    current = None
    slice_left = quantum
    pending_requeue = None
    next_arrival = 0
    order = sorted(range(n), key=lambda i: (jobs[i]["arrival"], i))
    t = 0

    while len(completed) < n:
        # Сначала добавляем все процессы, поступившие к моменту t.
        while (next_arrival < n
               and jobs[order[next_arrival]]["arrival"] <= t):
            i = order[next_arrival]
            if algorithm == "RR":
                ready.append(i)
            next_arrival += 1

        # В RR новые поступления ставятся в очередь раньше
        # процесса, у которого только что закончился квант.
        if pending_requeue is not None:
            ready.append(pending_requeue)
            pending_requeue = None

        available = [
            i for i in range(n)
            if jobs[i]["arrival"] <= t
            and remaining[i] > 0
            and i not in completed
        ]

        if algorithm == "RR":
            if current is None and ready:
                current = ready.popleft()
                slice_left = quantum

        elif algorithm in {"FCFS", "SJF"}:
            # FCFS и SJF — непредотесняющие алгоритмы.
            if current is None and available:
                if algorithm == "FCFS":
                    current = min(
                        available,
                        key=lambda i: (jobs[i]["arrival"], i)
                    )
                else:
                    current = min(
                        available,
                        key=lambda i: (
                            jobs[i]["burst"], jobs[i]["arrival"], i
                        )
                    )

        else:
            # SRTF и Priority — вытесняющие алгоритмы.
            if available:
                if algorithm == "SRTF":
                    best = min(
                        available,
                        key=lambda i: (
                            remaining[i], jobs[i]["arrival"], i
                        )
                    )
                    # При равном оставшемся времени сохраняем текущий процесс.
                    if (current in available
                            and remaining[current] == remaining[best]):
                        best = current
                    current = best
                else:
                    best = min(
                        available,
                        key=lambda i: (
                            jobs[i]["priority"], jobs[i]["arrival"], i
                        )
                    )
                    # При равном приоритете не вытесняем текущий процесс.
                    if (current in available
                            and jobs[current]["priority"]
                            == jobs[best]["priority"]):
                        best = current
                    current = best
            else:
                current = None

        # Если процесс не готов — фиксируем простой CPU.
        pid = jobs[current]["pid"] if current is not None else None

        if intervals and intervals[-1]["pid"] == pid:
            intervals[-1]["end"] = t + 1
        else:
            intervals.append({"start": t, "end": t + 1, "pid": pid})

        if current is not None:
            i = current
            if first_start[i] is None:
                first_start[i] = t

            remaining[i] -= 1

            if algorithm == "RR":
                slice_left -= 1

            if remaining[i] == 0:
                completed.add(i)
                current = None
                if algorithm == "RR":
                    slice_left = quantum
            elif algorithm == "RR" and slice_left == 0:
                pending_requeue = i
                current = None
                slice_left = quantum

        t += 1

    return intervals


def calculate_metrics(processes, intervals):
    """Метрики для каждого процесса и средние значения."""
    if not processes or not intervals:
        raise ValueError("Нужны процессы и интервалы")

    details = {}
    for p in processes:
        pid = p["pid"]
        own = [x for x in intervals if x["pid"] == pid]
        if not own:
            raise ValueError(f"Нет интервалов выполнения для {pid}")

        completion = max(x["end"] for x in own)
        first_start = min(x["start"] for x in own)
        turnaround = completion - p["arrival"]
        waiting = turnaround - p["burst"]
        response = first_start - p["arrival"]

        details[pid] = {
            "waiting": waiting,
            "turnaround": turnaround,
            "response": response,
            "completion": completion,
        }

    start = min(x["start"] for x in intervals)
    end = max(x["end"] for x in intervals)
    elapsed = end - start
    busy = sum(
        x["end"] - x["start"]
        for x in intervals if x["pid"] is not None
    )

    return {
        "processes": details,
        "avg_waiting": mean(x["waiting"] for x in details.values()),
        "avg_turnaround": mean(x["turnaround"] for x in details.values()),
        "avg_response": mean(x["response"] for x in details.values()),
        "cpu_utilization": 100 * busy / elapsed if elapsed else 0,
    }


def print_table(results):
    """Печатает таблицу метрик алгоритмов."""
    print(
        f"{'Алгоритм':<12} {'Ожидание':>12} {'Оборот':>12} "
        f"{'Отклик':>12} {'CPU, %':>10}"
    )
    print("-" * 62)

    for name, metrics in results.items():
        print(
            f"{name:<12} "
            f"{metrics['avg_waiting']:>12.2f} "
            f"{metrics['avg_turnaround']:>12.2f} "
            f"{metrics['avg_response']:>12.2f} "
            f"{metrics['cpu_utilization']:>10.2f}"
        )


def main():
    from sets import set1, set2

    algorithms = ["FCFS", "SJF", "SRTF", "PRIORITY", "RR"]

    for set_name, processes in [("set1", set1), ("set2", set2)]:
        print(f"\n=== {set_name} ===")
        results = {}

        for algorithm in algorithms:
            params = {"quantum": 3} if algorithm == "RR" else {}
            intervals = simulate(processes, algorithm, **params)
            results[algorithm] = calculate_metrics(processes, intervals)

        print_table(results)

        print("\nИнтервалы CPU для set1/set2:")
        for algorithm in algorithms:
            params = {"quantum": 3} if algorithm == "RR" else {}
            intervals = simulate(processes, algorithm, **params)
            timeline = " | ".join(
                f"{x['start']}-{x['end']}:"
                f"{x['pid'] if x['pid'] is not None else 'IDLE'}"
                for x in intervals
            )
            print(f"{algorithm:<10} {timeline}")


if __name__ == "__main__":
    main()
