# Prerequisites

System requirements for `wallpaper-effects-process`.

---

## Required

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Runtime |
| uv | Latest | Package manager |
| ImageMagick | 7.x | Image processing |

### Install Python

```bash
# Ubuntu/Debian
sudo apt-get install python3.11

# Fedora
sudo dnf install python3.11

# Arch
sudo pacman -S python
```

### Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc  # or restart terminal
```

### Install ImageMagick

```bash
# Ubuntu/Debian
sudo apt-get install imagemagick

# Fedora
sudo dnf install ImageMagick

# Arch
sudo pacman -S imagemagick

# macOS
brew install imagemagick
```

---

## Verify Requirements

```bash
python3 --version    # Should be 3.11+
uv --version         # Should show uv version
magick --version     # Should show ImageMagick 7.x
```

---

## ImageMagick Policy (Ubuntu/Debian)

On some systems, ImageMagick may have restrictive policies. If you encounter permission errors:

```bash
# Edit policy file
sudo nano /etc/ImageMagick-7/policy.xml

# Comment out or modify restrictive policies
# <policy domain="path" rights="none" pattern="@*" />
```

---

## Optional Dependencies

| Package | Purpose |
|---------|---------|
| `rich` | Enhanced CLI output (included) |
| `typer` | CLI framework (included) |
| `pydantic` | Configuration validation (included) |

