#!/usr/bin/env bash
# Package the approved PNG avatar as a multi-resolution macOS icon.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE="$ROOT/assets/icon/AppIcon.png"
SMALL_SOURCE="$ROOT/assets/icon/AppIcon-small.png"
BUILD="${DSH_BUILD_DIR:-$ROOT/build}"
OUTPUT="$BUILD/AppIcon.icns"
if [[ ! -f "$SOURCE" ]]; then
  echo "missing icon source: $SOURCE" >&2
  exit 1
fi
mkdir -p "$BUILD"
ICON_WORK="$(mktemp -d "$BUILD/.icons.XXXXXX")"
trap 'rm -rf "$ICON_WORK"' EXIT
ICONSET="$ICON_WORK/AppIcon.iconset"
mkdir -p "$ICONSET"
# Small representations come from a zoomed-in variant: the full composition turns
# into an unreadable smear at 16-64 px, which is exactly the size the Share menu uses.
for size in 16 32 128 256 512; do
  input="$SOURCE"
  if [[ "$size" -le 32 && -f "$SMALL_SOURCE" ]]; then
    input="$SMALL_SOURCE"
  fi
  sips -z "$size" "$size" "$input" --out "$ICONSET/icon_${size}x${size}.png" >/dev/null
  retina=$((size * 2))
  sips -z "$retina" "$retina" "$input" --out "$ICONSET/icon_${size}x${size}@2x.png" >/dev/null
done
iconutil --convert icns "$ICONSET" --output "$ICON_WORK/AppIcon.icns"
mv "$ICON_WORK/AppIcon.icns" "$OUTPUT"
echo "icon: $OUTPUT"
