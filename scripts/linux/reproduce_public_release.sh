#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EVIDENCE_DIR="$ROOT_DIR/release/evidence"

usage() {
    cat >&2 <<EOF
usage:
  $0 analysis
EOF
}

mode="${1:-analysis}"
case "$mode" in
    analysis)
        (( $# <= 1 )) || { usage; exit 2; }
        (
            cd "$EVIDENCE_DIR"
            sha256sum --check SHA256SUMS
        )
        python3 -I -B "$ROOT_DIR/scripts/analyze_release_evidence.py"
        (
            cd "$EVIDENCE_DIR"
            sha256sum --check SHA256SUMS
        )
        echo "public evidence analysis passed: $EVIDENCE_DIR/regenerated/results.md"
        ;;
    -h|--help)
        usage
        ;;
    *)
        usage
        exit 2
        ;;
esac
