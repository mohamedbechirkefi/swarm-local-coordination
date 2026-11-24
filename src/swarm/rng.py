# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Seeded random streams shared across arms (common random numbers).

A master seed spawns three independent ``numpy.random.SeedSequence`` children:
initial state, per-step noise, disturbance. None of them depends on the arm,
so A0, A1 and A2 with the same seed see identical initial positions,
headings, noise draws and shocked agents (protocol section 5).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

STREAMS = ("init", "noise", "disturb")


@dataclass
class Streams:
    init: np.random.Generator
    noise: np.random.Generator
    disturb: np.random.Generator


def make_streams(seed: int) -> Streams:
    if isinstance(seed, bool) or not isinstance(seed, int) or seed < 0:
        raise ValueError(f"seed must be a non-negative integer, got {seed!r}")
    children = np.random.SeedSequence(seed).spawn(len(STREAMS))
    gens = [np.random.Generator(np.random.PCG64(c)) for c in children]
    return Streams(*gens)
