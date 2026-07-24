# RX 6700 XT Llama 2 Vulkan optimizations

On an AMD Radeon RX 6700 XT, the retained opt-in `llama.cpp` Vulkan profile
improved Llama 2 7B `Q4_0` generation (`tg128`) by **13.928% with flash
attention off** and **11.290% with flash attention on** versus its matched
paced control. Prompt processing (`pp512`) was statistically neutral:
`+0.004%` and `+0.015%`, with both 95% intervals crossing zero.

These are author-operated, matched measurements from a dated custom source
profile. They are not current-master results, an accepted scoreboard entry,
an independent reproduction, an MLPerf result, or a general AMD performance
claim.

This reader-facing release contains the checksummed source patches, compact raw
evidence, deterministic analysis, source/build instructions, and the sealed
negative result from a later current-master correctness cutline. Model weights
are not included.

## Results

Each row contains 84 raw samples: three independent `A1 B1 B2 A2` cycles with
seven samples per invocation. Intervals are deterministic paired 95%
hierarchical-bootstrap intervals with 100,000 replicates.

| Source profile and cell | Control t/s | Candidate t/s | Paired gain | 95% CI |
| --- | ---: | ---: | ---: | ---: |
| Nine-patch, FA-off pp512 | 1236.773 | 1237.596 | +0.067% | [+0.018%, +0.114%] |
| Nine-patch, FA-off tg128 | 75.837 | 78.017 | +2.878% | [+1.944%, +3.493%] |
| Nine-patch, FA-on pp512 | 1271.995 | 1271.524 | -0.037% | [-0.082%, +0.019%] |
| Nine-patch, FA-on tg128 | 80.888 | 84.097 | +3.969% | [+3.314%, +4.644%] |
| Retained-a551, FA-off pp512 | 1237.031 | 1237.083 | +0.004% | [-0.040%, +0.054%] |
| Retained-a551, FA-off tg128 | 75.231 | 85.710 | +13.928% | [+13.656%, +14.193%] |
| Retained-a551, FA-on pp512 | 1272.243 | 1272.429 | +0.015% | [-0.090%, +0.093%] |
| Retained-a551, FA-on tg128 | 80.569 | 89.665 | +11.290% | [+10.908%, +11.716%] |

The strongest retained absolute means were `85.709606` t/s FA-off and
`89.665432` t/s FA-on. Its 12/12 guarded invocations produced 336 raw samples,
peaked at 94 C below the 95 C abort threshold, and restored the 186 W stock
cap and automatic fan after every invocation. The compact release evidence
contains both accepted campaigns: 24 raw result records, 672 raw samples, and
eight regenerated rows.

See [Results](docs/RESULTS.md) for the complete interpretation and
[Methodology](docs/METHODOLOGY.md) for the correctness, thermal, and
statistical gates.

## Scoreboard boundary

