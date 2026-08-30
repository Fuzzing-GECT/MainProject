import glob
import os

trace_files = sorted(glob.glob("dynamic_traces/named/*.txt"))

print(f"{'Input':<15} {'Total Events':<15} {'Unique Functions':<18} {'Main Parsing Behaviour'}")
print("-" * 75)

for trace_file in trace_files:

    # Read all non-empty lines
    with open(trace_file, "r") as f:
        lines = [line.strip() for line in f if line.strip()]

    # Extract function names
    functions = []

    for line in lines:
        parts = line.split()

        if len(parts) >= 2:
            functions.append(parts[1])

    unique_functions = set(functions)

    # Identify important parsing behaviour
    behaviour = []

    if "parse_object" in unique_functions:
        behaviour.append("Object")

    if "parse_array" in unique_functions:
        behaviour.append("Array")

    if "parse_string" in unique_functions:
        behaviour.append("String")

    if "parse_number" in unique_functions:
        behaviour.append("Number")

    if not behaviour:
        behaviour.append("Other / early path")

    filename = os.path.basename(trace_file)

    print(
        f"{filename:<15} "
        f"{len(lines):<15} "
        f"{len(unique_functions):<18} "
        f"{', '.join(behaviour)}"
    )
