#!/usr/bin/env python3
"""Layer priority example for layered-settings package.

This example demonstrates how configuration layers work together
and shows the priority order of different configuration sources.

Layer priority (lowest to highest):
1. Package defaults (flat format)
2. Project root settings.toml (namespaced format)
3. User config ~/.config/<app_name>/settings.toml (namespaced format)
4. CLI overrides (dotted path notation)
"""

import tempfile
from pathlib import Path

from layered_settings import SchemaRegistry, configure, get_config
from pydantic import BaseModel, Field


# Define configuration schemas
class CoreSettings(BaseModel):
    """Core application settings."""

    workers: int = Field(default=4)
    timeout: float = Field(default=30.0)
    debug: bool = Field(default=False)


class AppConfig(BaseModel):
    """Root configuration."""

    core: CoreSettings = Field(default_factory=CoreSettings)


def demonstrate_layers() -> None:
    """Demonstrate how different configuration layers override each other."""

    # Create temporary directory structure for this example
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # 1. Create package defaults file (flat format)
        defaults_file = temp_path / "defaults.toml"
        defaults_file.write_text("""
# Package defaults (flat format - no namespace prefix)
workers = 4
timeout = 30.0
debug = false
""")

        # 2. Create project settings file (namespaced format)
        project_file = temp_path / "settings.toml"
        project_file.write_text("""
# Project settings (namespaced format)
[core]
workers = 8
# Note: timeout and debug use package defaults
""")

        # 3. Create user config directory and file (namespaced format)
        user_config_dir = temp_path / ".config" / "layer-demo"
        user_config_dir.mkdir(parents=True)
        user_file = user_config_dir / "settings.toml"
        user_file.write_text("""
# User settings (namespaced format)
[core]
debug = true
# Note: workers uses project value, timeout uses package default
""")

        # Register schema with package defaults
        SchemaRegistry.clear()  # Clear any previous registrations
        SchemaRegistry.register(
            namespace="core",
            model=CoreSettings,
            defaults_file=defaults_file,
        )

        # Configure the system
        # NOTE: In a real application, you would use the actual home directory
        # and project root. Here we simulate by changing directories temporarily.
        import os

        original_cwd = os.getcwd()
        original_home = os.environ.get("HOME")

        try:
            # Set up environment to use our temporary directories
            os.chdir(temp_path)
            os.environ["HOME"] = str(temp_path)

            configure(root_model=AppConfig, app_name="layer-demo")

            # Get the merged configuration
            print("=" * 60)
            print("Layer Priority Demonstration")
            print("=" * 60)
            print()

            config = get_config()

            print("Final configuration values:")
            print(f"  workers: {config.core.workers}")
            print(f"  timeout: {config.core.timeout}")
            print(f"  debug: {config.core.debug}")
            print()

            print("Value sources:")
            print("  workers: 8 (from PROJECT settings.toml)")
            print("           - Package default was 4")
            print("           - Project override to 8")
            print()
            print("  timeout: 30.0 (from PACKAGE defaults.toml)")
            print("           - No overrides in project or user configs")
            print()
            print("  debug: True (from USER ~/.config/layer-demo/settings.toml)")
            print("           - Package default was False")
            print("           - User override to True")
            print()

            # Now demonstrate CLI override (highest priority)
            print("=" * 60)
            print("CLI Override (Highest Priority)")
            print("=" * 60)
            print()

            config_with_cli = get_config(overrides={"core.workers": 16})

            print("Final configuration with CLI override:")
            print(f"  workers: {config_with_cli.core.workers}")
            print(f"  timeout: {config_with_cli.core.timeout}")
            print(f"  debug: {config_with_cli.core.debug}")
            print()

            print("Value sources:")
            print("  workers: 16 (from CLI OVERRIDE)")
            print("           - Package default was 4")
            print("           - Project override to 8")
            print("           - CLI override to 16 (wins!)")
            print()

        finally:
            # Restore original environment
            os.chdir(original_cwd)
            if original_home:
                os.environ["HOME"] = original_home
            else:
                os.environ.pop("HOME", None)


def main() -> None:
    """Run the layer priority demonstration."""
    demonstrate_layers()


if __name__ == "__main__":
    main()
