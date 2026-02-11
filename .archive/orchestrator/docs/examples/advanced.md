# Advanced Examples

Complex workflows and integrations.

---

## CI/CD Pipeline

### GitHub Actions

```yaml
name: Generate Wallpaper Effects

on:
  push:
    paths:
      - 'wallpapers/**'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Build container
        run: |
          cd wallpaper-effects-generator/orchestrator
          docker build -t wallpaper-effects -f docker/Dockerfile .

      - name: Install orchestrator
        run: |
          cd wallpaper-effects-generator/orchestrator
          uv sync

      - name: Generate effects
        run: |
          cd wallpaper-effects-generator/orchestrator
          for img in wallpapers/*.png; do
            uv run wallpaper-effects batch all "$img" output/
          done

      - name: Upload artifacts
        uses: actions/upload-artifact@v4
        with:
          name: wallpaper-effects
          path: output/
```

---

## Batch Processing Script

```bash
#!/bin/bash
# process-all-wallpapers.sh

INPUT_DIR="${1:-./wallpapers}"
OUTPUT_DIR="${2:-./output}"

mkdir -p "$OUTPUT_DIR"

for img in "$INPUT_DIR"/*.{png,jpg,jpeg}; do
    [ -f "$img" ] || continue
    echo "Processing: $img"
    wallpaper-effects batch all "$img" "$OUTPUT_DIR"
done

echo "Done! Output in $OUTPUT_DIR"
```

---

## Docker Compose Integration

```yaml
# docker-compose.yml
version: '3.8'

services:
  wallpaper-effects:
    build:
      context: ./orchestrator
      dockerfile: docker/Dockerfile
    volumes:
      - ./input:/input:ro
      - ./output:/output:rw
    command: wallpaper-effects-process batch all /input/wallpaper.png /output
```

Run:

```bash
docker-compose run wallpaper-effects
```

---

## Kubernetes Job

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: wallpaper-effects
spec:
  template:
    spec:
      containers:
        - name: effects
          image: wallpaper-effects:latest
          command:
            - wallpaper-effects-process
            - batch
            - all
            - /input/wallpaper.png
            - /output
          volumeMounts:
            - name: input
              mountPath: /input
              readOnly: true
            - name: output
              mountPath: /output
      volumes:
        - name: input
          configMap:
            name: wallpaper-input
        - name: output
          emptyDir: {}
      restartPolicy: Never
```

---

## See Also

- [Basic Examples](basic.md)
- [Container Management](../guides/containers.md)
