# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Simple, slow reference implementations written with explicit Python loops,
used only for differential tests against the vectorized engine."""

from __future__ import annotations

import math

import numpy as np


def ref_disp(xi, xj, L, periodic):
    dx, dy = xj[0] - xi[0], xj[1] - xi[1]
    if periodic:
        dx -= L * round(dx / L)
        dy -= L * round(dy / L)
    return dx, dy


def ref_pairs(x, L, r, periodic):
    out = []
    n = len(x)
    for i in range(n):
        for j in range(i + 1, n):
            dx, dy = ref_disp(x[i], x[j], L, periodic)
            if math.hypot(dx, dy) <= r:
                out.append((i, j))
    return out


def ref_neighbours(x, L, r, periodic):
    nb = {i: [] for i in range(len(x))}
    for i, j in ref_pairs(x, L, r, periodic):
        nb[i].append(j)
        nb[j].append(i)
    return nb


def _arg_or_keep(vx, vy, th):
    return math.atan2(vy, vx) if math.hypot(vx, vy) > 1e-12 else th


def ref_A0(x, theta, L, r, periodic):
    nb = ref_neighbours(x, L, r, periodic)
    out = []
    for i in range(len(x)):
        sx, sy = math.cos(theta[i]), math.sin(theta[i])
        for j in nb[i]:
            sx += math.cos(theta[j])
            sy += math.sin(theta[j])
        out.append(_arg_or_keep(sx, sy, theta[i]))
    return np.array(out)


def ref_A1(x, theta, L, r, periodic, r_sep, w_a, w_c):
    nb = ref_neighbours(x, L, r, periodic)
    out = []
    for i in range(len(x)):
        sepx = sepy = 0.0
        has_sep = False
        for j in nb[i]:
            dx, dy = ref_disp(x[i], x[j], L, periodic)
            d = math.hypot(dx, dy)
            if d <= r_sep:
                has_sep = True
                if d > 0:
                    sepx -= dx / d
                    sepy -= dy / d
        if has_sep:
            out.append(_arg_or_keep(sepx, sepy, theta[i]))
            continue
        ax, ay = math.cos(theta[i]), math.sin(theta[i])
        mx = my = 0.0
        for j in nb[i]:
            ax += math.cos(theta[j])
            ay += math.sin(theta[j])
            dx, dy = ref_disp(x[i], x[j], L, periodic)
            mx += dx
            my += dy
        na = math.hypot(ax, ay)
        ax, ay = (ax / na, ay / na) if na > 1e-12 else (0.0, 0.0)
        if nb[i]:
            mx, my = mx / len(nb[i]), my / len(nb[i])
        nc = math.hypot(mx, my)
        cx, cy = (mx / nc, my / nc) if nc > 1e-12 else (0.0, 0.0)
        out.append(_arg_or_keep(w_a * ax + w_c * cx, w_a * ay + w_c * cy, theta[i]))
    return np.array(out)


def ref_A2(theta):
    gx = sum(math.cos(t) for t in theta)
    gy = sum(math.sin(t) for t in theta)
    if math.hypot(gx, gy) <= 1e-12:
        return np.array(theta, dtype=float)
    return np.full(len(theta), math.atan2(gy, gx))
