# cJSON Dynamic Execution Trace Experiment

## 1. Clone OSS-Fuzz and cJSON

```bash
cd /mnt/g
git clone https://github.com/google/oss-fuzz.git
git clone https://github.com/DaveGamble/cJSON.git
```

Enter the cJSON repository:

```bash
cd /mnt/g/cJSON
```

---

## 2. Check the cJSON fuzzing files

The relevant files are:

```text
cJSON/
├── fuzzing/
│   ├── cjson_read_fuzzer.c
│   ├── fuzz_main.c
│   ├── inputs/
│   └── json.dict
```

The existing `fuzz_main.c` is used to execute one input file directly without running libFuzzer.

Check that it exists:

```bash
ls fuzzing/
```

---

## 3. Create the build directory

```bash
cd /mnt/g/cJSON
mkdir build-trace2
cd build-trace2
```

---

## 4. Configure the build

Configure cJSON with fuzzing enabled:

```bash
cmake .. \
  -DENABLE_CJSON_TEST=ON \
  -DCMAKE_C_FLAGS="-finstrument-functions -g -O0"
```

The important option is:

```text
-finstrument-functions
```

It makes the compiler automatically insert function-entry and function-exit instrumentation.

---

## 5. Add the tracing code

Create:

```bash
nano trace.c
```

Use the shared `trace.c` file.

The tracing functions record:

```text
CALL
RETURN
```

for instrumented functions.

Save and exit.

---

## 6. Build the instrumented program

```bash
make -j$(nproc)
```

Check that the fuzzing executable exists:

```bash
ls fuzzing/fuzz_main
```

---

## 7. Prepare the input corpus

The original cJSON corpus is located at:

```text
cJSON/fuzzing/inputs/
```

Copy it to a separate directory so that the original corpus is not modified:

```bash
mkdir -p experiment_inputs
cp ../fuzzing/inputs/* experiment_inputs/
```

The cJSON fuzz target expects a 4-byte configuration prefix before the JSON input. Therefore, create experiment copies with the required prefix rather than modifying the original corpus.

Verify the original files if needed:

```bash
xxd -l 20 ../fuzzing/inputs/test10
```

---

## 8. Create directories for traces

```bash
mkdir -p dynamic_traces/raw
mkdir -p dynamic_traces/named
```

---

## 9. Run one input

For example:

```bash
./fuzzing/fuzz_main experiment_inputs/test10 2> dynamic_traces/raw/test10.txt
```

View the raw trace:

```bash
cat dynamic_traces/raw/test10.txt
```

The raw trace contains function addresses, for example:

```text
CALL  0x401436
CALL  0x4015ce
RETURN 0x4015ce
RETURN 0x401436
```

---

## 10. Map addresses to function names

Use the provided `map_trace.py`.

Check its usage:

```bash
python3 map_trace.py
```

It should show:

```text
Usage: python3 map_trace.py <trace_file> <executable>
```

Run:

```bash
python3 map_trace.py \
  dynamic_traces/raw/test10.txt \
  fuzzing/fuzz_main \
  > dynamic_traces/named/test10.txt
```

View the named trace:

```bash
head -30 dynamic_traces/named/test10.txt
```

The output should look like:

```text
CALL   main
CALL   LLVMFuzzerTestOneInput
CALL   cJSON_ParseWithOpts
CALL   cJSON_ParseWithLengthOpts
CALL   cJSON_New_Item
RETURN cJSON_New_Item
CALL   skip_utf8_bom
RETURN skip_utf8_bom
CALL   buffer_skip_whitespace
...
```

---

## 11. Run the complete corpus

After confirming that one input works, run the same process for all experiment inputs.

Example shell loop:

```bash
for f in experiment_inputs/*; do
    name=$(basename "$f")
    ./fuzzing/fuzz_main "$f" \
        2> "dynamic_traces/raw/${name}.txt"

    python3 map_trace.py \
        "dynamic_traces/raw/${name}.txt" \
        fuzzing/fuzz_main \
        > "dynamic_traces/named/${name}.txt"
done
```

This produces:

```text
dynamic_traces/
├── raw/
│   ├── test1.txt
│   ├── test2.txt
│   └── ...
└── named/
    ├── test1.txt
    ├── test2.txt
    └── ...
```

---

## 12. Count distinct functions across all inputs

To see all functions dynamically reached across the complete corpus:

```bash
awk '{print $2}' dynamic_traces/named/*.txt | sort -u
```

To get only the number:

```bash
awk '{print $2}' dynamic_traces/named/*.txt | sort -u | wc -l
```

This gives the number of **distinct functions dynamically observed** across all inputs.

---

## 13. Check CALL/RETURN counts

For an individual trace:

```bash
grep -c "^CALL" dynamic_traces/named/test10.txt
grep -c "^RETURN" dynamic_traces/named/test10.txt
```

CALL and RETURN counts should match for a complete execution trace.

---

## 14. Generate execution statistics

The resulting named traces can be analyzed to obtain:

* Number of CALL events
* Number of RETURN events
* Total trace events
* Number of distinct functions reached
* Function call sequences
* Differences in execution behaviour between inputs

The traces represent **actual runtime function-level control flow** for each input.

---

## 15. Purpose of the experiment

The experiment is intended to compare:

```text
Static analysis
      ↓
Potential program behaviour

Dynamic analysis
      ↓
Actually observed execution behaviour
```

The collected CALL/RETURN traces will subsequently be converted into a **Context-Free Grammar (CFG)** representation for further analysis and learning.

## Important

Do not modify the original cJSON input corpus.

Use the separate `experiment_inputs/` directory for the modified/experiment versions.

The following files are provided separately with this guide:

```text
trace.c
map_trace.py
```

These are the main helper files required for reproducing the dynamic trace collection experiment.
