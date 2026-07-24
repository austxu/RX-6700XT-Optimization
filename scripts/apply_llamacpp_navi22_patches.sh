#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PATCH_DIR="$ROOT_DIR/patches/llama.cpp-navi22-86d86ed4"
BASE_COMMIT=86d86ed4396b4130922f7b9af26e3d9fc11a591b
EXPECTED_TREE=181e8fccc75423329c07885b5b853dd92a0520b8
PATCH_COUNT=9

usage() {
    echo "usage: $0 /path/to/clean/llama.cpp" >&2
}

fail() {
    echo "apply llama.cpp Navi22 patches: $*" >&2
    exit 2
}

(( $# == 1 )) || { usage; exit 2; }
TARGET="$(realpath -e -- "$1")"

git -C "$TARGET" rev-parse --git-dir >/dev/null 2>&1 || fail "target is not a Git checkout"
[[ -z "$(git -C "$TARGET" status --porcelain)" ]] || fail "target checkout is dirty"
[[ "$(git -C "$TARGET" rev-parse HEAD)" == "$BASE_COMMIT" ]] || fail "target is not at pinned base $BASE_COMMIT"
[[ ! -d "$(git -C "$TARGET" rev-parse --git-path rebase-apply)" ]] || fail "target already has a git-am operation in progress"

(cd "$PATCH_DIR" && sha256sum --check SHA256SUMS)
shopt -s nullglob
patches=("$PATCH_DIR"/*.patch)
(( ${#patches[@]} == PATCH_COUNT )) || fail "expected $PATCH_COUNT patches, found ${#patches[@]}"

git -C "$TARGET" am --3way "${patches[@]}"
actual_tree="$(git -C "$TARGET" rev-parse HEAD^{tree})"
[[ "$actual_tree" == "$EXPECTED_TREE" ]] || fail "final tree mismatch: $actual_tree"
[[ -z "$(git -C "$TARGET" status --porcelain)" ]] || fail "target is dirty after patch application"

printf 'applied %s patches\nbase=%s\nhead=%s\ntree=%s\n' \
    "$PATCH_COUNT" "$BASE_COMMIT" "$(git -C "$TARGET" rev-parse HEAD)" "$actual_tree"
