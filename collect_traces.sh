#!/bin/bash

INPUT_DIR="experiment_inputs"
FUZZER="./fuzzing/fuzz_main"
MAPPER="./map_trace.py"

RAW_DIR="dynamic_traces/raw"
NAMED_DIR="dynamic_traces/named"

mkdir -p "$RAW_DIR"
mkdir -p "$NAMED_DIR"

for input in "$INPUT_DIR"/*; do
    [ -f "$input" ] || continue

    name=$(basename "$input")

    echo "Tracing: $name"

    # Run the instrumented program and capture CALL/RETURN addresses
    "$FUZZER" "$input" 2> "$RAW_DIR/$name.txt"

    # Convert addresses to function names
    python3 "$MAPPER" \
        "$RAW_DIR/$name.txt" \
        "$FUZZER" \
        > "$NAMED_DIR/$name.txt"

done

echo "All traces collected successfully."
