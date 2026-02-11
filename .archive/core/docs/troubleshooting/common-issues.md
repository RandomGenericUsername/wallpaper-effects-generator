# Common Issues

Frequently encountered problems and solutions.

---

## ImageMagick Not Found

**Error:**

```
magick: command not found
```

**Solution:**

Install ImageMagick:

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

Verify:

```bash
magick --version
```

---

## ImageMagick Policy Restrictions

**Error:**

```
magick: attempt to perform an operation not allowed by the security policy
```

**Solution:**

Edit ImageMagick policy file:

```bash
sudo nano /etc/ImageMagick-7/policy.xml
# or
sudo nano /etc/ImageMagick-6/policy.xml
```

Comment out or modify restrictive policies.

---

## Command Not Found After Installation

**Error:**

```
wallpaper-effects-process: command not found
```

**Solution:**

Ensure `~/.local/bin` is in your PATH:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

Or use `uv run`:

```bash
cd core
uv run wallpaper-effects-process version
```

---

## Effect Not Found

**Error:**

```
Effect 'effect_name' not found
```

**Solution:**

1. Check available effects:
   ```bash
   wallpaper-effects-process show effects
   ```

2. Verify spelling

3. If custom effect, check `~/.config/wallpaper-effects/effects.yaml`

---

## Invalid Parameter Value

**Error:**

```
Invalid value for parameter 'blur': must match pattern
```

**Solution:**

Check parameter format. For blur geometry:

```bash
# Correct format: RADIUSxSIGMA
--blur 0x8

# Wrong
--blur 8
```

---

## Permission Denied

**Error:**

```
Permission denied: '/output/path'
```

**Solution:**

Ensure you have write permission to the output directory:

```bash
mkdir -p /output/path
chmod 755 /output/path
```

---

## Batch Generation Fails

**Problem:** Batch generation stops on first error.

**Solution:**

Use `--no-strict` to continue despite errors:

```bash
wallpaper-effects-process batch all input.png /output --no-strict
```

---

## Slow Processing

**Problem:** Batch processing is slow.

**Solutions:**

1. Ensure parallel mode is enabled (default)
2. Use smaller images for testing
3. Use SSD for output directory

```bash
# Force parallel mode
wallpaper-effects-process batch all input.png /output
# (parallel is default unless --sequential is specified)
```

---

## YAML Syntax Error

**Error:**

```
Error loading effects.yaml: YAML syntax error
```

**Solution:**

Validate your YAML:

```bash
python -c "import yaml; yaml.safe_load(open('effects.yaml'))"
```

Common issues:
- Missing quotes around strings with special characters
- Incorrect indentation
- Missing colons

---

## See Also

- [Error Reference](error-reference.md)
- [Prerequisites](../getting-started/prerequisites.md)
