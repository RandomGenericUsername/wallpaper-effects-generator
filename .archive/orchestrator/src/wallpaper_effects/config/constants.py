"""Pinned versions and constants for container images and tools."""

# Base images with pinned versions for reproducibility
BASE_IMAGES = {
    "python": "python:3.12-slim-bookworm",
}

# Backend versions
BACKEND_VERSIONS = {
    "imagemagick": {
        "version": "6.9.11",  # Debian bookworm version
        "base_image": BASE_IMAGES["python"],
        "dependencies": [
            "pillow>=10.0.0",
            "pydantic>=2.11.9",
            "dynaconf>=3.2.0",
        ],
    },
    "pil": {
        "version": "pure-python",
        "base_image": BASE_IMAGES["python"],
        "dependencies": [
            "pillow>=10.0.0",
            "pydantic>=2.11.9",
            "dynaconf>=3.2.0",
        ],
    },
}

# Environment defaults
DEFAULT_BACKEND = "imagemagick"
DEFAULT_BACKENDS = ["imagemagick", "pil"]
DEFAULT_OUTPUT_DIR = "~/.config/wallpaper-effects/output"
DEFAULT_CONFIG_DIR = "~/.config/wallpaper-effects"

# Container settings
CONTAINER_TIMEOUT = 300  # 5 minutes
CONTAINER_MEMORY_LIMIT = "1g"  # Higher for image processing
CONTAINER_CPUSET_CPUS = None  # No limit by default

# Container mount points (fixed paths inside container)
CONTAINER_INPUT_DIR = "/input"
CONTAINER_OUTPUT_DIR = "/output"
CONTAINER_CONFIG_DIR = "/config"

# Docker/Podman configuration
RUNTIME_DETECTION_ORDER = ["docker", "podman"]
RUNTIME_DEFAULTS = {
    "docker": {"command": "docker"},
    "podman": {"command": "podman"},
}

