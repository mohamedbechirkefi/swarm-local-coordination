# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Tests of the M4 evidence-audit helpers (experiments/audit_numbers.py) and the
exploratory derived quantities (experiments/exploratory_m4.py)."""

import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "experiments" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_matches_printed_precision_and_sign():
    au = _load("audit_numbers")
    assert au.matches("-0.307", -0.30712)
    assert au.matches("0.307", -0.30712)  # sign dropped in prose
    assert au.matches("0.125", 0.125)  # half to even and half up both accepted
    assert au.matches("0.13", 0.125)
    assert not au.matches("-0.308", -0.30712)
    assert not au.matches("1138.8", 1138.7262)


def test_flatten_paths_and_types():
    au = _load("audit_numbers")
    got = dict(au.flatten({"a": {"b": [1.5, "2.5", "x", None, True]}}))
    assert got == {"a.b[0]": 1.5, "a.b[1]": 2.5}


def test_skip_section_numbers_and_dois():
    au = _load("audit_numbers")
    text = "See Section 5.2 and https://doi.org/10.1103/PhysRevLett.75.1226;\n## 4.3 Statistics\nvalue 0.307"
    cleaned = au.SKIP.sub(" ", text)
    assert au.TOKEN.findall(cleaned) == ["0.307"]


def test_derived_change_drop_and_retained():
    ex = _load("exploratory_m4")
    phi = [0.8] * 3000 + [0.4] * 50 + [0.8] * 450
    rec = {"status": "ok", "config": {"t_disturb": 3000, "n_agents": 200},
           "series": {"phi": phi}, "metrics": {"phi_pre": 0.8, "phi_post": 0.76}}
    ex.derived([rec])
    m = rec["metrics"]
    b = math.sqrt(math.pi) / (2 * math.sqrt(200))
    assert math.isclose(m["x_change"], -0.04)
    assert math.isclose(m["x_drop"], 0.4)
    assert math.isclose(m["x_retained"], (0.4 - b) / (0.8 - b))
