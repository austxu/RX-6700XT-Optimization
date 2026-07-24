#!/usr/bin/env python3
"""Regenerate public result rows and confidence intervals from exported samples."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import statistics
import sys
from pathlib import Path
from typing import Any

# Isolated mode omits the script directory. Add only this resolved,
# repository-owned sibling path before importing the public statistics helper.
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import release_statistics as common


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "release/evidence"
SLOTS = ("A1", "B1", "B2", "A2")
REPLICATES = 100_000
CAMPAIGN_SLUGS = ("llama2-attention", "llama2-retained-a551")
CAMPAIGN_FILES = (
    "analysis.json",
    "campaign.txt",
    "raw-results.jsonl",
    "raw-samples.csv",
    "source-files.sha256",
)
METRIC_SPECS = {
    "fa0_pp512": ("0", "pp512", 512),
    "fa0_tg128": ("0", "tg128", 128),
    "fa1_pp512": ("1", "pp512", 512),
    "fa1_tg128": ("1", "tg128", 128),
}
RAW_SAMPLE_FIELDS = (
    "metric",
    "flash_attn",
    "workload",
    "cycle",
    "slot",
    "role",
    "repetition",
    "sample_ns",
    "tps",
)
HEX64 = re.compile(r"[0-9a-f]{64}")
INDEX_SCHEMA = "amd-inference-public-evidence-v2"
RESULTS_SCHEMA = "amd-inference-regenerated-results-v1"
CORRECTNESS_SCHEMA = "current-master-correctness-v1"
CORRECTNESS_SUMMARY_FIELDS = {
    "schema",
    "profile",
    "decision",
    "failures",
    "pins_sha256",
    "campaign_manifest",
    "artifact_sha256",
    "focused_graph_sha256",
    "comparisons",
    "gates",
}
CORRECTNESS_GATE_FIELDS = {
    "control_candidate_default",
    "candidate_default_enabled_tokens",
    "llama2_enabled_logits",
    "q4k_nmse_limit",
    "q4k_max_absolute_error_limit",
    "q4k_argmax",
    "q4k_top10",
    "cpu_reference_tokens",
    "cpu_reference_nmse_limit",
    "cpu_reference_max_absolute_error_limit",
    "cpu_reference_argmax",
    "cpu_reference_top10",
}
EXPECTED_CORRECTNESS = {
    "llama2": {
        "artifact_root": (
            "artifacts/public-release/current-master/correctness/"
            "llama2-20260724T065633Z"
        ),
        "profile": "llama2",
        "failure_class": "numerical-correctness",
        "failure_count": 12,
        "source_root_manifest_sha256": (
            "78dac576e71305ee1810772cd0e9c499769a24178d23df545121d055157d24c2"
        ),
        "source_summary_sha256": (
            "13543e2e55c4bf4fb53f82b71ba524814c98cc7eb0939578e56e38ca6e723a9f"
        ),
        "source_campaign_sha256": (
            "6ed62c68c46b090d7fda5e29919c3e157dc7ef2e52270a623e576ef8f3b73ff9"
        ),
        "exported_summary_sha256": (
            "164b6d674c94bc2b244c988889f68fbe14115e7827d775d389d29b882d5b0258"
        ),
        "exported_campaign_sha256": (
            "88d67fedfbc11335501d7cfbb692e8d4366e78ff9297b194bdb4cfe00e2ae09b"
        ),
    },
}
EXPECTED_CAMPAIGNS = {
    "llama2-attention": {
        "metadata": {
            "analyzer": "scripts/analyze_public_release_llama2.py",
            "artifact_root": (
                "artifacts/public-release/phase5/"
                "llama2-attention-abba-20260717T224044Z"
            ),
            "claim_scope": "author-operated matched local benchmark",
            "exported_files": list(CAMPAIGN_FILES),
            "raw_sample_count": 336,
            "result_json_count": 12,
            "result_row_count": 4,
            "root_manifest_sha256": (
                "645ce196c11efe0d730f2d19490e23cca674f93cd84311de3aa94462ac29e495"
            ),
            "source_root_sealed": True,
        },
        "exported_sha256": {
            "analysis.json": (
                "dd3315a3356b6d828e78e4ce6182146b2e77b9b2ffa49e3ed8e11a20b802f80d"
            ),
            "campaign.txt": (
                "0c16815f162e4f528a7417c7d81da6ebb8f706ababf3311de138db9880eaabff"
            ),
            "raw-results.jsonl": (
                "7e8b8b9b7641203f56c5b8fb534b028d5be1a00be72e9c675444d8831b8bc142"
            ),
            "raw-samples.csv": (
                "7bdddb5e80ef2dd011dac81eb8d667792221c0d281dab65b2102a911db6e2c5b"
            ),
            "source-files.sha256": (
                "645ce196c11efe0d730f2d19490e23cca674f93cd84311de3aa94462ac29e495"
            ),
        },
    },
    "llama2-retained-a551": {
        "metadata": {
            "analyzer": "scripts/analyze_public_release_llama2.py",
            "artifact_root": (
                "artifacts/public-release/phase6/"
                "llama2-retained-a551-abba-20260721T025858Z"
            ),
            "claim_scope": "author-operated matched local benchmark",
            "exported_files": list(CAMPAIGN_FILES),
            "raw_sample_count": 336,
            "result_json_count": 12,
            "result_row_count": 4,
            "root_manifest_sha256": (
                "ba78604dd1d73a44f4f9bbb7afe14e91b23f0e5740d2f15f4ad0d1269427633d"
            ),
            "scoreboard_eligibility_note": (
                "The measured candidate is a custom retained-a551 fork. The "
                "discussion's main post does not explicitly require master, "
                "but llama.cpp collaborator 0cc4m later said the thread is for "
                "master-branch performance. The result is outside that stated "
                "scope unless a curator explicitly grants an exception."
            ),
            "scoreboard_submission_eligible": False,
            "source_root_sealed": True,
        },
        "exported_sha256": {
            "analysis.json": (
                "7df60f78e5946cdb6aac1f10f10b90b7774f4ee5752cbf477af9028b632c86df"
            ),
            "campaign.txt": (
                "e05089aa51c8f34c1207646f3d1b838039bdb36f6662c644d11b4d24cc17a99e"
            ),
            "raw-results.jsonl": (
                "12d9e86e99b691c592165321872363c3c2d43f23cb6d76eea75235907107337b"
            ),
            "raw-samples.csv": (
                "dbd1a22b14ec6c759a9b590c8ab64a0eee0512f49533abaf5d512d8b9708b275"
            ),
            "source-files.sha256": (
                "ba78604dd1d73a44f4f9bbb7afe14e91b23f0e5740d2f15f4ad0d1269427633d"
            ),
        },
    },
}
EXPECTED_SUPPORTING = {
    "final-correctness": {
        "metadata": {
            "artifact_root": (
                "artifacts/public-release/release/"
                "final-correctness-20260718T004000Z"
            ),
            "exported_source_seal": (
                "supporting/final-correctness-source-files.sha256"
            ),
            "root_manifest_sha256": (
                "c3e4e52c67c8524b6af9db02cf2375e775424d7a519867f79f086fe7527e41a9"
            ),
            "source_root_sealed": True,
        },
        "summary_export": "correctness/final-summary.txt",
        "summary_source": "summary.txt",
        "summary_sha256": (
            "7bdec9c5ea4786be40f49e72640b8a10ca4a8f4216c4936a8f38ef802492bf02"
        ),
    },
    "retained-a551-correctness": {
        "metadata": {
            "artifact_root": (
                "artifacts/public-release/phase6/"
                "q4-down-prefetch-correctness-20260720T062412Z"
            ),
            "exported_source_seal": (
                "supporting/retained-a551-correctness-source-files.sha256"
            ),
            "root_manifest_sha256": (
                "ad8779feea6ac21c9fc63343b6133d75d3bc8accee76e9db0577ad318825eac6"
            ),
            "source_root_sealed": True,
        },
        "summary_export": "correctness/retained-a551-summary.txt",
        "summary_source": "summary.txt",
        "summary_sha256": (
            "789887004308f6d0b54ae475500efea72aedf46f505d673f763ecdae899c8160"
        ),
    },
    "retained-a551-preflight": {
        "metadata": {
            "artifact_root": (
                "artifacts/public-release/phase6/"
                "llama2-retained-a551-abba-preflight-20260721T025813Z"
            ),
            "exported_source_seal": (
                "supporting/retained-a551-preflight-source-files.sha256"
            ),
            "root_manifest_sha256": (
                "fb13f54aa10bbe2be18152703f681db1c0c95169038af5d6001a0819549dc0c5"
            ),
            "source_root_sealed": True,
        },
    },
    "hardware": {
        "metadata": {
            "artifact_source": (
                "artifacts/public-release/phase1/"
                "historical-evidence-20260716T202738Z/"
                "hardware-supplement-20260716T2029Z.txt"
            ),
            "source_sha256": (
                "08a8aa8dca574fb75ee1be15e686953100fcfeb100e897e83cb06ae76f7b7e44"
            ),
        },
        "export": "hardware/hardware-manifest.txt",
        "exported_sha256": (
            "124af01dd3413f37becbf91b581dddf77a232514a32e4e739d52310a8f5117b6"
        ),
    },
}
EXPECTED_COUNTS = {
    "campaigns": 2,
    "correctness_outcomes": 1,
    "raw_samples": 672,
    "result_json": 24,
    "result_rows": 8,
    "sealed_correctness_failures": 1,
    "unsealed_route_failures": 0,
}


def expected_evidence_files() -> set[Path]:
    paths = {
        Path("index.json"),
        Path("regenerated/results.json"),
        Path("regenerated/results.md"),
        Path("negative-results/current-master/outcomes.json"),
        Path("negative-results/current-master/llama2/campaign.txt"),
        Path("negative-results/current-master/llama2/source-files.sha256"),
        Path("negative-results/current-master/llama2/summary.json"),
        Path("correctness/final-summary.txt"),
        Path("correctness/retained-a551-summary.txt"),
        Path("hardware/hardware-manifest.txt"),
    }
    for slug in CAMPAIGN_SLUGS:
        paths.update(Path("campaigns") / slug / name for name in CAMPAIGN_FILES)
    for slug in (
        "final-correctness",
        "retained-a551-correctness",
        "retained-a551-preflight",
    ):
        paths.add(
            Path(EXPECTED_SUPPORTING[slug]["metadata"]["exported_source_seal"])
        )
    return paths


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def strict_json_loads(text: str | bytes, context: str) -> Any:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        value: dict[str, Any] = {}
        for key, item in pairs:
            if key in value:
                raise ValueError(f"{context}: duplicate JSON key: {key!r}")
            value[key] = item
        return value

    def reject_constant(value: str) -> Any:
        raise ValueError(f"{context}: non-finite JSON number: {value}")

    def finite_float(value: str) -> float:
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError(f"{context}: non-finite JSON number: {value}")
        return parsed

    try:
        return json.loads(
            text,
            object_pairs_hook=unique_object,
            parse_constant=reject_constant,
            parse_float=finite_float,
        )
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{context}: invalid JSON: {exc}") from exc


def strict_json_file(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"could not read JSON file {path}: {exc}") from exc
    return strict_json_loads(text, str(path))


def regular_files(root: Path) -> list[Path]:
    absolute = root.absolute()
    require(
        absolute.is_dir()
        and not absolute.is_symlink()
        and absolute.resolve(strict=True) == absolute,
        f"evidence root or ancestor is not a canonical directory: {root}",
    )
    result: list[Path] = []
    for directory, directories, files in os.walk(absolute, followlinks=False):
        directory_path = Path(directory)
        directories.sort()
        files.sort()
        for name in directories:
            child = directory_path / name
            require(
                child.is_dir() and not child.is_symlink(),
                f"symlink or non-directory is forbidden: {child}",
            )
        for name in files:
            child = directory_path / name
            require(
                child.is_file() and not child.is_symlink(),
                f"symlink or non-regular file is forbidden: {child}",
            )
            result.append(child)
    return result


def safe_relative(raw: str, context: str) -> Path:
    relative = Path(raw)
    require(
        bool(raw)
        and "\\" not in raw
        and not relative.is_absolute()
        and relative.as_posix() == raw
        and "." not in relative.parts
        and ".." not in relative.parts,
        f"{context}: unsafe or non-canonical relative path: {raw!r}",
    )
    return relative


def parse_checksum_manifest(path: Path) -> dict[Path, str]:
    require(path.is_file() and not path.is_symlink(), f"missing checksum manifest: {path}")
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"could not read checksum manifest {path}: {exc}") from exc
    require(bool(lines), f"empty checksum manifest: {path}")
    entries: dict[Path, str] = {}
    previous = ""
    for number, line in enumerate(lines, 1):
        digest, separator, raw_name = line.partition("  ")
        require(
            bool(separator)
            and HEX64.fullmatch(digest) is not None
            and raw_name
            and not raw_name.startswith("./"),
            f"{path}:{number}: malformed checksum entry",
        )
        relative = safe_relative(raw_name, f"{path}:{number}")
        require(relative not in entries, f"{path}:{number}: duplicate checksum path")
        require(raw_name > previous, f"{path}:{number}: checksum paths are not sorted")
        previous = raw_name
        entries[relative] = digest
    return entries


def verify_evidence_checksums(evidence: Path) -> dict[Path, str]:
    files = regular_files(evidence)
    manifest = evidence / "SHA256SUMS"
    entries = parse_checksum_manifest(manifest)
    actual = {path.relative_to(evidence) for path in files if path != manifest}
    require(
        set(entries) == actual == expected_evidence_files(),
        "SHA256SUMS does not exactly cover the evidence tree: "
        f"manifest_missing={sorted(str(item) for item in actual - set(entries))}, "
        f"manifest_extra={sorted(str(item) for item in set(entries) - actual)}, "
        f"inventory_missing={sorted(str(item) for item in expected_evidence_files() - actual)}, "
        f"inventory_extra={sorted(str(item) for item in actual - expected_evidence_files())}",
    )
    for relative, expected in entries.items():
        actual_digest = sha256_bytes((evidence / relative).read_bytes())
        require(
            actual_digest == expected,
            f"checksum mismatch for {relative}: {actual_digest} != {expected}",
        )
    return entries


def parse_source_seal(path: Path) -> dict[Path, str]:
    require(path.is_file() and not path.is_symlink(), f"missing source seal: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    require(bool(lines), f"empty source seal: {path}")
    entries: dict[Path, str] = {}
    previous = ""
    for number, line in enumerate(lines, 1):
        digest, separator, raw_name = line.partition("  ")
        require(
            bool(separator)
            and HEX64.fullmatch(digest) is not None
            and raw_name.startswith("./"),
            f"{path}:{number}: malformed source-seal entry",
        )
        relative = safe_relative(raw_name[2:], f"{path}:{number}")
        require(relative not in entries, f"{path}:{number}: duplicate source-seal path")
        require(raw_name > previous, f"{path}:{number}: source-seal paths are not sorted")
        previous = raw_name
        entries[relative] = digest
    return entries


def parse_campaign(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        key, separator, value = line.partition("=")
        require(bool(separator) and key and key not in values, f"{path}:{number}: malformed campaign row")
        values[key] = value
    require(bool(values), f"empty campaign manifest: {path}")
    return values


def validate_failed_summary(summary: Any, profile: str, failure_count: int) -> None:
    require(
        isinstance(summary, dict) and set(summary) == CORRECTNESS_SUMMARY_FIELDS,
        f"{profile}: correctness summary fields mismatch",
    )
    require(summary["schema"] == CORRECTNESS_SCHEMA, f"{profile}: summary schema mismatch")
    require(summary["profile"] == profile, f"{profile}: summary profile mismatch")
    require(summary["decision"] == "fail", f"{profile}: summary must remain a failure")
    failures = summary["failures"]
    require(
        isinstance(failures, list)
        and len(failures) == failure_count
        and len(set(failures)) == len(failures)
        and all(isinstance(item, str) and item for item in failures),
        f"{profile}: failure list mismatch",
    )
    require(
        isinstance(summary["pins_sha256"], str)
        and HEX64.fullmatch(summary["pins_sha256"]) is not None,
        f"{profile}: pins digest is invalid",
    )
    require(
        isinstance(summary["campaign_manifest"], dict)
        and bool(summary["campaign_manifest"]),
        f"{profile}: campaign manifest is missing",
    )
    for name in ("artifact_sha256", "focused_graph_sha256"):
        values = summary[name]
        require(isinstance(values, dict), f"{profile}: {name} is not an object")
        if name == "artifact_sha256":
            require(bool(values), f"{profile}: artifact hashes are empty")
        for raw_path, digest in values.items():
            safe_relative(raw_path, f"{profile}/{name}")
            require(
                isinstance(digest, str) and HEX64.fullmatch(digest) is not None,
                f"{profile}: invalid digest in {name}",
            )
    require(
        isinstance(summary["comparisons"], dict) and bool(summary["comparisons"]),
        f"{profile}: comparisons are missing",
    )
    require(
        isinstance(summary["gates"], dict)
        and set(summary["gates"]) == CORRECTNESS_GATE_FIELDS,
        f"{profile}: correctness gates mismatch",
    )


def validate_correctness_outcomes(
    evidence: Path, index: dict[str, Any]
) -> dict[str, Any]:
    metadata_root = index.get("correctness_outcomes")
    require(
        isinstance(metadata_root, dict)
        and set(metadata_root) == set(EXPECTED_CORRECTNESS),
        "correctness outcome index mismatch",
    )
    outcomes_path = evidence / "negative-results/current-master/outcomes.json"
    outcomes_payload = strict_json_file(outcomes_path)
    require(
        isinstance(outcomes_payload, dict)
        and set(outcomes_payload) == {"schema", "outcomes"}
        and outcomes_payload["schema"] == "current-master-correctness-outcomes-v1"
        and isinstance(outcomes_payload["outcomes"], dict)
        and set(outcomes_payload["outcomes"]) == set(EXPECTED_CORRECTNESS),
        "current-master outcome summary schema mismatch",
    )

    for slug in ("llama2",):
        expected = EXPECTED_CORRECTNESS[slug]
        metadata = metadata_root[slug]
        expected_keys = {
            "artifact_root",
            "profile",
            "decision",
            "failure_class",
            "failure_count",
            "evidence_status",
            "source_root_sealed",
            "source_root_manifest_sha256",
            "source_summary_sha256",
            "source_campaign_sha256",
            "exported_summary_sha256",
            "exported_campaign_sha256",
            "exported_files",
            "performance_timing_authorized",
        }
        require(
            isinstance(metadata, dict) and set(metadata) == expected_keys,
            f"{slug}: indexed correctness metadata fields mismatch",
        )
        for name in (
            "artifact_root",
            "profile",
            "failure_class",
            "failure_count",
            "source_root_manifest_sha256",
            "source_summary_sha256",
        ):
            require(metadata[name] == expected[name], f"{slug}: indexed {name} mismatch")
        require(
            metadata["decision"] == "fail"
            and metadata["evidence_status"] == "sealed"
            and metadata["source_root_sealed"] is True
            and metadata["performance_timing_authorized"] is False,
            f"{slug}: sealed negative-result status mismatch",
        )
        exported_files = ["campaign.txt", "source-files.sha256", "summary.json"]
        require(metadata["exported_files"] == exported_files, f"{slug}: exported file list mismatch")
        directory = evidence / f"negative-results/current-master/{slug}"
        actual_files = sorted(path.name for path in regular_files(directory))
        require(actual_files == exported_files, f"{slug}: compact directory contents mismatch")

        summary_path = directory / "summary.json"
        campaign_path = directory / "campaign.txt"
        seal_path = directory / "source-files.sha256"
        require(
            sha256_bytes(summary_path.read_bytes()) == metadata["exported_summary_sha256"],
            f"{slug}: exported summary digest mismatch",
        )
        require(
            sha256_bytes(campaign_path.read_bytes()) == metadata["exported_campaign_sha256"],
            f"{slug}: exported campaign digest mismatch",
        )
        require(
            sha256_bytes(seal_path.read_bytes()) == expected["source_root_manifest_sha256"],
            f"{slug}: exported source seal digest mismatch",
        )
        source_entries = parse_source_seal(seal_path)
        require(
            source_entries.get(Path("summary.json")) == expected["source_summary_sha256"]
            and Path("COMPLETE") in source_entries,
            f"{slug}: source seal does not bind the failed summary and COMPLETE marker",
        )
        summary = strict_json_file(summary_path)
        validate_failed_summary(summary, expected["profile"], expected["failure_count"])
        campaign = parse_campaign(campaign_path)
        require(
            campaign == summary["campaign_manifest"],
            f"{slug}: compact campaign does not match the failed summary",
        )
        require(
            source_entries.get(Path("manifest/campaign.txt"))
            == expected["source_campaign_sha256"]
            and source_entries.get(Path("manifest/pins.json"))
            == summary["pins_sha256"],
            f"{slug}: source seal does not bind campaign.txt and pins.json",
        )
        for collection_name in ("artifact_sha256", "focused_graph_sha256"):
            for raw_path, digest in summary[collection_name].items():
                require(
                    source_entries.get(Path(raw_path)) == digest,
                    f"{slug}: source seal does not bind "
                    f"{collection_name} entry {raw_path}",
                )
        for name in (
            "source_campaign_sha256",
            "exported_campaign_sha256",
            "exported_summary_sha256",
        ):
            require(metadata[name] == expected[name], f"{slug}: indexed {name} mismatch")
        outcome = outcomes_payload["outcomes"][slug]
        require(
            outcome
            == {
                "artifact_root": expected["artifact_root"],
                "decision": "fail",
                "evidence_status": "sealed",
                "failure_class": expected["failure_class"],
                "failure_count": expected["failure_count"],
                "performance_timing_authorized": False,
                "profile": expected["profile"],
                "source_root_manifest_sha256": expected[
                    "source_root_manifest_sha256"
                ],
                "source_root_sealed": True,
                "source_summary_sha256": expected["source_summary_sha256"],
            },
            f"{slug}: public outcome row mismatch",
        )

    return outcomes_payload


def load_campaign_raw_records(
    directory: Path, artifact_root: str, source_entries: dict[Path, str]
) -> tuple[list[dict[str, Any]], dict[str, str]]:
    path = directory / "raw-results.jsonl"
    lines = path.read_text(encoding="utf-8").splitlines()
    require(len(lines) == 12, f"{directory.name}: expected exactly 12 raw result records")
    records: list[dict[str, Any]] = []
    input_hashes: dict[str, str] = {}
    source_paths: list[str] = []
    prefix = artifact_root + "/"
    for number, line in enumerate(lines, 1):
        record = strict_json_loads(line, f"{path}:{number}")
        require(
            isinstance(record, dict)
            and set(record) == {"result", "source_path", "source_sha256"},
            f"{path}:{number}: raw result record fields mismatch",
        )
        source_path = record["source_path"]
        digest = record["source_sha256"]
        require(
            isinstance(source_path, str)
            and source_path.startswith(prefix)
            and isinstance(digest, str)
            and HEX64.fullmatch(digest) is not None,
            f"{path}:{number}: raw result provenance is invalid",
        )
        safe_relative(source_path, f"{path}:{number}")
        source_relative = safe_relative(
            source_path[len(prefix) :], f"{path}:{number}"
        )
        require(
            re.fullmatch(
                r"invocations/cycle-(?:01|02|03)/"
                r"(?:A1-control|B1-candidate|B2-candidate|A2-control)/"
                r"result\.json",
                source_relative.as_posix(),
            )
            is not None,
            f"{path}:{number}: raw result path is outside the fixed ABBA inventory",
        )
        require(
            source_entries.get(source_relative) == digest,
            f"{path}:{number}: raw result is not bound by the pinned source seal",
        )
        require(
            source_relative.as_posix() not in input_hashes,
            f"{path}:{number}: duplicate raw result path",
        )
        require(
            isinstance(record["result"], list) and len(record["result"]) == 4,
            f"{path}:{number}: raw result payload must contain four cells",
        )
        source_paths.append(source_path)
        input_hashes[source_relative.as_posix()] = digest
        records.append(record)
    require(
        source_paths == sorted(source_paths),
        f"{directory.name}: raw result records are not sorted",
    )
    return records, input_hashes


def validate_campaign_evidence(
    evidence: Path, slug: str, metadata: Any
) -> list[dict[str, Any]]:
    expected = EXPECTED_CAMPAIGNS[slug]
    require(
        isinstance(metadata, dict) and metadata == expected["metadata"],
        f"{slug}: campaign metadata differs from the frozen publication inventory",
    )
    directory = evidence / f"campaigns/{slug}"
    actual_files = sorted(path.name for path in regular_files(directory))
    require(
        actual_files == list(CAMPAIGN_FILES),
        f"{slug}: compact campaign file set mismatch",
    )
    for name, digest in expected["exported_sha256"].items():
        require(
            sha256_bytes((directory / name).read_bytes()) == digest,
            f"{slug}: frozen compact file digest changed: {name}",
        )

    seal_path = directory / "source-files.sha256"
    require(
        sha256_bytes(seal_path.read_bytes())
        == expected["metadata"]["root_manifest_sha256"],
        f"{slug}: source-root seal digest mismatch",
    )
    source_entries = parse_source_seal(seal_path)
    require(
        source_entries.get(Path("analysis/raw-samples.csv"))
        == expected["exported_sha256"]["raw-samples.csv"]
        and Path("analysis/analysis.json") in source_entries
        and Path("manifest/campaign.txt") in source_entries,
        f"{slug}: source seal does not bind the exported analysis inputs",
    )

    analysis = strict_json_file(directory / "analysis.json")
    campaign = parse_campaign(directory / "campaign.txt")
    require(
        isinstance(analysis, dict)
        and analysis.get("campaign_manifest") == campaign,
        f"{slug}: campaign manifest and accepted analysis disagree",
    )
    metrics = analysis.get("metrics")
    require(
        isinstance(metrics, dict) and set(metrics) == set(METRIC_SPECS),
        f"{slug}: expected exactly the four Llama 2 result cells",
    )
    records, input_hashes = load_campaign_raw_records(
        directory, expected["metadata"]["artifact_root"], source_entries
    )
    require(
        analysis.get("input_result_sha256") == input_hashes,
        f"{slug}: accepted analysis inputs do not match the sealed raw results",
    )
    return records


def validate_supporting_evidence(evidence: Path, index: dict[str, Any]) -> None:
    metadata = index.get("supporting_evidence")
    require(
        isinstance(metadata, dict) and set(metadata) == set(EXPECTED_SUPPORTING),
        "supporting evidence inventory mismatch",
    )
    for slug in (
        "final-correctness",
        "retained-a551-correctness",
        "retained-a551-preflight",
    ):
        expected = EXPECTED_SUPPORTING[slug]
        require(
            metadata[slug] == expected["metadata"],
            f"{slug}: supporting source metadata mismatch",
        )
        seal_path = evidence / expected["metadata"]["exported_source_seal"]
        require(
            sha256_bytes(seal_path.read_bytes())
            == expected["metadata"]["root_manifest_sha256"],
            f"{slug}: supporting source-seal digest mismatch",
        )
        source_entries = parse_source_seal(seal_path)
        if "summary_export" in expected:
            summary_path = evidence / expected["summary_export"]
            require(
                sha256_bytes(summary_path.read_bytes())
                == expected["summary_sha256"]
                == source_entries.get(Path(expected["summary_source"])),
                f"{slug}: supporting summary is not bound by the source seal",
            )

    hardware = EXPECTED_SUPPORTING["hardware"]
    require(
        metadata["hardware"] == hardware["metadata"],
        "hardware source metadata mismatch",
    )
    require(
        sha256_bytes((evidence / hardware["export"]).read_bytes())
        == hardware["exported_sha256"],
        "hardware compact export digest mismatch",
    )


def validate_evidence_index(evidence: Path) -> dict[str, Any]:
    index_path = evidence / "index.json"
    index = strict_json_file(index_path)
    require(
        isinstance(index, dict)
        and set(index)
        == {
            "schema",
            "snapshot_utc",
            "path_normalization",
            "claim_policy",
            "campaigns",
            "correctness_outcomes",
            "supporting_evidence",
            "counts",
        }
        and index["schema"] == INDEX_SCHEMA,
        "evidence index schema or fields mismatch",
    )
    campaigns = index["campaigns"]
    require(
        isinstance(campaigns, dict) and set(campaigns) == set(CAMPAIGN_SLUGS),
        "campaign index mismatch",
    )
    for slug in CAMPAIGN_SLUGS:
        validate_campaign_evidence(evidence, slug, campaigns[slug])
    counts = index["counts"]
    require(
        counts == EXPECTED_COUNTS,
        "evidence index counts differ from the fixed 24/672/8 inventory",
    )
    validate_supporting_evidence(evidence, index)
    validate_correctness_outcomes(evidence, index)
    return index


def close(actual: float, expected: float, label: str) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError(f"{label} mismatch: {actual} != {expected}")


def raw_result_sample_ns(
    records: list[dict[str, Any]], artifact_root: str
) -> dict[tuple[str, int, str, int], int]:
    expected: dict[tuple[str, int, str, int], int] = {}
    prefix = artifact_root + "/"
    path_pattern = re.compile(
        r"invocations/cycle-(01|02|03)/"
        r"(A1|B1|B2|A2)-(control|candidate)/result\.json"
    )
    for record in records:
        source_relative = record["source_path"][len(prefix) :]
        match = path_pattern.fullmatch(source_relative)
        require(match is not None, f"unexpected raw result path: {source_relative}")
        cycle = int(match.group(1))
        slot = match.group(2)
        role = match.group(3)
        require(
            role == ("control" if slot.startswith("A") else "candidate"),
            f"{source_relative}: slot/role mismatch",
        )
        seen_metrics: set[str] = set()
        for row in record["result"]:
            require(isinstance(row, dict), f"{source_relative}: result row is not an object")
            flash = row.get("flash_attn")
            n_prompt = row.get("n_prompt")
            n_gen = row.get("n_gen")
            require(
                isinstance(flash, int)
                and not isinstance(flash, bool)
                and flash in (0, 1),
                f"{source_relative}: invalid flash-attention value",
            )
            if n_prompt == 512 and n_gen == 0:
                workload = "pp512"
            elif n_prompt == 0 and n_gen == 128:
                workload = "tg128"
            else:
                raise ValueError(f"{source_relative}: unexpected benchmark cell")
            metric = f"fa{flash}_{workload}"
            require(
                metric in METRIC_SPECS and metric not in seen_metrics,
                f"{source_relative}: duplicate or unknown benchmark cell",
            )
            seen_metrics.add(metric)
            samples = row.get("samples_ns")
            require(
                isinstance(samples, list)
                and len(samples) == 7
                and all(
                    isinstance(value, int)
                    and not isinstance(value, bool)
                    and value > 0
                    for value in samples
                ),
                f"{source_relative}/{metric}: expected seven positive integer samples",
            )
            for repetition, sample_ns in enumerate(samples, 1):
                key = (metric, cycle, slot, repetition)
                require(key not in expected, f"duplicate raw sample identity: {key}")
                expected[key] = sample_ns
        require(
            seen_metrics == set(METRIC_SPECS),
            f"{source_relative}: expected all four Llama 2 cells",
        )
    require(len(expected) == 336, "raw result records do not contain exactly 336 samples")
    return expected


def load_groups(
    path: Path, expected_sample_ns: dict[tuple[str, int, str, int], int]
) -> dict[str, dict[int, dict[str, list[float]]]]:
    groups: dict[str, dict[int, dict[str, list[float]]]] = {}
    observed: set[tuple[str, int, str, int]] = set()
    with path.open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        require(
            tuple(reader.fieldnames or ()) == RAW_SAMPLE_FIELDS,
            f"{path}: raw-sample CSV header mismatch",
        )
        for number, row in enumerate(reader, 2):
            require(
                None not in row
                and set(row) == set(RAW_SAMPLE_FIELDS)
                and all(value is not None for value in row.values()),
                f"{path}:{number}: malformed CSV row",
            )
            metric = row["metric"]
            require(metric in METRIC_SPECS, f"{path}:{number}: unknown metric")
            flash, workload, tokens = METRIC_SPECS[metric]
            require(
                row["flash_attn"] == flash and row["workload"] == workload,
                f"{path}:{number}: metric fields disagree",
            )
            require(
                re.fullmatch(r"[123]", row["cycle"]) is not None
                and row["slot"] in SLOTS
                and re.fullmatch(r"[1-7]", row["repetition"]) is not None
                and re.fullmatch(r"[1-9][0-9]*", row["sample_ns"]) is not None,
                f"{path}:{number}: non-canonical sample identity",
            )
            cycle = int(row["cycle"])
            slot = row["slot"]
            repetition = int(row["repetition"])
            require(
                row["role"] == ("control" if slot.startswith("A") else "candidate"),
                f"{path}:{number}: slot/role mismatch",
            )
            identity = (metric, cycle, slot, repetition)
            require(identity not in observed, f"{path}:{number}: duplicate sample identity")
            observed.add(identity)
            sample_ns = int(row["sample_ns"])
            require(
                expected_sample_ns.get(identity) == sample_ns,
                f"{path}:{number}: sample is not bound to its sealed raw result",
            )
            try:
                tps = float(row["tps"])
            except ValueError as exc:
                raise ValueError(f"{path}:{number}: invalid throughput") from exc
            require(
                math.isfinite(tps)
                and tps > 0.0
                and math.isclose(
                    tps,
                    tokens * 1_000_000_000.0 / sample_ns,
                    rel_tol=0.0,
                    abs_tol=1e-9,
                ),
                f"{path}:{number}: throughput does not match sample_ns",
            )
            groups.setdefault(metric, {}).setdefault(cycle, {}).setdefault(
                slot, []
            ).append(tps)
    require(
        observed == set(expected_sample_ns) and len(observed) == 336,
        f"{path}: expected the exact sealed 336-sample inventory",
    )
    require(set(groups) == set(METRIC_SPECS), f"{path}: missing Llama 2 result cell")
    for key, cycles in groups.items():
        if sorted(cycles) != [1, 2, 3]:
            raise ValueError(f"{key}: expected cycles 1,2,3")
        for cycle, slots in cycles.items():
            if set(slots) != set(SLOTS) or any(
                len(samples) != 7 for samples in slots.values()
            ):
                raise ValueError(f"{key} cycle {cycle}: expected A1/B1/B2/A2 with r7")
    return groups


def bootstrap(cycles: list[dict[str, list[float]]], seed_material: str, absolute_candidate: bool) -> tuple[list[float], list[float] | None]:
    seed = int.from_bytes(hashlib.sha256(seed_material.encode()).digest()[:8], "big")
    rng = common.SplitMix64(seed)
    gains: list[float] = []
    candidate_means: list[float] = []
    for _ in range(REPLICATES):
        ratios: list[float] = []
        candidates: list[float] = []
        for _cycle in cycles:
            cycle = cycles[rng.randbelow(len(cycles))]
            means = {}
            for slot in SLOTS:
                samples = cycle[slot]
                means[slot] = sum(samples[rng.randbelow(len(samples))] for _ in samples) / len(samples)
            control = (means["A1"] + means["A2"]) / 2
            candidate = (means["B1"] + means["B2"]) / 2
            ratios.append(candidate / control)
            candidates.append(candidate)
        gains.append(100 * (statistics.fmean(ratios) - 1))
        if absolute_candidate:
            candidate_means.append(statistics.fmean(candidates))
    gains.sort()
    gain_ci = [common.quantile_type7(gains, 0.025), common.quantile_type7(gains, 0.975)]
    if not absolute_candidate:
        return gain_ci, None
    candidate_means.sort()
    return gain_ci, [common.quantile_type7(candidate_means, 0.025), common.quantile_type7(candidate_means, 0.975)]


def calculate(cycles_by_number: dict[int, dict[str, list[float]]], seed_material: str, absolute_candidate: bool) -> dict[str, Any]:
    cycles = [cycles_by_number[index] for index in sorted(cycles_by_number)]
    ratios = []
    control_samples: list[float] = []
    candidate_samples: list[float] = []
    cycle_gains = []
    for slots in cycles:
        means = {slot: statistics.fmean(samples) for slot, samples in slots.items()}
        control = (means["A1"] + means["A2"]) / 2
        candidate = (means["B1"] + means["B2"]) / 2
        ratio = candidate / control
        ratios.append(ratio)
        cycle_gains.append(100 * (ratio - 1))
        control_samples.extend(slots["A1"] + slots["A2"])
        candidate_samples.extend(slots["B1"] + slots["B2"])
    gain_ci, candidate_ci = bootstrap(cycles, seed_material, absolute_candidate)
    return {
        "control_mean_tps": statistics.fmean(control_samples),
        "candidate_mean_tps": statistics.fmean(candidate_samples),
        "cycle_gain_pct": cycle_gains,
        "paired_mean_gain_pct": 100 * (statistics.fmean(ratios) - 1),
        "bootstrap_gain_ci_95_pct": gain_ci,
        "bootstrap_candidate_ci_95_tps": candidate_ci,
    }


def analyze_campaign(
    slug: str, evidence: Path = EVIDENCE
) -> dict[str, dict[str, Any]]:
    directory = evidence / f"campaigns/{slug}"
    analysis = strict_json_file(directory / "analysis.json")
    expected = EXPECTED_CAMPAIGNS[slug]
    source_entries = parse_source_seal(directory / "source-files.sha256")
    records, input_hashes = load_campaign_raw_records(
        directory, expected["metadata"]["artifact_root"], source_entries
    )
    if analysis.get("input_result_sha256") != input_hashes:
        raise ValueError(f"{slug}: exported raw result hashes do not match accepted analysis inputs")
    if slug in ("llama2-attention", "llama2-retained-a551"):
        groups = load_groups(
            directory / "raw-samples.csv",
            raw_result_sample_ns(records, expected["metadata"]["artifact_root"]),
        )
        seed = lambda key: f"llama2-scoreboard-abba-v1\0{20260717}\0{key}"
        expected_root = analysis["metrics"]
        expected_ci = "bootstrap_gain_ci_95_pct"
        absolute = True
    else:
        raise ValueError(f"unknown campaign: {slug}")

    results = {}
    for key in METRIC_SPECS:
        cycles = groups[key]
        result = calculate(cycles, seed(key), absolute)
        expected = expected_root[key]
        close(result["control_mean_tps"], expected["control_mean_tps"], f"{slug}/{key} control")
        close(result["candidate_mean_tps"], expected["candidate_mean_tps"], f"{slug}/{key} candidate")
        close(result["paired_mean_gain_pct"], expected["paired_mean_gain_pct"], f"{slug}/{key} gain")
        for index in range(2):
            close(result["bootstrap_gain_ci_95_pct"][index], expected[expected_ci][index], f"{slug}/{key} CI[{index}]")
        if absolute:
            for index in range(2):
                close(result["bootstrap_candidate_ci_95_tps"][index], expected["bootstrap_candidate_ci_95_tps"][index], f"{slug}/{key} absolute CI[{index}]")
        results[key] = result
    return results


def render_markdown(campaigns: dict[str, dict[str, dict[str, Any]]]) -> str:
    lines = [
        "# Regenerated public results", "",
        "Generated from the committed `raw-samples.csv` files with 100,000 deterministic hierarchical bootstrap replicates.", "",
        "| Campaign | Cell | Control t/s | Candidate t/s | Paired gain | 95% CI |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for campaign, cells in campaigns.items():
        for cell, result in cells.items():
            ci = result["bootstrap_gain_ci_95_pct"]
            lines.append(
                f"| {campaign} | {cell} | {result['control_mean_tps']:.3f} | "
                f"{result['candidate_mean_tps']:.3f} | {result['paired_mean_gain_pct']:+.3f}% | "
                f"[{ci[0]:+.3f}%, {ci[1]:+.3f}%] |"
            )
    lines.append("")
    return "\n".join(lines)


def regenerated_outputs(evidence: Path = EVIDENCE) -> dict[str, bytes]:
    validate_evidence_index(evidence)
    campaigns = {slug: analyze_campaign(slug, evidence) for slug in CAMPAIGN_SLUGS}
    payload = {
        "schema": RESULTS_SCHEMA,
        "bootstrap_replicates": REPLICATES,
        "campaigns": campaigns,
    }
    return {
        "results.json": (
            json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
        ).encode("utf-8"),
        "results.md": render_markdown(campaigns).encode("utf-8"),
    }


def validate_evidence_tree(evidence: Path = EVIDENCE) -> dict[str, bytes]:
    verify_evidence_checksums(evidence)
    outputs = regenerated_outputs(evidence)
    regenerated = evidence / "regenerated"
    require(
        regenerated.is_dir() and not regenerated.is_symlink(),
        f"missing regenerated evidence directory: {regenerated}",
    )
    actual_names = sorted(path.name for path in regular_files(regenerated))
    require(
        actual_names == sorted(outputs),
        "regenerated evidence directory has an unexpected file set",
    )
    for name, data in outputs.items():
        require(
            (regenerated / name).read_bytes() == data,
            f"committed regenerated output is stale or mutated: {name}",
        )
    verify_evidence_checksums(evidence)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", type=Path, default=EVIDENCE)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    evidence = args.evidence_dir.absolute()
    outputs = validate_evidence_tree(evidence)
    if args.output_dir is not None:
        output = args.output_dir.absolute()
        default_output = evidence / "regenerated"
        if output != default_output:
            try:
                output.relative_to(evidence)
            except ValueError:
                pass
            else:
                raise ValueError(
                    "alternate output directory must be outside the sealed evidence tree"
                )
            output.mkdir(parents=True, exist_ok=True)
            existing = {
                path.name for path in output.iterdir()
            } if output.exists() else set()
            require(
                existing <= set(outputs),
                f"unexpected files in output directory: {sorted(existing - set(outputs))}",
            )
            for name, data in outputs.items():
                (output / name).write_bytes(data)
    verify_evidence_checksums(evidence)
    row_count = sum(
        len(cells)
        for cells in strict_json_loads(
            outputs["results.json"], "regenerated results"
        )["campaigns"].values()
    )
    print(f"regenerated and verified {row_count} result rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
