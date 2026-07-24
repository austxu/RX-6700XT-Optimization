# Release notes

## RX 6700 XT Llama 2 Vulkan optimization evidence

This public release packages the Llama 2 7B `Q4_0` results for opt-in
Navi22 Vulkan paths in `llama.cpp`: clean source replays, correctness gates,
two matched local benchmark campaigns, a sealed current-master negative, and
deterministic evidence analysis.

Results and artifacts for other model families remain preserved locally for
engineering continuity but are outside this release's result, evidence, and
repository scope. The published performance implementation is the checksummed
llama.cpp patch series.

### Included source profiles

- The nine-patch release profile applies to official llama.cpp
  `86d86ed4396b4130922f7b9af26e3d9fc11a591b` and reproduces final tree
  `181e8fccc75423329c07885b5b853dd92a0520b8`.
- The retained-a551 supplement applies after that profile and reproduces final
  tree `2d3add3e01638795ff1cdc45273375ff4f455b52`, byte-identical to benchmark
  commit `a551cb0142e68139f4ab953bf9233b4dbeefa4f3`.
- The current-master correctness profile applies ten checksummed patches to
  official llama.cpp
  `0cea36222fe9bac5ebfc45716c9eef11f37046c4` and reproduces candidate tree
  `2af9ba5958d30228c73faf8f918d4c30802a57ae` against paced-control tree
  `2cfe7d4bb10e1fd6a8e8e932072e9c24b8d92b2e`.
- Custom routes remain opt-in and preserve upstream fallback behavior outside
  their exact hardware and shape guards.

### Evidence highlights

- The nine-patch campaign improved FA-off `tg128` from 75.837 to 78.017 t/s
  (`+2.878%`) and FA-on `tg128` from 80.888 to 84.097 t/s (`+3.969%`).
- The retained-a551 campaign measured `85.709606` t/s FA-off and `89.665432`
  t/s FA-on at `tg128`, paired gains of `+13.928394%` and `+11.290309%` over
  its matched paced control. Its pp512 cells were neutral.
- Each campaign completed 12/12 guarded invocations and 336 raw samples.
  Their peaks were 93 C and 94 C, respectively, and every invocation restored
  the 186 W stock cap and automatic fan control.

The compact evidence snapshot contains two accepted Llama 2 campaigns, 24 raw
result JSON files, 672 raw samples, and eight independently regenerated rows.
It also contains the compact summary and source-seal binding for the final
sealed current-master Llama 2 correctness failure.

Every GPU invocation used the 174 W guarded protocol, forced PWM 255 while
running, a 95 C junction abort, matched cooling, Intel display routing,
exclusive RX 6700 XT access, and verified stock restoration.

### Current-master correctness result

The final Llama 2 root `llama2-20260724T065633Z` is a sealed **FAIL** with 12
CPU-versus-Vulkan failures. Matched control, candidate-default, and
candidate-enabled Vulkan outputs were byte-identical for FA-off and FA-on.
All ten guarded invocations exited zero, the peak was 45 C, and stock controls
were restored.

Correctness stopped this cutline before performance. No current-master screen,
full campaign, or other timing run was authorized or executed. The accepted
throughput rows remain historical results from their explicitly pinned source
profiles and must not be presented as current-master performance.

### Scoreboard claim boundary

The public target is the RX 6700 XT Llama 2 7B `Q4_0` FA-off `tg128` row at
`83.88 ± 0.08` t/s using llama.cpp `6d75883`. The guarded local recreation of
that historical source and protocol measured
`81.559936 ± 0.328402` t/s.

The nine-patch `84.097` t/s result is FA-on and not like-for-like with the
public FA-off row. The retained-a551 FA-off mean is numerically above the
public row but uses a different dated custom source tree. The scoreboard's
main post does not explicitly require master, but a later comment from
`llama.cpp` collaborator `0cc4m` says the thread is for master-branch
performance. The retained custom-source result is therefore outside the
scoreboard's stated scope unless a curator explicitly grants an exception.
These are author-operated matched local measurements, not an accepted
scoreboard submission, official record, independent reproduction, MLPerf
result, or general AMD-leadership claim.

### Reproduction and licensing

Run:

```bash
scripts/linux/reproduce_public_release.sh analysis
```

The command verifies checksums, recomputes all eight rows, byte-compares the
recomputed bytes with the tracked regenerated outputs, and verifies checksums
again. Default analysis does not rewrite the tracked evidence; the
author-side exporter writes the deterministic snapshot.

See `docs/REPRODUCING.md` for source replay, builds, and the requirements for a
fresh guarded Llama 2 reproduction attempt. Model weights are not
redistributed. This project's original code and documentation use the MIT
License; upstream llama.cpp notices and model terms remain separate.

### Publication state

This repository is the reader-facing source and evidence snapshot. Its
publication does not imply upstream inclusion or scoreboard acceptance. The
measured custom profiles remain outside the scoreboard's stated master-branch
scope unless a curator explicitly grants an exception.
