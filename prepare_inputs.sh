#!/bin/bash

INPUT_DIR="experiment_inputs"

for input in "$INPUT_DIR"/*; do
    [ -f "$input" ] || continue

    # Skip temporary/script-generated files if any
    case "$input" in
        *.tmp|*.new) continue ;;
    esac

    name=$(basename "$input")

    echo "Preparing: $name"

    # Remove the first two bytes ("bf") into a temporary file
    tail -c +3 "$input" > "$input.tmp"

    # Create the converted input
    printf '0000' > "$input.new"
    cat "$input.tmp" >> "$input.new"
    printf '\0' >> "$input.new"

    # Replace the copied input with the converted version
    mv "$input.new" "$input"
    rm "$input.tmp"
done

echo "All experiment inputs prepared successfully."
