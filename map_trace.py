import re
import subprocess
import sys


if len(sys.argv) != 3:
    print("Usage: python3 map_trace.py <trace_file> <executable>")
    sys.exit(1)


trace_file = sys.argv[1]
executable = sys.argv[2]


# Get symbols from the executable
result = subprocess.run(
    ["nm", "-n", executable],
    capture_output=True,
    text=True,
    check=True
)

symbols = []

for line in result.stdout.splitlines():
    parts = line.split()

    if len(parts) >= 3:
        try:
            address = int(parts[0], 16)
        except ValueError:
            continue

        symbol_type = parts[1]
        name = parts[2]

        # Keep text/code symbols
        if symbol_type in ("T", "t"):
            symbols.append((address, name))


# Sort by address
symbols.sort()


def resolve(address):
    """
    Find the nearest symbol whose address is <= runtime address.
    """
    best = None

    for symbol_address, name in symbols:
        if symbol_address <= address:
            best = (symbol_address, name)
        else:
            break

    if best is None:
        return f"0x{address:x}"

    symbol_address, name = best
    offset = address - symbol_address

    if offset == 0:
        return name

    return f"{name}+0x{offset:x}"


# Process trace
with open(trace_file) as f:
    for line in f:
        match = re.match(
            r"(CALL|RETURN)\s+(0x[0-9a-fA-F]+)",
            line
        )

        if not match:
            continue

        event = match.group(1)
        address = int(match.group(2), 16)

        function = resolve(address)

        print(f"{event:<6} {function}")
