from __future__ import annotations

from importlib.metadata import version as dist_version

from cli_invocation_contract import CONTRACT_VERSION
from typer.testing import CliRunner

from wallpaper_effects_generator.cli.main import app


def test_contract_version_pin_is_v020() -> None:
    """The pinned `contracts` tag and the token the CLI prints must agree.

    The token is read from `cli_invocation_contract.CONTRACT_VERSION`, never
    duplicated in this repo; pinning it explicitly here is what turns a stale
    `[tool.uv.sources]` tag into a red test instead of a silently consistent
    `--version` line. Bump this assertion together with the tag (v0.2.0).
    """
    assert CONTRACT_VERSION == "0.2.0"


def test_version_flag_reports_package_and_contract_version() -> None:
    result = CliRunner().invoke(app, ["--version"])

    assert result.exit_code == 0, result.output
    assert result.stdout.strip() == (
        f"{dist_version('wallpaper-effects-generator')} contract {CONTRACT_VERSION}"
    )
