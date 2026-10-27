def priority_demo(use_aging, aging_interval=3):
    # Низкое число означает высокий приоритет.
    processes = [
        {"pid": "LOW", "arrival": 0, "burst": 4, "priority": 10}
    ]

    # Поток процессов с высоким приоритетом.
    for t in range(1, 13):
        processes.append({
            "pid": f"H{t}",
            "arrival": t,
            "burst": 2,
            "priority": 0
        })

    remaining = {p["pid"]: p["burst"] for p in processes}
    first_start = {}
    completed = set()
    waiting = {p["pid"]: 0 for p in processes}
    intervals = []
    current = None
    t = 0

    while len(completed) < len(processes):
        available = [
            p for p in processes
            if p["arrival"] <= t
            and remaining[p["pid"]] > 0
        ]

        if available:
            def priority_key(p):
                effective = p["priority"]
                if use_aging:
                    effective -= waiting[p["pid"]] // aging_interval
                return (effective, p["arrival"], p["pid"])

            best = min(available, key=priority_key)
            current = best
        else:
            current = None

        pid = current["pid"] if current else None

        if intervals and intervals[-1]["pid"] == pid:
            intervals[-1]["end"] = t + 1
        else:
            intervals.append({"start": t, "end": t + 1, "pid": pid})

        for p in available:
            if current is None or p["pid"] != current["pid"]:
                waiting[p["pid"]] += 1

        if current:
            pid = current["pid"]
            first_start.setdefault(pid, t)
            remaining[pid] -= 1
            if remaining[pid] == 0:
                completed.add(pid)

        t += 1

    low_start = first_start.get("LOW")
    print("Aging включён" if use_aging else "Aging выключен")
    print("Первый запуск LOW:", low_start)
    print("Интервалы:")
    print(" | ".join(
        f"{x['start']}-{x['end']}:{x['pid'] or 'IDLE'}"
        for x in intervals
    ))
    print()


priority_demo(False)
priority_demo(True, aging_interval=1)
