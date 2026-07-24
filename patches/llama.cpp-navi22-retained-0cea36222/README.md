# Current-master retained Navi22 patch series

This directory pins the clean current-master port of the validated RX 6700 XT
Navi22 work. It combines the historical nine-patch release series with the
retained Llama 2 supplement as ten reviewable commits on official llama.cpp
master `0cea36222fe9bac5ebfc45716c9eef11f37046c4`, frozen at
2026-07-24 06:16 UTC.

## Exact source pins

| Role | Branch | Commit | Git tree |
| --- | --- | --- | --- |
| Official upstream / pure control | `navi22/control-0cea36222` | `0cea36222fe9bac5ebfc45716c9eef11f37046c4` | `3514d2f9359eb40f4a68890e3fa1337be1357187` |
| Pacing-only benchmark control | `navi22/paced-control-0cea36222` | `39b3a38e3cc3bb30f787fba8c53e9bea65b68768` | `2cfe7d4bb10e1fd6a8e8e932072e9c24b8d92b2e` |
| Full retained candidate | `navi22/retained-port-0cea36222` | `d019b2bfe0d3f7d4ff16ed1564ae53b48f24baef` | `2af9ba5958d30228c73faf8f918d4c30802a57ae` |

Replayed commit IDs may differ because `git am` supplies a new committer
timestamp. The verified Git tree is the source identity.
The one-command current-master builder supplies the recorded committer
metadata and additionally requires the exact pinned commit IDs.

Patch `0003-llama-bench-add-guarded-depth-prefill-pacing.patch` is intentionally
separate from the nine production/test commits. It changes only
`tools/llama-bench/llama-bench.cpp`, is inert unless its depth-pacing
environment variables are set, and can be applied alone to produce a
source-matched d4096 benchmark control.

## Apply and verify

Start from a clean checkout at the exact official base, then run one of:

```bash
scripts/apply_llamacpp_navi22_retained_0cea36222.sh /path/to/llama.cpp paced-control
scripts/apply_llamacpp_navi22_retained_0cea36222.sh /path/to/llama.cpp full
```

The script verifies the patch checksums, exact base commit/tree, clean checkout,
patch count and order, pacing isolation, changed-file allowlist, final tree, and
clean post-application state.

## Default-inert activation

All custom GPU routes remain off when their environment variables are unset.
The pacing code is also inactive unless its three depth-prefill variables are
set. Never set `GGML_VK_FORCE_MMVQ` for an official run.

The accepted Q4_K_M route uses:

```bash
GGML_VK_Q4_K_MMVQ_NAVI22=1
GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22=1
GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22_MODE=direct
```

The retained Llama 2 Q4_0 route uses:

```bash
GGML_VK_Q4_0_MMVQ_NAVI22=1
GGML_VK_Q4_0_MULTIPROJ_NAVI22=1
GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22=1
GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22_MODE=direct
GGML_VK_FLASH_ATTN_Q8_1_NAVI22=1
GGML_VK_Q4_0_MMVQ_NAVI22_ROWS1_SHAPE=down
GGML_VK_Q4_0_DOWN_PREFETCH_NAVI22=1
GGML_VK_F16_ATTN_NAVI22_MODE=p021
GGML_VK_F16_ATTN_MMV_NAVI22_ROWS=8
GGML_VK_POST_QKV_FUSION_NAVI22=1
GGML_VK_FA_MASKED_SPLIT_NAVI22=1
```

Depth-4096 benchmark pacing uses:

```bash
LLAMA_BENCH_DEPTH_PREFILL_CHUNK=512
LLAMA_BENCH_DEPTH_PREFILL_PAUSE_MS=2000
LLAMA_BENCH_DEPTH_COOLDOWN_MS=20000
```

GPU execution must still use this repository's fail-closed thermal guard. This
source port and its compile-only validation are not a substitute for a fresh
guarded correctness or benchmark campaign on current master.

## Production/test source allowlist

Excluding the isolated pacing file, the nine production/test commits may change
only these 17 files:

```text
ggml/src/ggml-vulkan/ggml-vulkan.cpp
ggml/src/ggml-vulkan/vulkan-shaders/flash_attn.comp
ggml/src/ggml-vulkan/vulkan-shaders/flash_attn_base.glsl
ggml/src/ggml-vulkan/vulkan-shaders/flash_attn_decode_f16_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/flash_attn_split_k_reduce_q8_1_x4_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/mul_mat_vec_f16_attn_av_rows16_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/mul_mat_vec_f16_attn_av_rows32_dualwave_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/mul_mat_vec_f16_attn_av_rows8_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/mul_mat_vec_f16_attn_qk_rows16_dualwave_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/mul_mat_vec_nc.comp
ggml/src/ggml-vulkan/vulkan-shaders/mul_mat_vec_q4_0_multiproj_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/mul_mat_vecq.comp
ggml/src/ggml-vulkan/vulkan-shaders/rms_norm_mul_partials_q8_1_x4_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/rms_norm_mul_q8_1_x4_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/rope_qkv_set_rows_navi22.comp
ggml/src/ggml-vulkan/vulkan-shaders/vulkan-shaders-gen.cpp
tests/test-backend-ops.cpp
```

## Local source-port validation

- `git diff --check` passed and all three worktrees were clean.
- Release/Vulkan compile-only builds produced `llama-bench`, `llama-debug`,
  and `test-backend-ops` for both the paced control and full candidate.
- All 16 generated Navi22 SPIR-V modules passed
  `spirv-val --target-env vulkan1.2`.
- A separate `GGML_VULKAN=OFF`, `GGML_NATIVE=OFF` build passed the retained
  CPU graph suites 22/22 and 5/5, plus both exact F16 attention cases 1/1.
- No GPU-capable executable was launched while preparing this port.

All upstream llama.cpp license and copyright notices remain authoritative and
are preserved. The exact upstream MIT notice at the pinned base is included as
[`UPSTREAM_LICENSE`](UPSTREAM_LICENSE); the repository's top-level license does
not replace or relicense it.
