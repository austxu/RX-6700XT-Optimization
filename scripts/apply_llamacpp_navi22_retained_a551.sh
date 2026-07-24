#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_APPLY="$ROOT_DIR/scripts/apply_llamacpp_navi22_patches.sh"
PATCH_DIR="$ROOT_DIR/patches/llama.cpp-navi22-retained-a551-86d86ed4"
BASE_COMMIT=86d86ed4396b4130922f7b9af26e3d9fc11a591b
PREREQUISITE_TREE=181e8fccc75423329c07885b5b853dd92a0520b8
EXPECTED_TREE=2d3add3e01638795ff1cdc45273375ff4f455b52
PATCH_COUNT=1

usage() {
    echo "usage: $0 /path/to/clean/llama.cpp" >&2
}

fail() {
    echo "apply retained llama.cpp Navi22 supplement: $*" >&2
    exit 2
}

(( $# == 1 )) || { usage; exit 2; }
TARGET="$(realpath -e -- "$1")"

git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1 || fail "target is not a Git checkout"
[[ -z "$(git -C "$TARGET" status --porcelain)" ]] || fail "target checkout is dirty"
[[ "$(git -C "$TARGET" rev-parse HEAD)" == "$BASE_COMMIT" ]] || fail "target is not at pinned base $BASE_COMMIT"

"$BASE_APPLY" "$TARGET"
actual_tree="$(git -C "$TARGET" rev-parse HEAD^{tree})"
[[ "$actual_tree" == "$PREREQUISITE_TREE" ]] || fail "prerequisite tree mismatch: $actual_tree"

(cd "$PATCH_DIR" && sha256sum --check SHA256SUMS)
shopt -s nullglob
patches=("$PATCH_DIR"/*.patch)
(( ${#patches[@]} == PATCH_COUNT )) || fail "expected $PATCH_COUNT supplement, found ${#patches[@]}"

git -C "$TARGET" am --3way "${patches[@]}"
actual_tree="$(git -C "$TARGET" rev-parse HEAD^{tree})"
[[ "$actual_tree" == "$EXPECTED_TREE" ]] || fail "final tree mismatch: $actual_tree"
[[ -z "$(git -C "$TARGET" status --porcelain)" ]] || fail "target is dirty after patch application"

printf 'applied 9 prerequisite patches and %s supplement\nbase=%s\nhead=%s\ntree=%s\n' \
    "$PATCH_COUNT" "$BASE_COMMIT" "$(git -C "$TARGET" rev-parse HEAD)" "$actual_tree"
