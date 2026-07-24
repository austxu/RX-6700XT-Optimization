# Verifying and rebuilding the Llama 2 release

This public package supports two complete, clean-clone workflows:

1. deterministic verification of every published result row; and
2. reconstruction and compilation of the exact patched llama.cpp source
   trees.

It also provides the model identity, workload, source manifests, and hardware
protocol needed for a fresh RX 6700 XT reproduction attempt. It does **not**
claim that the author-operated historical campaigns can be replayed
bit-for-bit from a clean clone with one command. Those runs bind exact
historical control commits, binaries, ignored correctness roots, machine
paths, and guarded telemetry. The accepted raw samples and the information
needed to audit them are published instead.

Only Llama 2 7B `Q4_0` results are in scope.

## 1. Verify every published result

From the repository root:

```bash
scripts/linux/reproduce_public_release.sh analysis
```

This read-only command:

1. verifies `release/evidence/SHA256SUMS`;
2. reads the 24 accepted result records and 672 raw samples;
3. recomputes all eight rows and their 100,000-replicate paired
   hierarchical-bootstrap intervals;
4. byte-compares the recomputed `results.json` and `results.md` with the
   tracked outputs under `release/evidence/regenerated`; and
5. verifies the evidence checksums again.

A stale, missing, or mutated file fails closed. No model, GPU, network access,
or author-only artifact directory is required.

The expected inventory is two accepted campaigns, 24 raw result records, 672
raw samples, eight result rows, and the compact sealed current-master Llama 2
correctness failure.

## 2. Reconstruct the strongest retained source

The retained-a551 package is the source behind the `+13.928%` FA-off and
`+11.290%` FA-on `tg128` results.

Prerequisites are Git, CMake, Ninja, a C/C++ toolchain, Vulkan headers and
loader, `glslc`, and `spirv-val`.

Start with a clean checkout at the exact official base:

```bash
git clone https://github.com/ggml-org/llama.cpp.git \
  external/llama.cpp-retained-a551
git -C external/llama.cpp-retained-a551 checkout \
  86d86ed4396b4130922f7b9af26e3d9fc11a591b
git -C external/llama.cpp-retained-a551 switch -c retained-a551-reproduction
scripts/apply_llamacpp_navi22_retained_a551.sh \
  external/llama.cpp-retained-a551
```

The application script checks both patch manifests, verifies the intermediate
nine-patch tree, and requires final tree
`2d3add3e01638795ff1cdc45273375ff4f455b52`. That tree is byte-identical to
benchmarked commit `a551cb0142e68139f4ab953bf9233b4dbeefa4f3`; the locally
created commit ID may differ because `git am` records local committer metadata.

Build the retained tree:

```bash
cmake -S external/llama.cpp-retained-a551 \
  -B external/llama.cpp-retained-a551/build-release -GNinja \
  -DCMAKE_BUILD_TYPE=Release \
  -DGGML_VULKAN=ON \
  -DGGML_NATIVE=ON \
  -DGGML_BACKEND_DL=OFF \
  -DLLAMA_BUILD_TESTS=ON \
  -DLLAMA_CURL=OFF
cmake --build external/llama.cpp-retained-a551/build-release \
  --target llama-bench llama-debug test-backend-ops
```

Before interpreting the build, confirm that the source tree is still exact:

```bash
git -C external/llama.cpp-retained-a551 diff --check
git -C external/llama.cpp-retained-a551 rev-parse HEAD^{tree}
```

The second command must print
`2d3add3e01638795ff1cdc45273375ff4f455b52`.

## 3. Reconstruct the other pinned profiles

### Nine-patch campaign

The first accepted campaign has a one-command source/build verifier:

```bash
scripts/linux/build_public_llamacpp.sh
```

It clones official llama.cpp when needed, checks out
`86d86ed4396b4130922f7b9af26e3d9fc11a591b`, applies the checksummed
nine-patch series, requires final tree
`181e8fccc75423329c07885b5b853dd92a0520b8`, builds Vulkan and
Vulkan-disabled CPU targets, and validates the four added SPIR-V modules.
It does not run a model benchmark.

For source-only application:

```bash
git clone https://github.com/ggml-org/llama.cpp.git \
  external/llama.cpp-nine-patch
git -C external/llama.cpp-nine-patch checkout \
  86d86ed4396b4130922f7b9af26e3d9fc11a591b
git -C external/llama.cpp-nine-patch switch -c nine-patch-reproduction
scripts/apply_llamacpp_navi22_patches.sh external/llama.cpp-nine-patch
```

