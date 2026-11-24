# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Neighbour search: brute force reference, cell list, topological k-nearest.

Metric neighbourhoods use the rule ``distance <= r`` (ties at exactly r are
neighbours). Metric searches return undirected pairs (i < j) sorted
lexicographically, so the brute-force and cell-list outputs are directly
comparable. ``evals`` counts pair distance evaluations actually performed
(protocol section 4, secondary metric 4).
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np

from .geometry import displacement


@dataclass
class Pairs:
    """Undirected pairs i < j with displacement d (from i to j) and distance."""

    i: np.ndarray
    j: np.ndarray
    d: np.ndarray
    dist: np.ndarray
    evals: int

    def subset(self, mask: np.ndarray) -> "Pairs":
        return Pairs(self.i[mask], self.j[mask], self.d[mask], self.dist[mask], self.evals)


def _finish(i: np.ndarray, j: np.ndarray, x: np.ndarray, box: float, periodic: bool,
            radius: float, evals: int) -> Pairs:
    d = displacement(x[i], x[j], box, periodic)
    dist = np.hypot(d[:, 0], d[:, 1])
    keep = dist <= radius
    i, j, d, dist = i[keep], j[keep], d[keep], dist[keep]
    order = np.lexsort((j, i))
    return Pairs(i[order], j[order], d[order], dist[order], evals)


def _check_inputs(x: np.ndarray, box: float, radius: float) -> None:
    if x.ndim != 2 or x.shape[1] != 2:
        raise ValueError(f"positions must have shape (N, 2), got {x.shape}")
    if not np.all(np.isfinite(x)):
        raise ValueError("positions must be finite")
    if not (box > 0 and radius > 0):
        raise ValueError("box and radius must be > 0")


def brute_force_pairs(x: np.ndarray, box: float, radius: float, periodic: bool) -> Pairs:
    """Reference: every unordered pair is evaluated, N(N-1)/2 evaluations."""
    _check_inputs(x, box, radius)
    n = x.shape[0]
    i, j = np.triu_indices(n, k=1)
    return _finish(i.astype(np.int64), j.astype(np.int64), x, box, periodic, radius, int(i.size))


def cells_per_side(box: float, radius: float) -> int:
    """Largest m with cell side box/m >= r, with a 1e-9 relative safety margin."""
    return max(1, int(np.floor(box / (radius * (1.0 + 1e-9)))))


@lru_cache(maxsize=64)
def _neighbour_cells(m: int, periodic: bool) -> np.ndarray:
    """(m*m, 9) table of neighbouring cell ids, duplicates and outside cells set to -1."""
    table = -np.ones((m * m, 9), dtype=np.int64)
    for cx in range(m):
        for cy in range(m):
            seen: list[int] = []
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    nx, ny = cx + dx, cy + dy
                    if periodic:
                        nx, ny = nx % m, ny % m
                    elif not (0 <= nx < m and 0 <= ny < m):
                        continue
                    cid = nx * m + ny
                    if cid not in seen:
                        seen.append(cid)
            table[cx * m + cy, : len(seen)] = seen
    table.setflags(write=False)
    return table


def cell_list_pairs(x: np.ndarray, box: float, radius: float, periodic: bool) -> Pairs:
    """Cell-list search: only agents in the same or adjacent cells are evaluated."""
    _check_inputs(x, box, radius)
    n = x.shape[0]
    m = cells_per_side(box, radius)
    side = box / m
    c = np.clip(np.floor(x / side).astype(np.int64), 0, m - 1)
    cell = c[:, 0] * m + c[:, 1]
    order = np.argsort(cell, kind="stable")
    count = np.bincount(cell, minlength=m * m)
    start = np.concatenate(([0], np.cumsum(count)[:-1]))
    table = _neighbour_cells(m, periodic)

    a = np.repeat(np.arange(n, dtype=np.int64), 9)
    b = table[cell].ravel()
    valid = b >= 0
    a, b = a[valid], b[valid]
    cb = count[b]
    total = int(cb.sum())
    i = np.repeat(a, cb)
    offset = np.arange(total, dtype=np.int64) - np.repeat(np.cumsum(cb) - cb, cb)
    j = order[np.repeat(start[b], cb) + offset]
    keep = i < j
    i, j = i[keep], j[keep]
    return _finish(i, j, x, box, periodic, radius, int(i.size))


def metric_pairs(x: np.ndarray, box: float, radius: float, periodic: bool, index: str) -> Pairs:
    if index == "cell":
        return cell_list_pairs(x, box, radius, periodic)
    if index == "brute":
        return brute_force_pairs(x, box, radius, periodic)
    raise ValueError(f"unknown index {index!r}")


def topological_edges(x: np.ndarray, box: float, k: int, periodic: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
    """Directed edges receiver -> k nearest others (ties broken by lower index).

    Returns (receiver, other, displacement receiver->other, evals). Brute force.
    """
    _check_inputs(x, box, 1.0)
    n = x.shape[0]
    kk = min(k, n - 1)
    if kk <= 0:
        empty = np.zeros(0, dtype=np.int64)
        return empty, empty, np.zeros((0, 2)), 0
    d = displacement(x[:, None, :], x[None, :, :], box, periodic)
    dist = np.hypot(d[..., 0], d[..., 1])
    np.fill_diagonal(dist, np.inf)
    idx = np.argsort(dist, axis=1, kind="stable")[:, :kk]
    recv = np.repeat(np.arange(n, dtype=np.int64), kk)
    other = idx.ravel().astype(np.int64)
    return recv, other, d[recv, other], n * (n - 1) // 2
