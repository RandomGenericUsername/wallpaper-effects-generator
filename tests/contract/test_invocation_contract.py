"""The repo's own side of the invocation contract (spine AD-4).

`cli_invocation_contract` owns the record; this module owns the proof that *this*
checkout satisfies it. The record's ``argv``/``env`` templates are rendered from
this module (never re-typed as literals, per AGENTS.md §2) and the installed
``weg`` console script is run for real, so a regression in the local backend or
the artifact layout fails here instead of in a consumer's suite.

The catalog shells out to ``magick`` (ImageMagick 7). The autouse fake in
``tests/conftest.py`` is disabled for the ``real_imagemagick`` marker: the
artifacts asserted below must be real pixels, and a host without ``magick``
fails rather than skips.
"""

from __future__ import annotations

import re
import shutil
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from cli_invocation_contract import get
from cli_invocation_contract.testkit import assert_cli_writes_artifacts

RECORD = get("weg")

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
WALLPAPER = FIXTURES / "wallpaper.png"

_PLACEHOLDER_RE = re.compile(r"^\{([a-z0-9_]+)\}(\?)?$")


def _render(token: str, values: Mapping[str, str]) -> str | None:
    """Render one record template token; ``None`` means an absent optional token."""
    match = _PLACEHOLDER_RE.match(token)
    if match is None:
        return token
    name, optional = match.groups()
    if name in values:
        value = values[name]
        if not value.strip():
            raise AssertionError(f"placeholder {name!r} resolved to an empty value")
        return value
    if optional:
        return None
    raise AssertionError(
        f"record placeholder {name!r} has no value; supplied one of {sorted(values)}"
    )


def _argv(record: Mapping[str, Any], values: Mapping[str, str]) -> list[str]:
    argv: list[str] = []
    for token in record["argv"]:
        rendered = _render(token, values)
        if rendered is not None:
            argv.append(rendered)
    return argv


def _env(record: Mapping[str, Any], values: Mapping[str, str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for key, template in record["env"]["injected"].items():
        rendered = _render(template, values)
        if rendered is None:
            raise AssertionError(f"record injects {key!r} as an absent optional")
        env[key] = rendered
    missing = sorted(set(record["env"]["required"]) - set(env))
    if missing:
        raise AssertionError(
            f"record requires {missing} but does not inject them; the test must source "
            "those values explicitly before running the CLI"
        )
    return env


def _console_script(binary: str) -> Path:
    """Return the installed console script, preferring the running interpreter's env."""
    candidate = Path(sys.executable).with_name(binary)
    if candidate.is_file():
        return candidate
    found = shutil.which(binary)
    if found is None:
        pytest.fail(
            f"{binary} console script not found next to {sys.executable} nor on PATH; "
            "run `make sync` first"
        )
    return Path(found)


@pytest.mark.real_imagemagick
def test_batch_all_writes_contract_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`assert_cli_writes_artifacts` on a real run of the recorded invocation."""
    binary = RECORD["binary"]
    if shutil.which("magick") is None:
        pytest.fail(
            "magick (ImageMagick 7) is not on PATH and the local backend shells out to it; "
            "install it or run `make imagemagick` (the pinned static build CI uses)"
        )
    if not WALLPAPER.is_file():
        pytest.fail(f"missing checked-in fixture {WALLPAPER}")

    weg = _console_script(binary)
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    values = {"wallpaper": str(WALLPAPER), "output_dir": str(output_dir)}

    # The testkit runs a bare argv, so env injection goes through the process env.
    for key, value in _env(RECORD, values).items():
        monkeypatch.setenv(key, value)

    artifacts = assert_cli_writes_artifacts(
        RECORD,
        binary,
        [str(weg), *_argv(RECORD, values)],
        output_dir,
    )

    assert artifacts, "the contract run exited 0 but matched no artifact"
    empty = [str(path) for path in artifacts if path.stat().st_size == 0]
    assert not empty, f"artifacts exist but carry no pixels (fake backend?): {empty}"
