# Error Reference

Index of error messages and their meanings.

---

## Exit Codes

| Code | Description |
|------|-------------|
| `0` | Success |
| `1` | General error |
| `2` | Invalid arguments |

---

## Error Messages

### Configuration Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Error loading effects.yaml` | YAML syntax error | Check YAML syntax |
| `Effect 'X' not found` | Unknown effect name | Check `show effects` |
| `Composite 'X' not found` | Unknown composite | Check `show composites` |
| `Preset 'X' not found` | Unknown preset | Check `show presets` |

### Execution Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `magick: command not found` | ImageMagick not installed | Install ImageMagick |
| `magick: security policy` | Policy restriction | Edit policy.xml |
| `Input file not found` | Invalid input path | Check file exists |
| `Permission denied` | No write access | Check permissions |

### Parameter Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `Invalid value for 'X'` | Wrong format | Check parameter type |
| `Value out of range` | Outside min/max | Use valid range |

---

## Debugging

Enable debug mode for more information:

```bash
wallpaper-effects-process -vv process effect in.png out.png -e blur
```

This shows:
- Commands being executed
- Parameter values
- Timing information

---

## See Also

- [Common Issues](common-issues.md)
