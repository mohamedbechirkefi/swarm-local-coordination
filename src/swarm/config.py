# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Typed, validated simulation configuration.

Units: lengths in model units "u", time in steps, angles in radians,
speed in u per step, density in agents per u^2. Every field is validated at
construction; invalid input raises ``ConfigError`` (explicit error path).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass, fields

ARMS = ("A0", "A1", "A2")
BOUNDARIES = ("periodic", "reflecting")
NEIGHBOURHOODS = ("metric", "topological")
INDEXES = ("cell", "brute")


class ConfigError(ValueError):
    """Raised for any invalid simulation or experiment configuration."""


@dataclass(frozen=True)
class SimConfig:
    """One simulation run, fully specified (protocol section 2).

    arm: A0 alignment-only, A1 separation+cohesion+alignment, A2 centralized.
    n_agents: N. density: rho = N / L^2 (agents per u^2); L is derived.
    noise: eta in [0, 1]; heading noise ~ Uniform(-eta*pi, eta*pi).
    radius: communication radius r (u). speed: v0 (u per step).
    steps: T (number of recorded steps). t_disturb: t_d. window: W.
    shock_fraction: f. sep_ratio: r_s / r. w_align, w_cohesion: A1 weights.
    collision_ratio: d_c / r. recovery_threshold: fraction of phi_pre.
    recovery_hold: consecutive steps required for recovery.
    pre_window: steps before t_d averaged into phi_pre.
    boundary: periodic or reflecting. neighbourhood: metric or topological.
    k_topological: k for topological neighbourhoods.
    index: cell (cell list) or brute (brute force) for metric search.
    seed: master seed; RNG streams are spawned from it (rng.py).
    """

    arm: str = "A0"
    n_agents: int = 200
    density: float = 1.0
    noise: float = 0.3
    radius: float = 1.0
    speed: float = 0.05
    steps: int = 1000
    t_disturb: int = 500
    window: int = 500
    shock_fraction: float = 0.5
    sep_ratio: float = 0.25
    w_align: float = 1.0
    w_cohesion: float = 1.0
    collision_ratio: float = 0.1
    recovery_threshold: float = 0.9
    recovery_hold: int = 10
    pre_window: int = 100
    boundary: str = "periodic"
    neighbourhood: str = "metric"
    k_topological: int = 7
    index: str = "cell"
    seed: int = 0

    def __post_init__(self) -> None:
        validate_sim_config(self)

    @property
    def box(self) -> float:
        """Side length L = sqrt(N / rho), in u."""
        return math.sqrt(self.n_agents / self.density)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SimConfig":
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ConfigError(f"unknown config keys: {sorted(unknown)}")
        return cls(**data)

    def config_hash(self) -> str:
        """SHA-256 of the canonical JSON of the config (seed included)."""
        return canonical_hash(self.to_dict())


def canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), allow_nan=False)


def canonical_hash(obj: object) -> str:
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()


def _finite(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ConfigError(f"{name} must be a number, got {type(value).__name__}")
    if not math.isfinite(value):
        raise ConfigError(f"{name} must be finite, got {value}")
    return float(value)


def _int(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ConfigError(f"{name} must be an integer, got {type(value).__name__}")
    return value


def validate_sim_config(c: SimConfig) -> None:
    if c.arm not in ARMS:
        raise ConfigError(f"arm must be one of {ARMS}, got {c.arm!r}")
    if c.boundary not in BOUNDARIES:
        raise ConfigError(f"boundary must be one of {BOUNDARIES}, got {c.boundary!r}")
    if c.neighbourhood not in NEIGHBOURHOODS:
        raise ConfigError(f"neighbourhood must be one of {NEIGHBOURHOODS}, got {c.neighbourhood!r}")
    if c.index not in INDEXES:
        raise ConfigError(f"index must be one of {INDEXES}, got {c.index!r}")
    n = _int("n_agents", c.n_agents)
    if n < 1:
        raise ConfigError("n_agents must be >= 1")
    for name in ("steps", "t_disturb", "window", "recovery_hold", "pre_window", "k_topological", "seed"):
        _int(name, getattr(c, name))
    if c.seed < 0:
        raise ConfigError("seed must be >= 0")
    if c.density <= 0 or _finite("density", c.density) <= 0:
        raise ConfigError("density must be > 0")
    if not 0.0 <= _finite("noise", c.noise) <= 1.0:
        raise ConfigError("noise must be in [0, 1]")
    if _finite("radius", c.radius) <= 0:
        raise ConfigError("radius must be > 0")
    if _finite("speed", c.speed) < 0:
        raise ConfigError("speed must be >= 0")
    if c.steps < 1:
        raise ConfigError("steps must be >= 1")
    if not 0 <= c.t_disturb <= c.steps:
        raise ConfigError("t_disturb must be in [0, steps]")
    if c.window < 0 or c.t_disturb + c.window > c.steps:
        raise ConfigError("t_disturb + window must be <= steps")
    if c.pre_window < 0 or c.pre_window > c.t_disturb:
        raise ConfigError("pre_window must be in [0, t_disturb]")
    if not 0.0 <= _finite("shock_fraction", c.shock_fraction) <= 1.0:
        raise ConfigError("shock_fraction must be in [0, 1]")
    if not 0.0 <= _finite("sep_ratio", c.sep_ratio) <= 1.0:
        raise ConfigError("sep_ratio must be in [0, 1]")
    if _finite("w_align", c.w_align) < 0 or _finite("w_cohesion", c.w_cohesion) < 0:
        raise ConfigError("weights must be >= 0")
    if not 0.0 <= _finite("collision_ratio", c.collision_ratio) <= 1.0:
        raise ConfigError("collision_ratio must be in [0, 1]")
    if not 0.0 < _finite("recovery_threshold", c.recovery_threshold) <= 1.0:
        raise ConfigError("recovery_threshold must be in (0, 1]")
    if c.recovery_hold < 1:
        raise ConfigError("recovery_hold must be >= 1")
    if c.k_topological < 1:
        raise ConfigError("k_topological must be >= 1")
    box = math.sqrt(n / c.density)
    if c.boundary == "periodic" and c.radius >= box / 2:
        # Minimum-image distances are only unambiguous for r < L/2.
        raise ConfigError(f"radius {c.radius} must be < L/2 = {box / 2:.6g} for periodic boundaries")
