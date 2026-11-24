# SPDX-License-Identifier: LicenseRef-SWARM-NC-Research-1.0
"""Versioned JSON schemas, validated at export and at import (fail closed).

Schema versions follow semantic versioning. A reader accepts only the exact
major version it was written for; anything else is rejected.
"""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

RESULT_SCHEMA_VERSION = "1.0.0"
EXPERIMENT_SCHEMA_VERSION = "1.0.0"

_num_or_null = {"type": ["number", "null"]}
_sha256 = {"type": "string", "pattern": "^[0-9a-f]{64}$"}

SIM_CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "arm": {"enum": ["A0", "A1", "A2"]},
        "n_agents": {"type": "integer", "minimum": 1},
        "density": {"type": "number", "exclusiveMinimum": 0},
        "noise": {"type": "number", "minimum": 0, "maximum": 1},
        "radius": {"type": "number", "exclusiveMinimum": 0},
        "speed": {"type": "number", "minimum": 0},
        "steps": {"type": "integer", "minimum": 1},
        "t_disturb": {"type": "integer", "minimum": 0},
        "window": {"type": "integer", "minimum": 0},
        "shock_fraction": {"type": "number", "minimum": 0, "maximum": 1},
        "sep_ratio": {"type": "number", "minimum": 0, "maximum": 1},
        "w_align": {"type": "number", "minimum": 0},
        "w_cohesion": {"type": "number", "minimum": 0},
        "collision_ratio": {"type": "number", "minimum": 0, "maximum": 1},
        "recovery_threshold": {"type": "number", "exclusiveMinimum": 0, "maximum": 1},
        "recovery_hold": {"type": "integer", "minimum": 1},
        "pre_window": {"type": "integer", "minimum": 0},
        "boundary": {"enum": ["periodic", "reflecting"]},
        "neighbourhood": {"enum": ["metric", "topological"]},
        "k_topological": {"type": "integer", "minimum": 1},
        "index": {"enum": ["cell", "brute"]},
        "seed": {"type": "integer", "minimum": 0},
    },
}

MANIFEST_SCHEMA = {
    "type": "object",
    "required": ["run_id", "config_hash", "seed", "git_revision", "git_dirty", "package_version",
                 "python", "numpy", "os", "cpu", "started_utc", "finished_utc", "runtime_s",
                 "peak_rss_bytes", "command"],
    "properties": {
        "run_id": {"type": "string"},
        "config_hash": _sha256,
        "seed": {"type": "integer"},
        "git_revision": {"type": "string"},
        "git_dirty": {"type": ["boolean", "null"]},
        "package_version": {"type": "string"},
        "python": {"type": "string"},
        "numpy": {"type": "string"},
        "os": {"type": "string"},
        "cpu": {"type": "string"},
        "started_utc": {"type": "string"},
        "finished_utc": {"type": "string"},
        "runtime_s": {"type": "number", "minimum": 0},
        "peak_rss_bytes": {"type": ["integer", "null"]},
        "command": {"type": "string"},
    },
}

RESULT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "SWARM run result",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "record_type", "experiment_id", "run_id", "label", "status",
                 "error", "config", "config_hash", "metrics", "timing", "series", "manifest"],
    "properties": {
        "schema_version": {"const": RESULT_SCHEMA_VERSION},
        "record_type": {"const": "swarm.run_result"},
        "experiment_id": {"type": "string", "pattern": "^EXP-[0-9]{3}$"},
        "run_id": {"type": "string", "minLength": 1},
        "label": {"enum": ["exploratory", "confirmatory"]},
        "status": {"enum": ["ok", "failed"]},
        "error": {"type": ["string", "null"]},
        "config": {**SIM_CONFIG_SCHEMA, "required": list(SIM_CONFIG_SCHEMA["properties"])},
        "config_hash": _sha256,
        "metrics": {
            "type": "object",
            "additionalProperties": False,
            "required": ["phi_pre", "phi_post", "tau", "tau_censored", "cohesion_post",
                         "collisions_per_agent_per_100", "dist_evals_per_step"],
            "properties": {
                "phi_pre": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                "phi_post": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                "tau": {"type": ["integer", "null"], "minimum": 0},
                "tau_censored": {"type": ["boolean", "null"]},
                "cohesion_post": {"type": ["number", "null"], "exclusiveMinimum": 0, "maximum": 1},
                "collisions_per_agent_per_100": {"type": ["number", "null"], "minimum": 0},
                "dist_evals_per_step": {"type": ["number", "null"], "minimum": 0},
            },
        },
        "timing": {
            "type": "object",
            "properties": {
                "wall_s": _num_or_null,
                "wall_s_per_step": _num_or_null,
                "search_s_per_step": _num_or_null,
            },
        },
        "series": {
            "type": "object",
            "properties": {
                "phi": {"type": ["array", "null"], "items": {"type": "number", "minimum": 0, "maximum": 1}},
            },
            "required": ["phi"],
        },
        "manifest": MANIFEST_SCHEMA,
    },
}

EXPERIMENT_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "SWARM experiment configuration",
    "type": "object",
    "additionalProperties": False,
    "required": ["schema_version", "experiment_id", "label", "confirmatory", "description",
                 "base", "grid", "seeds", "output_dir"],
    "properties": {
        "schema_version": {"const": EXPERIMENT_SCHEMA_VERSION},
        "experiment_id": {"type": "string", "pattern": "^EXP-[0-9]{3}$"},
        "label": {"enum": ["exploratory", "confirmatory"]},
        "confirmatory": {"type": "boolean"},
        "description": {"type": "string"},
        "protocol_path": {"type": "string"},
        "base": SIM_CONFIG_SCHEMA,
        "grid": {"type": "object", "additionalProperties": {"type": "array", "minItems": 1}},
        "seeds": {"type": "array", "minItems": 1, "items": {"type": "integer", "minimum": 0},
                  "uniqueItems": True},
        "output_dir": {"type": "string", "minLength": 1},
        "store_series": {"type": "boolean"},
        "full_matrix_runs": {"type": "integer", "minimum": 1},
    },
}


class SchemaError(ValueError):
    """A record failed schema validation."""


def _validate(obj: object, schema: dict, what: str) -> None:
    try:
        jsonschema.validate(obj, schema, cls=jsonschema.Draft202012Validator)
    except jsonschema.ValidationError as exc:
        path = "/".join(str(p) for p in exc.absolute_path)
        raise SchemaError(f"invalid {what} at '{path}': {exc.message}") from None


def validate_result(record: dict) -> None:
    _validate(record, RESULT_SCHEMA, "run result")


def validate_experiment(config: dict) -> None:
    _validate(config, EXPERIMENT_SCHEMA, "experiment config")


def write_result(record: dict, path: Path) -> None:
    """Validate then write (never write an invalid record)."""
    validate_result(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(record, indent=1, allow_nan=False) + "\n", encoding="utf-8")


def read_result(path: Path) -> dict:
    """Read and validate; raises SchemaError on any mismatch (fail closed)."""
    try:
        record = json.loads(Path(path).read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SchemaError(f"{path}: not valid JSON ({exc})") from None
    validate_result(record)
    return record
