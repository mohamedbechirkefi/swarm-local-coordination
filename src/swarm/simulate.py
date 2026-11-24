# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Simulation core: one run from a validated ``SimConfig`` to recorded series.

Step order for t = 0, ..., T-1 (synchronous update):
  1. if t == t_d, apply the heading shock to the pre-drawn agents;
  2. search neighbours of the state at t; record phi(t) and, in the post
     window [t_d, t_d + W), cohesion and collisions;
  3. compute desired headings with the arm's rule, add noise, wrap;
  4. move every agent by v0 along its new heading; apply the boundary.
phi is therefore recorded for t = 0..T-1; phi(t_d) is the shocked state.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import numpy as np

from . import rules
from .config import SimConfig
from .geometry import reflect, wrap_angle, wrap_positions
from .metrics import collision_rate, largest_component_fraction, polarization, recovery_time
from .neighbors import metric_pairs, topological_edges
from .rng import make_streams


class SimulationError(RuntimeError):
    """Non-finite state or violated invariant during a run."""


@dataclass
class SimResult:
    config: SimConfig
    phi: np.ndarray
    metrics: dict
    timing: dict
    trajectory: dict | None = field(default=None)


def initial_state(cfg: SimConfig) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.random.Generator]:
    """Initial positions and headings, the shock draw, and the noise stream."""
    st = make_streams(cfg.seed)
    L = cfg.box
    x = st.init.uniform(0.0, L, size=(cfg.n_agents, 2))
    x = wrap_positions(x, L)
    theta = wrap_angle(st.init.uniform(-np.pi, np.pi, size=cfg.n_agents))
    k = int(round(cfg.shock_fraction * cfg.n_agents))
    chosen = np.sort(st.disturb.choice(cfg.n_agents, size=k, replace=False)).astype(np.int64)
    new = wrap_angle(st.disturb.uniform(-np.pi, np.pi, size=k))
    return x, theta, chosen, new, st.noise


def _directed(pairs) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    recv = np.concatenate([pairs.i, pairs.j])
    other = np.concatenate([pairs.j, pairs.i])
    disp = np.concatenate([pairs.d, -pairs.d])
    dist = np.concatenate([pairs.dist, pairs.dist])
    return recv, other, disp, dist


def step_headings(cfg: SimConfig, x: np.ndarray, theta: np.ndarray, pairs) -> np.ndarray:
    """Desired headings (before noise) for the configured arm and neighbourhood."""
    if cfg.arm == "A2":
        return rules.centralized(theta)
    periodic = cfg.boundary == "periodic"
    if cfg.neighbourhood == "topological":
        recv, other, disp, _ = topological_edges(x, cfg.box, cfg.k_topological, periodic)
        dist = np.hypot(disp[:, 0], disp[:, 1])
    else:
        recv, other, disp, dist = _directed(pairs)
    if cfg.arm == "A0":
        return rules.align_only(theta, recv, other)
    return rules.zonal(theta, recv, other, disp, dist, cfg.sep_ratio * cfg.radius,
                       cfg.w_align, cfg.w_cohesion)


def run(cfg: SimConfig, record_trajectory: bool = False) -> SimResult:
    """Run one simulation. Raises ``SimulationError`` on non-finite state."""
    L = cfg.box
    periodic = cfg.boundary == "periodic"
    x, theta, chosen, new_headings, noise_rng = initial_state(cfg)
    n, T = cfg.n_agents, cfg.steps
    t_end = cfg.t_disturb + cfg.window
    d_c = cfg.collision_ratio * cfg.radius
    half = cfg.noise * np.pi

    phi = np.empty(T)
    evals_total = 0
    cohesion = []
    collisions = 0
    t_search = 0.0
    traj_x = [x.copy()] if record_trajectory else None
    traj_t = [theta.copy()] if record_trajectory else None

    t0 = time.perf_counter()
    for t in range(T):
        if t == cfg.t_disturb and chosen.size:
            theta = theta.copy()
            theta[chosen] = new_headings
            if record_trajectory:
                traj_t[-1] = theta.copy()
        ts = time.perf_counter()
        pairs = metric_pairs(x, L, cfg.radius, periodic, cfg.index)
        t_search += time.perf_counter() - ts
        evals_total += pairs.evals
        phi[t] = polarization(theta)
        if cfg.t_disturb <= t < t_end:
            cohesion.append(largest_component_fraction(n, pairs.i, pairs.j))
            collisions += int(np.count_nonzero(pairs.dist < d_c))

        desired = step_headings(cfg, x, theta, pairs)
        noise = noise_rng.uniform(-half, half, size=n)
        theta = wrap_angle(desired + noise)
        x = x + cfg.speed * np.stack([np.cos(theta), np.sin(theta)], axis=1)
        if periodic:
            x = wrap_positions(x, L)
        else:
            x, theta = reflect(x, theta, L)
        if not (np.all(np.isfinite(x)) and np.all(np.isfinite(theta))):
            raise SimulationError(f"non-finite state at step {t}")
        if np.any(x < 0.0) or np.any(x > L) or (periodic and np.any(x >= L)):
            raise SimulationError(f"position outside the box at step {t}")
        if record_trajectory:
            traj_x.append(x.copy())
            traj_t.append(theta.copy())
    wall = time.perf_counter() - t0

    pre_lo = cfg.t_disturb - cfg.pre_window
    phi_pre = float(phi[pre_lo:cfg.t_disturb].mean()) if cfg.pre_window > 0 else None
    metrics: dict = {"phi_pre": phi_pre, "phi_post": None, "tau": None, "tau_censored": None,
                     "cohesion_post": None, "collisions_per_agent_per_100": None,
                     "dist_evals_per_step": evals_total / T}
    if cfg.window > 0:
        metrics["phi_post"] = float(phi[cfg.t_disturb:t_end].mean())
        metrics["cohesion_post"] = float(np.mean(cohesion))
        metrics["collisions_per_agent_per_100"] = collision_rate(collisions, n, cfg.window)
        if phi_pre is not None:
            tau, cens = recovery_time(phi, cfg.t_disturb, cfg.window, phi_pre,
                                      cfg.recovery_threshold, cfg.recovery_hold)
            metrics["tau"], metrics["tau_censored"] = tau, cens
    timing = {"wall_s": wall, "wall_s_per_step": wall / T, "search_s_per_step": t_search / T}
    trajectory = None
    if record_trajectory:
        trajectory = {"x": np.array(traj_x), "theta": np.array(traj_t)}
    return SimResult(cfg, phi, metrics, timing, trajectory)