### Current-master correctness-only cutline

The later cutline is pinned to official llama.cpp
`0cea36222fe9bac5ebfc45716c9eef11f37046c4`, as fetched on 2026-07-24.
The checksummed source-only package is
`patches/llama.cpp-navi22-retained-0cea36222/`, with application helper
`scripts/apply_llamacpp_navi22_retained_0cea36222.sh`. Its full candidate tree
is
`2af9ba5958d30228c73faf8f918d4c30802a57ae`. The sealed historical cutline
failed the fixed CPU-versus-Vulkan numerical gates even though matched control,
candidate-default, and candidate-enabled Vulkan outputs were byte-identical.
That failure prohibited timing. There is no current-master performance result
to reproduce or compare.

## 4. Prepare a fresh hardware reproduction

### Model identity

Obtain `llama-2-7b.Q4_0.gguf` under its upstream terms and verify it before
loading:

```text
bytes   3825807040
sha256  78b8f9777dd620ad29cd2cffb6653b17fa8a5b1fddc1b8821180d60eedd24d48
```

The immutable source revision and model terms are in
[the model registry](PUBLIC_RELEASE_MODELS.md). Weights are not redistributed.

### Workload

The public discussion's basic workload is:

```text
llama-bench -m llama-2-7b.Q4_0.gguf -ngl 100 -fa 0,1
```

This line defines the benchmark workload; it is not a safe standalone GPU
invocation. The dated public reference, source commit, and all four posted
RX 6700 XT values are preserved in
[`release/protocols`](../release/protocols).

The retained candidate used these opt-in routes:

```bash
export GGML_VK_Q4_0_MMVQ_NAVI22=1
export GGML_VK_Q4_0_MULTIPROJ_NAVI22=1
export GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22=1
export GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22_MODE=direct
export GGML_VK_FLASH_ATTN_Q8_1_NAVI22=1
export GGML_VK_Q4_0_MMVQ_NAVI22_ROWS1_SHAPE=down
export GGML_VK_Q4_0_DOWN_PREFETCH_NAVI22=1
export GGML_VK_F16_ATTN_NAVI22_MODE=p021
export GGML_VK_F16_ATTN_MMV_NAVI22_ROWS=8
export GGML_VK_POST_QKV_FUSION_NAVI22=1
export GGML_VK_FA_MASKED_SPLIT_NAVI22=1
```

Do not set `GGML_VK_FORCE_MMVQ`. The exact accepted campaign configuration is
in
[`release/evidence/campaigns/llama2-retained-a551/campaign.txt`](../release/evidence/campaigns/llama2-retained-a551/campaign.txt).

### Safety and comparison contract

Every RX 6700 XT GPU process used for a comparable result must run alone and
under a fail-closed guard with:

- the display connected to the Intel GPU;
- a 174 W run cap and PWM 255 while running;
- a 95 C junction abort with 0.05-second polling;
- identical cooling for control and candidate;
- exclusive RX locking; and
- trap-based restoration to the 186 W stock cap and automatic fan control.

Correctness precedes timing. A fresh reproduction must first validate its exact
source tree, model hash, built binaries, SPIR-V modules, route activation,
finite outputs, and its declared numerical/token gates. Invalid, overlapping,
correctness-failing, or thermal-aborted runs do not enter statistics.

For a matched statistical recreation, use three independent `A1 B1 B2 A2`
cycles, seven repetitions per invocation, and keep pp512/tg128 and FA-off/on as
separate cells. Publish every sample. The analysis uses cycle-paired means and
100,000 deterministic hierarchical-bootstrap replicates.

Because the clean public package does not automate this full machine-specific
campaign, a reproducer must record the new source commits, binary hashes,
driver state, device routing, commands, cooling, and telemetry as a new
experiment. Do not append new samples to the historical evidence or present a
fresh run as a bit-for-bit replay.

## 5. Interpret the scoreboard comparison

The main discussion post does not explicitly state a master-only rule. A later
comment from `llama.cpp` collaborator `0cc4m`
[says](https://github.com/ggml-org/llama.cpp/discussions/10879#discussioncomment-17557303)
the thread is for master-branch performance. The retained custom-source result
is outside the scoreboard's stated scope unless a curator explicitly grants an
exception.

The retained FA-off mean is numerically above the historical `83.88` t/s row,
but it remains a dated, matched custom-source result. It is not an accepted
scoreboard result or record. See [Limitations](LIMITATIONS.md) for the complete
claim boundary.
