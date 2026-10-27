from scheduler import simulate, calculate_metrics
from sets import set1

for algorithm, params in [
    ("SRTF", {}),
    ("RR", {"quantum": 3}),
]:
    intervals = simulate(set1, algorithm, **params)

    busy_time = sum(
        x["end"] - x["start"]
        for x in intervals
        if x["pid"] is not None
    )

    expected_time = sum(p["burst"] for p in set1)
    metrics = calculate_metrics(set1, intervals)

    assert busy_time == expected_time, (
        f"{algorithm}: неверная сумма времени выполнения"
    )

    assert all(
        x["end"] > x["start"] for x in intervals
    ), f"{algorithm}: найден интервал нулевой или отрицательной длины"

    assert all(
        intervals[i]["end"] == intervals[i + 1]["start"]
        for i in range(len(intervals) - 1)
    ), f"{algorithm}: есть разрыв между интервалами"

    print(f"\n{algorithm}: проверка пройдена")
    print("Занятое время CPU:", busy_time)
    print("Среднее ожидание:", round(metrics["avg_waiting"], 2))
    print("Среднее время оборота:", round(metrics["avg_turnaround"], 2))
    print("Среднее время отклика:", round(metrics["avg_response"], 2))
    print("Интервалы:", intervals)
