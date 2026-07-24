# Llama 2 results

The strongest retained profile improved Llama 2 7B `Q4_0` `tg128` by
`+13.928%` FA-off and `+11.290%` FA-on over its matched paced control on an
author-operated RX 6700 XT. Its `pp512` changes were statistically neutral:
`+0.004%` and `+0.015%`, with both 95% intervals crossing zero.

These are dated, matched custom-source measurements. They are not
public-record, MLPerf, cross-model, current-master, or independent-reproduction
claims. Throughput is tokens/second.

Each published row contains 84 raw samples: three independent
`A1 B1 B2 A2` cycles with seven samples per invocation. Intervals are paired
95% hierarchical-bootstrap intervals with 100,000 deterministic replicates.
Results for other model families remain preserved locally but are outside this
publication's result and evidence scope.

## Public target recreation

The target was the RX 6700 XT row in the public
[`llama.cpp Vulkan scoreboard`](https://github.com/ggml-org/llama.cpp/discussions/10879):
Llama 2 7B `Q4_0`, no flash attention (`FA-off`), `tg128`,
`83.88 ± 0.08` tokens/s, using llama.cpp commit
`6d758839ff741d4966ca92b7f801b7a8b5b96364`.

The exact local model is 3,825,807,040 bytes with SHA-256
`78b8f9777dd620ad29cd2cffb6653b17fa8a5b1fddc1b8821180d60eedd24d48`.
The guarded recreation of that historical source and protocol measured
`81.559936 ± 0.328402` tokens/s. The public value and local value must remain
separate: this documents a recreation of the target, not an independent
reproduction or accepted scoreboard submission.

## Accepted campaigns

The two accepted campaigns use separately pinned source profiles. They are
preserved historical evidence and are not performance measurements from the
final current-master cutline.

| Source profile | Cell | Control t/s | Candidate t/s | Paired gain | 95% gain CI | Decision |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| Nine-patch | FA-off pp512 | 1236.773 | 1237.596 | +0.067% | [+0.018%, +0.114%] | statistical, not practical |
| Nine-patch | FA-off tg128 | 75.837 | 78.017 | +2.878% | [+1.944%, +3.493%] | practical win |
| Nine-patch | FA-on pp512 | 1271.995 | 1271.524 | -0.037% | [-0.082%, +0.019%] | neutral |
| Nine-patch | FA-on tg128 | 80.888 | 84.097 | +3.969% | [+3.314%, +4.644%] | practical win |
| Retained-a551 | FA-off pp512 | 1237.031 | 1237.083 | +0.004% | [-0.040%, +0.054%] | neutral |
| Retained-a551 | FA-off tg128 | 75.231 | 85.710 | +13.928% | [+13.656%, +14.193%] | practical win vs matched control |
| Retained-a551 | FA-on pp512 | 1272.243 | 1272.429 | +0.015% | [-0.090%, +0.093%] | neutral |
| Retained-a551 | FA-on tg128 | 80.569 | 89.665 | +11.290% | [+10.908%, +11.716%] | practical win vs matched control |

The strongest retained local decode means are `85.709606` t/s FA-off and
`89.665432` t/s FA-on. That campaign completed 12/12 guarded invocations and
336 raw samples, peaked at 94 C, and restored stock controls after every
invocation.

## Scoreboard interpretation

The nine-patch campaign's `84.097` t/s value is FA-on; it is not a
like-for-like comparison with the public FA-off row. Its absolute candidate
interval was `[83.753, 84.356]` t/s, so its lower bound also did not exceed the
repository's `83.96` authorization threshold.

The retained-a551 FA-off mean of `85.709606` t/s is numerically above the
posted `83.88` t/s row, but it was measured from a different dated custom
source tree against its own matched paced control. The discussion's main post
does not explicitly state a master-only rule. A later commenter, whom GitHub
identifies as `llama.cpp` collaborator `0cc4m`,
[says](https://github.com/ggml-org/llama.cpp/discussions/10879#discussioncomment-17557303)
the thread is for master-branch performance. The retained custom-source result
is outside the scoreboard's stated scope unless a curator explicitly grants an
exception. Neither campaign is an accepted scoreboard result or record.

For context only, the historical scoreboard commit recreated locally at
`81.559936` t/s and exact then-current upstream measured `75.907` t/s FA-off
under the same stricter guard. These reference runs are not substituted into
the paired campaign statistics and do not revise the posted scoreboard row.

## Final current-master correctness cutline

The final cutline used official llama.cpp master
`0cea36222fe9bac5ebfc45716c9eef11f37046c4`. Its sealed Llama 2 root is
`artifacts/public-release/current-master/correctness/llama2-20260724T065633Z`.
All ten guarded invocations completed (four focused graph gates and six
full-model Vulkan roles), every process exited zero, the peak was 45 C, and
the 186 W stock cap and automatic fan control were restored.

For both FA modes, the matched control, candidate-default, and
candidate-enabled Vulkan token and logit outputs were byte-identical. The
fixed CPU-versus-Vulkan gates nevertheless failed:

| FA mode | CPU-vs-Vulkan NMSE | Maximum absolute error | Top-10 |
| --- | ---: | ---: | --- |
| off | 0.0011588587 | 0.2664886 | differs |
| on | 0.0012161039 | 0.2874110 | differs |

Applying those three failures to both candidate-default and candidate-enabled
comparisons produced 12 failures. The sealed decision is **FAIL**.
`files.sha256` has SHA-256
`78dac576e71305ee1810772cd0e9c499769a24178d23df545121d055157d24c2`;
`summary.json` has SHA-256
`13543e2e55c4bf4fb53f82b71ba524814c98cc7eb0939578e56e38ca6e723a9f`.

Correctness stopped the cutline before performance. No current-master screen,
full campaign, or other timing run was authorized or executed. The accepted
historical rows above must not be presented as current-master performance.

## Publication evidence

The compact, path-sanitized snapshot contains two accepted Llama 2 campaigns,
24 raw invocation result records, 672 raw samples, and eight regenerated
result rows. It also contains the compact summary and source-seal binding for
the sealed current-master Llama 2 correctness failure. See the
[`summary.json`](../release/evidence/negative-results/current-master/llama2/summary.json)
and the full
[`release/evidence`](../release/evidence).

Verify the tracked snapshot without changing it:

```bash
scripts/linux/reproduce_public_release.sh analysis
```

The command verifies the evidence checksums, recomputes every row and
confidence interval, byte-compares the recomputed outputs with the tracked
regenerated files, and verifies the checksums again. Alternative runtimes were
not placed in the matched table because their timing boundaries were not
equivalent; see [`docs/LIMITATIONS.md`](LIMITATIONS.md).
