#!/usr/bin/env python3
"""Deterministic statistical primitives for public evidence regeneration."""

from __future__ import annotations

import math


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


class SplitMix64:
    """Small deterministic generator used by the sealed bootstrap protocol."""

    def __init__(self, seed: int):
        self.state = seed & ((1 << 64) - 1)

    def next(self) -> int:
        mask = (1 << 64) - 1
        self.state = (self.state + 0x9E3779B97F4A7C15) & mask
        value = self.state
        value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & mask
        value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & mask
        return (value ^ (value >> 31)) & mask

    def randbelow(self, stop: int) -> int:
        require(stop > 0, "randbelow requires a positive bound")
        modulus = 1 << 64
        limit = modulus - modulus % stop
        while True:
            value = self.next()
            if value < limit:
                return value % stop


def quantile_type7(values: list[float], probability: float) -> float:
    require(bool(values) and 0.0 <= probability <= 1.0, "invalid quantile input")
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    fraction = position - lower
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + fraction * (values[upper] - values[lower])
