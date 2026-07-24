# Retained Llama 2 Navi22 supplement

This directory packages the exact net source delta from the validated nine-patch
public-final tree to the final retained Llama 2 Q4_0 tree.

- Official llama.cpp base: `86d86ed4396b4130922f7b9af26e3d9fc11a591b`
- Prerequisite nine-patch tree: `181e8fccc75423329c07885b5b853dd92a0520b8`
- Benchmarked retained commit: `a551cb0142e68139f4ab953bf9233b4dbeefa4f3`
- Expected retained tree: `2d3add3e01638795ff1cdc45273375ff4f455b52`
- Canonical prerequisite-to-retained tree-diff SHA-256:
  `3da21181b5f3f4f7e5ff0bd0572000f50b87c291e345a6a597fa5a5be78e5d67`

The supplement is a clean squashed patch. It deliberately excludes the long
experimental history between the accepted public-final tree and `a551cb014`,
which contains rejected and reverted experiments. Applying the supplement
produces a source tree byte-identical to the tree used by the final retained r7
campaign.

Apply the prerequisite series and this supplement from the repository root:

```bash
scripts/apply_llamacpp_navi22_retained_a551.sh /path/to/clean/llama.cpp
```

The target must be clean and checked out at the official base. The script
verifies both patch manifests and both intermediate/final tree hashes. The
existing nine-patch profile remains unchanged because its earlier release
evidence is pinned to the prerequisite tree.

This is a custom-fork source package, not an accepted Vulkan scoreboard
submission. It is outside the scoreboard's stated master-branch scope unless a
curator explicitly grants an exception. Upstream llama.cpp license and
copyright notices remain authoritative and are preserved.
