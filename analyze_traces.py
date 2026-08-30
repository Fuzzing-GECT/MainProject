import glob
import os

trace_files = sorted(glob.glob("dynamic_traces/named/*.txt"))

print(
    f"{'Input':<15}"
    f"{'CALLs':>8}"
    f"{'RETURNs':>10}"
    f"{'Events':>9}"
    f"{'Unique Funcs':>15}"
)

print("-" * 60)

for trace_file in trace_files:

    with open(trace_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    calls = []
    returns = []

    for line in lines:
        parts = line.split()

        if len(parts) < 2:
            continue

        event = parts[0]
        function = parts[1]

        if event == "CALL":
            calls.append(function)

        elif event == "RETURN":
            returns.append(function)

    unique_functions = set(calls + returns)

    filename = os.path.basename(trace_file)

    print(
        f"{filename:<15}"
        f"{len(calls):>8}"
        f"{len(returns):>10}"
        f"{len(lines):>9}"
        f"{len(unique_functions):>15}"
    )
