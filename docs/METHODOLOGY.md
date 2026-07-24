# Llama 2 benchmark methodology

## Scope and test system

This publication reports only Llama 2 7B `Q4_0` results. Other model-family
artifacts remain preserved locally for engineering continuity but are outside
the publication result and evidence scope.

The accepted measurements were collected from 2026-07-17 through 2026-07-21
on one AMD Radeon RX 6700 XT (`1002:73df`, Navi22) used only for compute. The
connected display remained on Intel UHD Graphics 770. The captured environment
was Ubuntu 26.04, kernel 7.0.0-27, Mesa/RADV 26.0.3, Vulkan loader 1.4.341,
GCC 15.2, CMake 4.2.3, shaderc 2026.1, and SPIRV-Tools 2026.1. The complete
sanitized manifest is
[`release/evidence/hardware/hardware-manifest.txt`](../release/evidence/hardware/hardware-manifest.txt).

This is a single-system, author-operated study. It does not establish
performance on other Navi22 boards, drivers, operating systems, models, or
quantizations and is not an independent reproduction.

## Source and model

The exact GGUF input is Llama 2 7B `Q4_0`, 3,825,807,040 bytes, SHA-256
`78b8f9777dd620ad29cd2cffb6653b17fa8a5b1fddc1b8821180d60eedd24d48`.
Its immutable source and terms are recorded in
[`docs/PUBLIC_RELEASE_MODELS.md`](PUBLIC_RELEASE_MODELS.md). Model weights are
not included in the repository or release assets.

Both accepted campaigns descend from official llama.cpp
`86d86ed4396b4130922f7b9af26e3d9fc11a591b` and use the matched paced control
`c7ed0c9ae5e42d8c926658c884a214f73ef204de`. The benchmark pacing is outside
the timed region and is identical for control and candidate.

The first accepted candidate is
`6b66b2e2f7b3b04ab84b2b498ab63127ced5826a`. The checksummed nine-patch
publication profile has final tree
`181e8fccc75423329c07885b5b853dd92a0520b8`, byte-identical to that accepted
performance candidate.

The retained-a551 campaign uses candidate
`a551cb0142e68139f4ab953bf9233b4dbeefa4f3`. Its checksummed supplemental
profile reproduces final tree
`2d3add3e01638795ff1cdc45273375ff4f455b52`, byte-identical to the benchmarked
candidate.

The final correctness-only pre-publication port is separately pinned to
official llama.cpp master
`0cea36222fe9bac5ebfc45716c9eef11f37046c4`, paced control
`39b3a38e3cc3bb30f787fba8c53e9bea65b68768`, and candidate
`d019b2bfe0d3f7d4ff16ed1564ae53b48f24baef`. Its negative correctness result
is not combined with the historical throughput campaigns.

## Candidate routes

The Llama 2 path is opt-in. The nine-patch candidate combines:

- a two-row Q4_0 × Q8_1 MMVQ route;
- grouped QKV and FFN multi-projection launches; and
- a flash-attention Q8_1 sidecar.

The retained-a551 supplement adds the exact later Llama 2 route stack captured
by its campaign manifest. Defaults remain inert, and unsupported hardware or
shapes fall back to upstream behavior. The patch set also preserves broader
engineering code needed by its source history, but this publication makes no
performance claim from that code outside Llama 2 `Q4_0`.

## Correctness before performance

No candidate advanced to full timing before the applicable gates passed:

- clean Release Vulkan and Vulkan-disabled CPU builds;
- `git diff --check` and `spirv-val` for every added shader;
- default-off behavior and exact enabled-route coverage;
- deterministic operation-level boundary and partial-shape tests;
- finite outputs, token equality, argmax/top-10 equality, and fixed numerical
  limits where byte identity was not expected;
- same-build byte-identical tokens and logits for the accepted Llama 2
  oracles; and
- audits of shape guards, barriers, scratch lifetime, and subgroup
  assumptions.

The nine-patch source passed 22/22 CPU and 22/22 Vulkan graph cases, 5/5 CPU
and 5/5 Vulkan attention cases, and byte-identical token and logit artifacts.
Its accepted route audit recorded 224 Q4_0 dispatches, 62 grouped
multi-projection launches covering 156 logical projections, and 31
produced/consumed attention sidecars from 32 structural opportunities. The
committed summary is
[`release/evidence/correctness/final-summary.txt`](../release/evidence/correctness/final-summary.txt).

The retained-a551 source independently passed 22/22 CPU and 22/22 Vulkan
whole-graph cases, its attention and route-specific suites, and byte-identical
token/logit oracles. Its summary is
[`release/evidence/correctness/retained-a551-summary.txt`](../release/evidence/correctness/retained-a551-summary.txt);
the source seal is bound by the evidence index.

### Final current-master cutline

The final current-master cutline added a full-model CPU-versus-Vulkan gate.
The sealed root
`artifacts/public-release/current-master/correctness/llama2-20260724T065633Z`
completed ten guarded invocations: four focused graph gates and six full-model
Vulkan roles. Every process exited zero. For both FA modes, the matched
control, candidate-default, and candidate-enabled Vulkan token and logit
outputs were byte-identical.

The CPU-versus-Vulkan comparisons nevertheless exceeded the fixed `2e-7`
NMSE and `0.007` maximum-error limits and differed in top-10 membership:

| FA mode | NMSE | Maximum absolute error |
| --- | ---: | ---: |
| off | 0.0011588587 | 0.2664886 |
| on | 0.0012161039 | 0.2874110 |

The repeated default/enabled comparisons produced 12 failures and a sealed
**FAIL** decision. Correctness-before-performance prohibited a current-master
screen or full campaign, so no current-master timing was authorized or run.

## Thermal and routing controls

Every GPU process ran through `scripts/linux/run_with_thermal_guard.sh` under
an exclusive inherited `flock`. The fail-closed policy was:

- 174,000,000 µW run power cap;
- PWM 255 while running and a 2-second settle;
- 95,000 m°C junction abort with 0.05-second polling;
- identical cooling gates for A and B;
- no display connected to the RX 6700 XT; and
- trap-based restoration to 186,000,000 µW and automatic fan control.

Malformed, correctness-failing, incomplete, or thermally aborted runs were
excluded and never reused. The nine-patch Llama 2 campaign peaked at 93 C and
the retained-a551 campaign peaked at 94 C. Every accepted invocation verified
restoration. The final current-master correctness-only root peaked at 45 C
and also restored stock controls; that peak is guard evidence, not a
performance sample.

## Timing and statistics

Each published cell consists of three independent cycles in fixed
`A1 B1 B2 A2` order, where A is matched control and B is candidate. Each
invocation contains seven `llama-bench` repetitions and emits JSON. The
analyzers validate model identity, commits, patch bytes, binaries, flags,
device, route counts, raw timing arithmetic, process non-overlap, cooling
tail, telemetry, and restoration before accepting a sample.

For each cycle, the two A means and two B means are averaged and their ratio is
computed. The paired gain is the arithmetic mean of the three cycle ratios
minus one. The 95% interval uses 100,000 deterministic hierarchical-bootstrap
replicates: cycles are resampled, then the seven observations within each
selected slot are resampled. A statistical win requires every cycle to favor
B and a gain interval wholly above zero. A practical win also requires a mean
gain of at least 1%. Prompt-processing results are reported separately from
generation.

The compact publication snapshot contains two campaigns, 24 raw result JSON
files, 672 raw samples, and eight result rows. The release analyzer recomputes
all eight rows from those samples and byte-compares the result with the
tracked regenerated output.
