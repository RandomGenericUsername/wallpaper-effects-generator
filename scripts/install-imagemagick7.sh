#!/usr/bin/env bash
# install-imagemagick7.sh — put a real `magick` (ImageMagick 7) on PATH for CI.
#
# WHY. The effects catalog shells out to `magick`, and the local backend probes
# for it (`SubprocessCommandRunner._detect_binary`), so the contract-conformance
# test needs ImageMagick 7 for real — a skip would make the gate green without
# ever producing an artifact. GitHub's Ubuntu runner image provides no `magick`
# (no ImageMagick entry in the runner image manifest), so the pytest jobs install
# the pinned upstream static build here: a fixed version, a fixed SHA-256, no
# `latest`.
#
# The AppImage is *extracted* (`--appimage-extract`), not executed via FUSE, and
# the extracted tree is installed under $IMAGEMAGICK_PREFIX; a `magick` symlink
# points at its AppRun. AppRun resolves its own directory with `readlink` and
# exports MAGICK_HOME/LD_LIBRARY_PATH before exec'ing the bundled binary, so the
# check below runs under a normal system PATH and pins the exact version — a
# stub or a different ImageMagick cannot satisfy it.
#
# Idempotent: a real ImageMagick 7 already on PATH is left alone (a developer's
# machine or a future runner image). Anything else is installed.
#
# Usage: scripts/install-imagemagick7.sh
#   IMAGEMAGICK_PREFIX  install root (default: $HOME/.local/opt/imagemagick-<version>)
#   IMAGEMAGICK_VERSION override the pinned version
#   IMAGEMAGICK_SHA256  override the pinned checksum (only with a version bump)
# In CI ($GITHUB_PATH set) the bin directory is appended for later steps.
set -euo pipefail

VERSION="${IMAGEMAGICK_VERSION:-7.1.2-34}"
SHA256="${IMAGEMAGICK_SHA256:-6e9edfd35d5f30b57c27533afe003d6085faaf8607b207426f398d11751acf93}"
PREFIX="${IMAGEMAGICK_PREFIX:-$HOME/.local/opt/imagemagick-$VERSION}"
ASSET="ImageMagick-$VERSION-gcc-x86_64.AppImage"
URL="https://github.com/ImageMagick/ImageMagick/releases/download/$VERSION/$ASSET"

if command -v magick >/dev/null 2>&1; then
  version_line="$(magick -version 2>/dev/null | head -n 1 || true)"
  case "$version_line" in
    *"ImageMagick 7"*)
      echo "magick already available: $(command -v magick) ($version_line)"
      exit 0
      ;;
  esac
fi

case "$(uname -s)-$(uname -m)" in
  Linux-x86_64) ;;
  *)
    echo "unsupported platform for the pinned AppImage: $(uname -s)-$(uname -m)" >&2
    exit 1
    ;;
esac

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

echo "downloading $URL"
curl -fsSL "$URL" -o "$tmp/$ASSET"
echo "$SHA256  $tmp/$ASSET" | sha256sum -c -
chmod +x "$tmp/$ASSET"
(cd "$tmp" && "./$ASSET" --appimage-extract >/dev/null)

rm -rf "$PREFIX"
mkdir -p "$PREFIX" "$PREFIX/bin"
cp -a "$tmp/squashfs-root/." "$PREFIX/"
ln -sfn "$PREFIX/AppRun" "$PREFIX/bin/magick"

installed="$(env -i PATH=/usr/bin:/bin "$PREFIX/bin/magick" -version | head -n 1)"
case "$installed" in
  *"ImageMagick $VERSION"*) echo "installed: $PREFIX/bin/magick ($installed)" ;;
  *)
    echo "installed binary did not report ImageMagick $VERSION: $installed" >&2
    exit 1
    ;;
esac

if [ -n "${GITHUB_PATH:-}" ]; then
  echo "$PREFIX/bin" >> "$GITHUB_PATH"
  echo "appended $PREFIX/bin to GITHUB_PATH"
else
  echo "add it to your shell: export PATH=\"$PREFIX/bin:\$PATH\""
fi