The historical comparison is the RX 6700 XT row in the
[`llama.cpp` Vulkan discussion](https://github.com/ggml-org/llama.cpp/discussions/10879):
Llama 2 7B `Q4_0`, FA-off, `tg128`, `83.88 ± 0.08` t/s at llama.cpp
`6d758839ff741d4966ca92b7f801b7a8b5b96364`. A guarded local recreation of
that source and workload measured `81.559936 ± 0.328402` t/s; it does not
revise or independently reproduce the posted row.

The discussion's main post asks contributors to clone and build `llama.cpp`
and report the Git hash and Vulkan information, but it does not explicitly say
“master only.” In a later comment, `llama.cpp` collaborator `0cc4m`
[said](https://github.com/ggml-org/llama.cpp/discussions/10879#discussioncomment-17557303)
that the thread is for master-branch performance. The retained custom-source
result is therefore outside the scoreboard's stated scope unless a curator
explicitly grants an exception.

Some checksum-bound historical `analysis.json` files retain the categorical
“master-only” wording used when those campaigns were sealed. They remain
byte-for-byte unchanged as historical evidence; the interpretation above and
the current evidence index are the corrected policy statement.

Accordingly, the retained FA-off mean is only a local matched result that is
numerically above the historical row. This repository does not describe it as
an official result or record.

## Three reader paths

### 1. Verify the published numbers

No model or GPU is required:

```bash
scripts/linux/reproduce_public_release.sh analysis
```

This verifies every compact-evidence checksum, recomputes all eight rows and
their confidence intervals, byte-compares the regenerated outputs, and
verifies the checksums again without changing the evidence tree.

### 2. Reconstruct and build the exact source

The nine-patch campaign has a one-command source/build verifier:

```bash
scripts/linux/build_public_llamacpp.sh
```

For the strongest retained profile, start from a clean checkout at the pinned
official base and apply the retained package:

```bash
git clone https://github.com/ggml-org/llama.cpp.git \
  external/llama.cpp-retained-a551
git -C external/llama.cpp-retained-a551 checkout \
  86d86ed4396b4130922f7b9af26e3d9fc11a591b
git -C external/llama.cpp-retained-a551 switch -c retained-a551-reproduction
scripts/apply_llamacpp_navi22_retained_a551.sh \
  external/llama.cpp-retained-a551
```

The apply script verifies both patch manifests and the exact final Git tree
`2d3add3e01638795ff1cdc45273375ff4f455b52`, which is byte-identical to the
benchmarked source tree. [Reproducing](docs/REPRODUCING.md) includes the build
command and identifies the separately pinned current-master patch tree.

### 3. Run a new hardware recreation

The public package does not claim a one-command, bit-for-bit replay of the
historical full campaigns. Those author runs bind exact historical checkout
identities, binaries, ignored correctness roots, and machine-specific guarded
telemetry. The raw accepted samples, manifests, protocols, and analysis are
published; a new hardware run should be reported as a fresh reproduction
attempt, not as a continuation of an old campaign.

The exact model identity, workload, opt-in route variables, and hardware-safety
requirements are in [Reproducing](docs/REPRODUCING.md). Every RX 6700 XT GPU
run must be serialized and guarded with a 174 W run cap, forced PWM 255, a
95 C junction abort, frequent polling, symmetric cooling, Intel display
routing, and verified restoration to the 186 W stock cap and automatic fan.

## Final current-master cutline

The final correctness-only cutline used official llama.cpp master
`0cea36222fe9bac5ebfc45716c9eef11f37046c4`. All ten guarded invocations
completed and peaked at 45 C. Matched control, candidate-default, and
candidate-enabled Vulkan outputs were byte-identical for both FA modes, but
the predeclared CPU-versus-Vulkan numerical gates failed, producing a sealed
12-failure decision.

Because control and candidate Vulkan outputs were identical, this does not
show a candidate-caused regression. It does mean the predeclared correctness
contract did not authorize timing. No current-master performance screen or
campaign was run, and none of the historical results above may be relabeled as
current-master performance. The negative summary is included in
[the compact evidence](release/evidence/negative-results/current-master/llama2/summary.json).

## Repository map

- [`patches/`](patches) contains the checksummed llama.cpp source profiles and
  preserved upstream license notices.
- [`scripts/`](scripts) contains patch application, source/build, and
  deterministic analysis tools.
- [`release/evidence/`](release/evidence) contains the compact, path-sanitized
  accepted samples and current-master negative.
- [`release/protocols/`](release/protocols) contains the dated public
  scoreboard workload snapshot.
- [`docs/RESULTS.md`](docs/RESULTS.md),
  [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md),
  [`docs/REPRODUCING.md`](docs/REPRODUCING.md), and
  [`docs/LIMITATIONS.md`](docs/LIMITATIONS.md) define the public claims and
  their boundaries.
- [`docs/PUBLIC_RELEASE_MODELS.md`](docs/PUBLIC_RELEASE_MODELS.md) pins the
  Llama 2 model URL, size, hash, and terms.

## Licensing

The repository's original code and documentation use the
[MIT License](LICENSE). The patch files preserve upstream llama.cpp copyright
and licensing notices; this license does not replace upstream licensing or
model terms. See [Third-party notices](THIRD_PARTY_NOTICES.md). Model weights
are not included.
