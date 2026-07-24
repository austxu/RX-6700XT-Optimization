# llama.cpp Navi22 patch series

This directory pins the clean production patch series used for the RX 6700 XT
results. It applies to official llama.cpp commit
`86d86ed4396b4130922f7b9af26e3d9fc11a591b`.

- Patch count: 9.
- Expected final Git tree:
  `181e8fccc75423329c07885b5b853dd92a0520b8`.
- Clean local reference branch: `navi22/public-final-86d86ed4` at
  `0482df775cc274ee06c217c023ed94ed4b00a99e`.
- Accepted benchmark/correctness tree: the same tree at
  `6b66b2e2f7b3b04ab84b2b498ab63127ced5826a`.

The clean reference omits a temporary diagnostic add/remove pair from the
experimental history. Its complete source tree is byte-identical to the
accepted production candidate. Commit hashes created by `git am` may differ,
but the application script verifies the final tree hash.

Apply the series from this repository:

```bash
scripts/apply_llamacpp_navi22_patches.sh /path/to/clean/llama.cpp
```

The target checkout must be clean and exactly at the pinned base. The script
verifies every patch before applying it. All upstream llama.cpp copyright and
license notices remain authoritative and are preserved by the patches.

The optimizations are opt-in and fail closed on unsupported hardware. The
accepted Q4_K_M configuration uses:

```bash
GGML_VK_Q4_K_MMVQ_NAVI22=1
GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22=1
GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22_MODE=direct
```

The accepted Llama 2 Q4_0 target additionally uses its Q4_0, multi-projection,
and attention-sidecar routes:

```bash
GGML_VK_Q4_0_MMVQ_NAVI22=1
GGML_VK_Q4_0_MULTIPROJ_NAVI22=1
GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22=1
GGML_VK_RMS_NORM_MUL_Q8_1_NAVI22_MODE=direct
GGML_VK_FLASH_ATTN_Q8_1_NAVI22=1
```

Do not run performance commands without the hardware-safety and comparison
contract in `docs/REPRODUCING.md`.
