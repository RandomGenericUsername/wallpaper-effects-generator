# Basic Examples

Simple usage examples.

---

## List Available Effects

```bash
wallpaper-effects show all
```

---

## Apply Blur Effect

```bash
wallpaper-effects process effect wallpaper.png blurred.png -e blur
```

---

## Apply Blur with Custom Radius

```bash
wallpaper-effects process effect wallpaper.png blurred.png -e blur --blur 0x12
```

---

## Apply Composite

```bash
wallpaper-effects process composite wallpaper.png dark.png -c blur-brightness80
```

---

## Apply Preset

```bash
wallpaper-effects process preset wallpaper.png warm.png -p warm_overlay
```

---

## Batch Generate All Effects

```bash
wallpaper-effects batch effects wallpaper.png /output/dir
```

---

## Batch Generate Everything

```bash
wallpaper-effects batch all wallpaper.png /output/dir
```

---

## Use Podman Instead of Docker

```bash
wallpaper-effects --runtime podman batch all wallpaper.png /output
```

---

## Quiet Mode

```bash
wallpaper-effects -q batch all wallpaper.png /output
```

---

## Verbose Mode

```bash
wallpaper-effects -v batch all wallpaper.png /output
```

---

## See Also

- [Advanced Examples](advanced.md)
- [Usage Guide](../guides/usage.md)

