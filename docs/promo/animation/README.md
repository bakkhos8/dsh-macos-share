# Promo motion graphic

A 24-second motion graphic for DSH Share, rendered entirely from this
repository: the share menu is drawn in code, the product icon comes from
`assets/icon/AppIcon.png`, and the copy matches the 0.2.0 release.

| File | What it is |
| --- | --- |
| `dsh-share-promo-loop.gif` | 9 s loop used at the top of the READMEs (committed) |
| `dsh-share-promo-square.mp4` | 1080×1080, 30 fps, H.264 (build product, not committed) |
| `dsh-share-promo-wide.mp4` | 1920×1080, 30 fps, H.264 (build product, not committed) |
| `render.py` | the renderer: design space, timeline and every frame |

## Rendering

Requirements: Python 3 with Pillow, and `ffmpeg` on `PATH`.

```bash
# inspect a few frames before committing to a full render
python3 docs/promo/animation/render.py --still 3.9 8.8 12.2 17.4 21.5

# square, for WeChat / Xiaohongshu
python3 docs/promo/animation/render.py --size 1080 --out docs/promo/animation/dsh-share-promo-square

# 16:9, for Bilibili / YouTube / X
python3 docs/promo/animation/render.py --width 1920 --height 1080 --out docs/promo/animation/dsh-share-promo-wide
```

A full render writes PNG frames next to the video and then encodes with
`libx264 -crf 18`. It takes roughly four minutes per format on an Apple Silicon
Mac.

Rebuild the README loop from a finished square video:

```bash
ffmpeg -y -ss 0.5 -t 8.9 -i docs/promo/animation/dsh-share-promo-square.mp4 \
  -vf "fps=14,scale=560:-1:flags=lanczos,palettegen=max_colors=180:stats_mode=diff" /tmp/pal.png
ffmpeg -y -ss 0.5 -t 8.9 -i docs/promo/animation/dsh-share-promo-square.mp4 -i /tmp/pal.png \
  -lavfi "fps=14,scale=560:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4" \
  docs/promo/animation/dsh-share-promo-loop.gif
```

## Timeline

| Time | Shot |
| --- | --- |
| 0.7 – 6.7 s | The macOS share menu opens; **DeepSeek Harness** appears at the bottom and highlights |
| 6.7 – 9.2 s | The menu steps aside, a Harness window slides in, and the shared items become draft attachments |
| 10.0 – 13.3 s | Three capability cards: several files, screenshots, links and text |
| 14.4 – 17.9 s | The three friction points (“no dragging”, “no copy-paste”, “no saving to the desktop”) are crossed out |
| 18.4 – 24.0 s | Icon, name, one-line description, platform line and the repository address |

Everything is drawn on a 1000 × 1000 design grid with the origin at the centre,
so the same choreography renders at any canvas size; wide canvases simply carry
more background. Colours are pre-blended over the background because Pillow's
`ImageDraw` does not alpha-composite every primitive.

The QR codes in this folder point at the repository and at the latest release.
