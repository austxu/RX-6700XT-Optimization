# Limitations

This publication reports only Llama 2 7B `Q4_0` measurements that passed the
repository's historical correctness, provenance, thermal, and statistical
gates. It does not claim a global optimum, general AMD leadership, an official
public-scoreboard record, MLPerf results, or independent reproduction.
Locally preserved work for other model families is outside this publication's
result and evidence scope.

## Public target boundary

The headline target is the public RX 6700 XT Vulkan scoreboard row for Llama 2
7B `Q4_0`, no flash attention, `tg128`: `83.88 ± 0.08` tokens/s at llama.cpp
commit `6d758839ff741d4966ca92b7f801b7a8b5b96364`. The local recreation of that
historical source and protocol measured `81.559936 ± 0.328402` tokens/s. The
public reference is the
[`llama.cpp Vulkan discussion`](https://github.com/ggml-org/llama.cpp/discussions/10879).
The local measurement is a recreation, not an independent reproduction,
public-record result, or revision of the posted row.

The first custom campaign's `84.097` t/s value uses flash attention and cannot
be compared directly with the public FA-off row. Its absolute candidate
interval was `[83.753, 84.356]` t/s, so its lower bound did not clear the
repository's `83.96` authorization threshold.

The retained-a551 campaign is the strongest measured Llama 2 result in this
repository: `85.709606` t/s FA-off and `89.665432` t/s FA-on. Those paired
gains are relative to a matched paced control rooted at `86d86ed4`. Although
its FA-off mean is numerically above the historical posted row, it comes from
a different dated custom source tree.

The discussion's main post does not explicitly state a master-only rule. A
later commenter, whom GitHub identifies as `llama.cpp` collaborator `0cc4m`,
[says](https://github.com/ggml-org/llama.cpp/discussions/10879#discussioncomment-17557303)
the thread is for master-branch performance. The retained custom-source result
is outside the scoreboard's stated scope unless a curator explicitly grants an
exception. Neither campaign is an accepted scoreboard submission, official
record, or independent reproduction.

## Final current-master boundary

The final correctness pass used official llama.cpp master
`0cea36222fe9bac5ebfc45716c9eef11f37046c4`. The Llama 2 root
`llama2-20260724T065633Z` is a sealed **FAIL** with 12 CPU-versus-Vulkan
failures. Matched control, candidate-default, and candidate-enabled Vulkan
outputs were byte-identical for both FA modes, but the CPU comparisons exceeded
the fixed NMSE and maximum-error gates and differed in top-10 membership.

All ten guarded invocations exited zero, the root peaked at 45 C, and the
186 W stock cap and automatic fan were restored. Those facts establish safe,
complete execution; they do not override numerical correctness.

The historical accepted measurements remain valid for their exact dated source
profiles, but their passes cannot be carried forward to a changed upstream
graph. No current-master timing was authorized or run, and no historical
throughput row may be relabeled as current-master performance.

## Alternative runtimes

Alternative runtimes were not placed in the matched table because model bytes,
quantization formats, harness boundaries, or software availability did not
support an equivalent comparison.

| Runtime | Exact Llama 2 Q4_0 GGUF | Matched timing boundary | Disposition |
| --- | --- | --- | --- |
| Pinned llama.cpp control and candidate | Yes | Yes | The only matched performance table |
| KoboldCpp | Potentially | No | No cross-runtime throughput claim; its application-level benchmark is not `llama-bench` pp512/tg128 |
| MLC LLM | No | No | Converted weights and a different quantization family would be a separate experiment |
| ROCm/HIP path | Potentially | No | Not run; no result claimed |
| MLPerf Inference | Not applicable | No | No LoadGen, accuracy, performance, or compliance run was performed |

Changing an alternative runtime to emulate the repository harness would no
longer measure that unmodified runtime. Conversely, comparing its native
end-to-end boundary with isolated `llama-bench` pp512 or tg128 would not be
like-for-like. Any future cross-runtime study needs its own model-identity,
quality, timing, and reporting contract.

`llama-bench` token throughput is not MLPerf. This work used no approved
MLPerf dataset, quality target, LoadGen scenario, or compliance process.

## Result scope

- All measurements are from one author-operated RX 6700 XT system. There is no
  independent reproduction.
- The compact publication snapshot contains two accepted Llama 2 campaigns,
  24 raw result records, 672 raw samples, eight regenerated rows, and the
  sealed current-master Llama 2 negative.
- The `pp512` rows describe prompt processing and must not be presented as
  generation speed. The `tg128` rows describe generation under the recorded
  harness.
- The earlier `84.097` t/s result is FA-on and not directly comparable to the
  public FA-off row.
- The retained-a551 FA-off result is numerically above the public row but is
  from a custom source profile outside the scoreboard's stated master-branch
  scope unless a curator explicitly grants an exception.
- The 45 C current-master correctness peak is guard evidence, not a benchmark
  thermal or performance sample.
- Thermals, drivers, clocks, model files, and software revisions materially
  affect these numbers. Comparisons using different models, quantizations,
  commits, flags, or timing boundaries are invalid.
- The broadest supported claim is limited to the two named implementations
  tested by the author on this card under their dated published protocols.
