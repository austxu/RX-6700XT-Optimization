#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH_DIR="$ROOT_DIR/patches/llama.cpp-navi22-retained-0cea36222"
BASE_COMMIT=0cea36222fe9bac5ebfc45716c9eef11f37046c4
BASE_TREE=3514d2f9359eb40f4a68890e3fa1337be1357187
PACED_TREE=2cfe7d4bb10e1fd6a8e8e932072e9c24b8d92b2e
FULL_TREE=2af9ba5958d30228c73faf8f918d4c30802a57ae
PATCH_COUNT=10
PACING_PATCH=0003-llama-bench-add-guarded-depth-prefill-pacing.patch

usage() {
    echo "usage: $0 /path/to/clean/llama.cpp [full|paced-control]" >&2
}

fail() {
    echo "apply current-master retained llama.cpp Navi22 patches: $*" >&2
    exit 2
}

(( $# >= 1 && $# <= 2 )) || { usage; exit 2; }
TARGET="$(realpath -e -- "$1")"
PROFILE="${2:-full}"

case "$PROFILE" in
    full|paced-control) ;;
    *) usage; fail "unknown profile: $PROFILE" ;;
esac

git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1 \
    || fail "target is not a Git checkout"
[[ -z "$(git -C "$TARGET" status --porcelain)" ]] \
    || fail "target checkout is dirty"
[[ "$(git -C "$TARGET" rev-parse HEAD)" == "$BASE_COMMIT" ]] \
    || fail "target is not at pinned base $BASE_COMMIT"
[[ "$(git -C "$TARGET" rev-parse HEAD^{tree})" == "$BASE_TREE" ]] \
    || fail "pinned base tree mismatch"
[[ ! -d "$(git -C "$TARGET" rev-parse --git-path rebase-apply)" ]] \
    || fail "target already has a git-am operation in progress"

(cd "$PATCH_DIR" && sha256sum --check SHA256SUMS)
shopt -s nullglob
patches=("$PATCH_DIR"/*.patch)
(( ${#patches[@]} == PATCH_COUNT )) \
    || fail "expected $PATCH_COUNT patches, found ${#patches[@]}"
[[ "$(basename "${patches[2]}")" == "$PACING_PATCH" ]] \
    || fail "patch 0003 is not the isolated pacing patch"

production_paths=(
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
)
PACING_PATH=tools/llama-bench/llama-bench.cpp

verify_paths() {
    local expected_name="$1"
    shift
    local -a expected=("$@")
    local -a actual=()
    local index

    mapfile -t actual < <(git -C "$TARGET" diff --name-only "$BASE_COMMIT"..HEAD | LC_ALL=C sort)
    (( ${#actual[@]} == ${#expected[@]} )) \
        || fail "$expected_name changed-file count mismatch"
    for index in "${!expected[@]}"; do
        [[ "${actual[$index]}" == "${expected[$index]}" ]] \
            || fail "$expected_name changed-file mismatch: expected ${expected[$index]}, got ${actual[$index]}"
    done
}

if [[ "$PROFILE" == paced-control ]]; then
    git -C "$TARGET" am --3way "$PATCH_DIR/$PACING_PATCH"
    [[ "$(git -C "$TARGET" rev-parse HEAD^{tree})" == "$PACED_TREE" ]] \
        || fail "paced-control tree mismatch"
    verify_paths paced-control "$PACING_PATH"
else
    git -C "$TARGET" am --3way "${patches[@]}"
    [[ "$(git -C "$TARGET" rev-parse HEAD^{tree})" == "$FULL_TREE" ]] \
        || fail "full candidate tree mismatch"

    mapfile -t applied_commits < <(git -C "$TARGET" rev-list --reverse "$BASE_COMMIT"..HEAD)
    (( ${#applied_commits[@]} == PATCH_COUNT )) \
        || fail "applied commit count mismatch"
    mapfile -t pacing_paths < <(
        git -C "$TARGET" diff-tree --no-commit-id --name-only -r "${applied_commits[2]}" |
            LC_ALL=C sort
    )
    (( ${#pacing_paths[@]} == 1 )) \
        || fail "patch 0003 changed-file count mismatch"
    [[ "${pacing_paths[0]}" == "$PACING_PATH" ]] \
        || fail "patch 0003 is not isolated to $PACING_PATH"

    full_paths=("${production_paths[@]}" "$PACING_PATH")
    mapfile -t full_paths < <(printf '%s\n' "${full_paths[@]}" | LC_ALL=C sort)
    verify_paths full "${full_paths[@]}"
fi

git -C "$TARGET" diff --check "$BASE_COMMIT"..HEAD
[[ -z "$(git -C "$TARGET" status --porcelain)" ]] \
    || fail "target is dirty after patch application"

printf 'profile=%s\nbase=%s\nhead=%s\ntree=%s\n' \
    "$PROFILE" "$BASE_COMMIT" "$(git -C "$TARGET" rev-parse HEAD)" \
    "$(git -C "$TARGET" rev-parse HEAD^{tree})"
