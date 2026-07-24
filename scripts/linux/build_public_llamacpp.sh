#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
APPLY_SCRIPT="$ROOT_DIR/scripts/apply_llamacpp_navi22_patches.sh"
BASE_COMMIT=86d86ed4396b4130922f7b9af26e3d9fc11a591b
EXPECTED_TREE=181e8fccc75423329c07885b5b853dd92a0520b8
DEFAULT_TARGET="$ROOT_DIR/external/llama.cpp-navi22-public"
TARGET="${1:-$DEFAULT_TARGET}"

fail() {
    echo "public llama.cpp build: $*" >&2
    exit 2
}

if (( $# > 1 )) || [[ "${1:-}" == -h || "${1:-}" == --help ]]; then
    echo "usage: $0 [llama.cpp-checkout]" >&2
    [[ "${1:-}" == -h || "${1:-}" == --help ]] && exit 0
    exit 2
fi

for command in git cmake sha256sum spirv-val; do
    command -v "$command" >/dev/null || fail "required command not found: $command"
done
[[ -x "$APPLY_SCRIPT" ]] || fail "patch application script is missing or not executable"

if [[ ! -e "$TARGET" ]]; then
    mkdir -p "$(dirname "$TARGET")"
    git clone --no-checkout https://github.com/ggml-org/llama.cpp.git "$TARGET"
    git -C "$TARGET" checkout --detach "$BASE_COMMIT"
    git -C "$TARGET" switch -c navi22/public-final-86d86ed4
fi
TARGET="$(realpath -e -- "$TARGET")"
git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1 || fail "target is not a Git checkout: $TARGET"
[[ -z "$(git -C "$TARGET" status --porcelain)" ]] || fail "target checkout is dirty"

current_tree="$(git -C "$TARGET" rev-parse HEAD^{tree})"
if [[ "$(git -C "$TARGET" rev-parse HEAD)" == "$BASE_COMMIT" ]]; then
    if [[ -z "$(git -C "$TARGET" branch --show-current)" ]]; then
        git -C "$TARGET" switch -c navi22/public-final-86d86ed4
    fi
    "$APPLY_SCRIPT" "$TARGET"
elif [[ "$current_tree" != "$EXPECTED_TREE" ]]; then
    fail "target is neither the pinned base nor the expected final tree (found $current_tree)"
fi

git -C "$TARGET" diff --check "$BASE_COMMIT"..HEAD
[[ "$(git -C "$TARGET" rev-parse HEAD^{tree})" == "$EXPECTED_TREE" ]] \
    || fail "patched source tree does not match $EXPECTED_TREE"

release_generator=()
cpu_generator=()
if [[ ! -f "$TARGET/build-release/CMakeCache.txt" ]]; then
    command -v ninja >/dev/null || fail "required command not found for a fresh build: ninja"
    release_generator=(-GNinja)
fi
if [[ ! -f "$TARGET/build-cpu-correctness/CMakeCache.txt" ]]; then
    command -v ninja >/dev/null || fail "required command not found for a fresh build: ninja"
    cpu_generator=(-GNinja)
fi

cmake -S "$TARGET" -B "$TARGET/build-release" "${release_generator[@]}" \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_VULKAN=ON \
    -DLLAMA_BUILD_TESTS=ON \
    -DLLAMA_CURL=OFF
cmake --build "$TARGET/build-release" --target llama-bench llama-debug test-backend-ops

cmake -S "$TARGET" -B "$TARGET/build-cpu-correctness" "${cpu_generator[@]}" \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_VULKAN=OFF \
    -DLLAMA_BUILD_TESTS=ON \
    -DLLAMA_CURL=OFF
cmake --build "$TARGET/build-cpu-correctness" --target test-backend-ops

for module in \
    rms_norm_mul_partials_q8_1_x4_navi22.spv \
    rms_norm_mul_q8_1_x4_navi22.spv \
    mul_mat_vec_q4_0_q8_1_f32_multiproj_navi22.spv \
    fa_split_k_reduce_q8_1_x4_navi22.spv; do
    spirv-val --target-env vulkan1.2 \
        "$TARGET/build-release/ggml/src/ggml-vulkan/vulkan-shaders.spv/$module"
done

printf 'public llama.cpp build passed\ncheckout=%s\nhead=%s\ntree=%s\n' \
    "$TARGET" "$(git -C "$TARGET" rev-parse HEAD)" \
    "$(git -C "$TARGET" rev-parse HEAD^{tree})"
