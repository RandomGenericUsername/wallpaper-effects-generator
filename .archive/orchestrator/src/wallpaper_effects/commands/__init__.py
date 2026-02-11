"""Commands module for wallpaper effects orchestrator."""

from wallpaper_effects.commands.install import run_install
from wallpaper_effects.commands.process import run_process
from wallpaper_effects.commands.show import run_show
from wallpaper_effects.commands.status import run_status

__all__ = [
    "run_install",
    "run_process",
    "run_show",
    "run_status",
]
