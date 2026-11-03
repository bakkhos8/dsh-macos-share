#!/usr/bin/env python3
"""Render the DSH Share promo motion graphic.

Design space: 1000 x 1000 units, centre origin. For 16:9 canvases the stage
just carries more background on both sides, so the same choreography works.

    python3 docs/promo/animation/render.py --still 1.6 5.2 7.6 12 16 21
    python3 docs/promo/animation/render.py --size 1080 --out docs/promo/animation/dsh-share-promo-1080
"""
from __future__ import annotations

import argparse
import math
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ICON_PATH = os.path.join(ROOT, "assets", "icon", "AppIcon.png")

FPS = 30
DURATION = 24.0

FONT_CN = "/System/Library/Fonts/Hiragino Sans GB.ttc"
FONT_LATIN = "/System/Library/Fonts/Helvetica.ttc"

BG_TOP = (9, 12, 24)
BG_BOT = (20, 26, 46)
INK = (243, 246, 255)
INK_DIM = (172, 182, 206)
INK_FAINT = (124, 134, 158)
ACCENT = (96, 150, 255)
ACCENT_LIGHT = (146, 198, 255)

# Panel colours are pre-blended over the background: PIL's ImageDraw does not
# alpha-composite every primitive, so translucent whites would come out solid.
GLASS = (30, 36, 54)
GLASS_EDGE = (62, 72, 100)
GLASS_DEEP = (22, 27, 42)


# ---------------------------------------------------------------- easing
def clamp01(v: float) -> float:
    return 0.0 if v < 0 else 1.0 if v > 1 else v


def ease(p: float) -> float:
    p = clamp01(p)
    return 4 * p * p * p if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2


def ease_out(p: float) -> float:
    p = clamp01(p)
    return 1 - (1 - p) ** 3


def pop(p: float) -> float:
    p = clamp01(p)
    if p >= 1:
        return 1.0
    c1, c3 = 1.70158, 2.70158
    q = p - 1
    return 1 + (c3 + 1) * q ** 3 + c3 * q ** 2


def prog(t: float, t0: float, t1: float, fn=ease) -> float:
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return fn((t - t0) / (t1 - t0))


def window(t: float, t_in: float, d_in: float, t_out: float | None, d_out: float) -> float:
    a = ease(clamp01((t - t_in) / d_in)) if d_in else 1.0
    if t_out is not None:
        a *= 1 - ease(clamp01((t - t_out) / d_out))
    return clamp01(a)


def mix(c1, c2, p: float):
    return tuple(int(round(c1[i] + (c2[i] - c1[i]) * p)) for i in range(3))


def rgba(c, a: float = 1.0):
    return (c[0], c[1], c[2], int(round(clamp01(a) * 255)))


_FONTS: dict[tuple, ImageFont.FreeTypeFont] = {}


def font(size: float, weight: str = "r", latin: bool = False) -> ImageFont.FreeTypeFont:
    key = (round(size, 1), weight, latin)
    if key not in _FONTS:
        px = max(1, int(round(size)))
        if latin:
            _FONTS[key] = ImageFont.truetype(FONT_LATIN, px, index=1)
        else:
            _FONTS[key] = ImageFont.truetype(FONT_CN, px, index=2 if weight == "b" else 0)
    return _FONTS[key]


class Stage:
    def __init__(self, width: int, height: int, zoom: float = 1.0):
        self.w, self.h = width, height
        self.unit = min(width, height) / 1000.0 * zoom
        self.img = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        self.d = ImageDraw.Draw(self.img, "RGBA")
        self._tf = (0.0, 0.0, 1.0)
        self._stack: list[tuple[float, float, float]] = []

    # transform
    def push(self, dx=0.0, dy=0.0, s=1.0):
        self._stack.append(self._tf)
        ox, oy, os_ = self._tf
        self._tf = (ox + dx * os_, oy + dy * os_, os_ * s)

    def pop(self):
        self._tf = self._stack.pop()

    # coordinates
    def sx(self, v):
        return v * self.unit * self._tf[2]

    def pt(self, x, y):
        dx, dy, s = self._tf
        return (self.w / 2 + (x * s + dx) * self.unit, self.h / 2 + (y * s + dy) * self.unit)

    def box(self, x, y, w, h):
        x0, y0 = self.pt(x, y)
        return (x0, y0, x0 + self.sx(w), y0 + self.sx(h))

    # primitives
    def rrect(self, x, y, w, h, r=0, fill=None, outline=None, width=1):
        self.d.rounded_rectangle(
            self.box(x, y, w, h), radius=self.sx(r), fill=fill, outline=outline,
            width=max(1, int(round(self.sx(width)))),
        )

    def circle(self, x, y, r, fill=None, outline=None, width=1):
        cx, cy = self.pt(x, y)
        rr = self.sx(r)
        self.d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=fill, outline=outline,
                       width=max(1, int(round(self.sx(width)))))

    def line(self, x0, y0, x1, y1, fill=None, width=1):
        self.d.line([self.pt(x0, y0), self.pt(x1, y1)], fill=fill,
                    width=max(1, int(round(self.sx(width)))))

    def text(self, x, y, s, size, weight="r", color=INK, anchor="mm", alpha=1.0, latin=False,
             spacing=0.0):
        f = font(self.sx(size), weight, latin)
        fill = rgba(color, alpha)
        if spacing:
            widths = [self.d.textlength(ch, font=f) for ch in s]
            total = sum(widths) + self.sx(spacing) * (len(s) - 1)
            cx, cy = self.pt(x, y)
            cursor = cx - total / 2
            for ch, w in zip(s, widths):
                self.d.text((cursor, cy), ch, font=f, fill=fill, anchor="lm")
                cursor += w + self.sx(spacing)
            return
        self.d.text(self.pt(x, y), s, font=f, fill=fill, anchor=anchor)

    def shadow(self, x, y, w, h, r=24, blur=28, alpha=0.45, dy=14):
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer, "RGBA")
        d.rounded_rectangle(self.box(x, y + dy, w, h), radius=self.sx(r), fill=(0, 0, 0, int(alpha * 255)))
        layer = layer.filter(ImageFilter.GaussianBlur(max(1.0, self.sx(blur))))
        self.img.alpha_composite(layer)

    def glow(self, x, y, r, color=ACCENT, alpha=0.5, blur=40):
        layer = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer, "RGBA")
        cx, cy = self.pt(x, y)
        rr = self.sx(r)
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=rgba(color, alpha))
        layer = layer.filter(ImageFilter.GaussianBlur(max(1.0, self.sx(blur))))
        self.img.alpha_composite(layer)

    def icon(self, x, y, size, radius=None, alpha=1.0):
        """Paste the app icon cropped to its artwork, so no empty margin shows."""
        icon = Image.open(ICON_PATH).convert("RGBA")
        bbox = icon.getchannel("A").getbbox()
        if bbox:
            icon = icon.crop(bbox)
        target = max(1, int(round(self.sx(size))))
        icon = icon.resize((target, target), Image.LANCZOS)
        mask = Image.new("L", (target, target), 0)
        rr = self.sx(radius) if radius is not None else target * 0.225
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, target - 1, target - 1], radius=rr, fill=255)
        if alpha < 1:
            mask = mask.point(lambda v: int(v * clamp01(alpha)))
        cx, cy = self.pt(x, y)
        self.img.paste(icon, (int(round(cx - target / 2)), int(round(cy - target / 2))), mask)

    def save(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.img.convert("RGB").save(path)


# ---------------------------------------------------------------- background
def draw_background(st: Stage, t: float):
    w, h = st.img.size
    grad = Image.new("RGB", (1, h))
    for y in range(h):
        grad.putpixel((0, y), mix(BG_TOP, BG_BOT, (y / max(1, h - 1)) * 0.95))
    st.img.paste(grad.resize((w, h), Image.BILINEAR), (0, 0))

    drift = math.sin(t * 0.33) * 70
    st.glow(-240 + drift, -280 + math.cos(t * 0.27) * 40, 560, ACCENT, 0.22, 240)
    st.glow(320 - drift * 0.7, 260, 480, (124, 96, 226), 0.18, 260)

    step = max(8, int(st.sx(52)))
    off = int((t * st.sx(5)) % step)
    dot = (255, 255, 255, 15)
    size = max(1, int(round(st.sx(1.7))))
    for y in range(-step + off, h, step):
        for x in range(-step + off, w, step):
            st.d.ellipse([x, y, x + size, y + size], fill=dot)

    vig = Image.new("L", (w, h), 0)
    dv = ImageDraw.Draw(vig)
    inset = int(min(w, h) * 0.10)
    dv.ellipse([-inset, -inset, w + inset, h + inset], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.20)))
    black = Image.new("RGBA", (w, h), (0, 0, 0, 255))
    black.putalpha(vig.point(lambda v: int((255 - v) * 0.6)))
    st.img.alpha_composite(black)


# ---------------------------------------------------------------- share menu
MENU_SECTIONS = [
    ("notes", "备忘录", (248, 206, 88)),
    ("airdrop", "隔空投送", (74, 126, 236)),
    ("freeform", "无边记", (40, 52, 80)),
    ("workbuddy", "WorkBuddy", (76, 200, 138)),
    ("messages", "信息", (88, 210, 100)),
    ("mail", "邮件", (74, 140, 240)),
]

MENU_X, MENU_Y, MENU_W, MENU_H = -215, -350, 430, 700
ROW_H = 88
MENU_PAD = 18
MENU_TOP = 42


def glyph(st: Stage, kind: str, x, y, size, alpha=1.0):
    r = size * 0.28
    bg = dict((k, c) for k, _, c in MENU_SECTIONS)[kind]
    st.rrect(x - size / 2, y - size / 2, size, size, r, fill=rgba(bg, alpha))
    fg = (255, 255, 255, int(242 * alpha))
    if kind == "notes":
        for i in range(3):
            st.rrect(x - size * 0.24, y - size * 0.2 + i * size * 0.2, size * 0.48, size * 0.075,
                     size * 0.04, fill=fg)
    elif kind == "airdrop":
        st.circle(x, y + size * 0.04, size * 0.24, outline=fg, width=size * 0.07)
        st.line(x, y + size * 0.04, x, y - size * 0.24, fill=fg, width=size * 0.07)
        st.line(x - size * 0.11, y - size * 0.13, x, y - size * 0.24, fill=fg, width=size * 0.07)
        st.line(x + size * 0.11, y - size * 0.13, x, y - size * 0.24, fill=fg, width=size * 0.07)
    elif kind == "freeform":
        st.line(x - size * 0.24, y - size * 0.04, x - size * 0.05, y + size * 0.14, fill=fg, width=size * 0.07)
        st.line(x - size * 0.05, y + size * 0.14, x + size * 0.1, y - size * 0.2, fill=fg, width=size * 0.07)
        st.line(x + size * 0.1, y - size * 0.2, x + size * 0.26, y - size * 0.05, fill=fg, width=size * 0.07)
    elif kind == "workbuddy":
        st.circle(x - size * 0.11, y + size * 0.06, size * 0.13, fill=fg)
        st.circle(x + size * 0.11, y - size * 0.06, size * 0.13, fill=fg)
    elif kind == "messages":
        st.rrect(x - size * 0.3, y - size * 0.26, size * 0.6, size * 0.42, size * 0.12, fill=fg)
        st.line(x - size * 0.12, y + size * 0.16, x - size * 0.02, y + size * 0.3, fill=fg, width=size * 0.09)
    elif kind == "mail":
        st.rrect(x - size * 0.28, y - size * 0.18, size * 0.56, size * 0.36, size * 0.07, fill=fg)
        st.line(x - size * 0.26, y - size * 0.13, x, y + size * 0.06, fill=rgba(bg, alpha), width=size * 0.07)
        st.line(x + size * 0.26, y - size * 0.13, x, y + size * 0.06, fill=rgba(bg, alpha), width=size * 0.07)


def draw_share_menu(st: Stage, t: float):
    """0.7 - 9.4 s. Slides left and shrinks once the Harness window arrives."""
    a = window(t, 0.7, 0.6, 9.0, 0.5)
    if a <= 0.002:
        return
    shift = prog(t, 6.7, 7.7)
    st.push(dx=-296 * shift, dy=0, s=1 - 0.22 * shift)

    enter = (1 - ease(prog(t, 0.7, 1.4))) * 18
    st.shadow(MENU_X, MENU_Y + enter, MENU_W, MENU_H, r=34, blur=32, alpha=0.5 * a, dy=20)
    st.rrect(MENU_X, MENU_Y + enter, MENU_W, MENU_H, 34,
             fill=rgba((250, 251, 254), 0.98 * a),
             outline=rgba((255, 255, 255), 0.30 * a), width=1)

    press = ease(prog(t, 3.2, 3.9))
    for i, (kind, label, _) in enumerate(MENU_SECTIONS):
        row_a = a * ease(clamp01((t - 1.2 - i * 0.1) / 0.45))
        if row_a <= 0.002:
            continue
        rx, ry = MENU_X + MENU_PAD, MENU_Y + MENU_TOP + i * ROW_H + enter
        dim = 1 - 0.42 * press
        glyph(st, kind, rx + 40, ry + ROW_H / 2, 44, row_a * dim)
        st.text(rx + 82, ry + ROW_H / 2, label, 30, color=(40, 45, 58), anchor="lm", alpha=row_a * dim)

    # our entry
    a_row = a * ease(clamp01((t - 2.9) / 0.5))
    if a_row > 0.002:
        rx, ry = MENU_X + MENU_PAD, MENU_Y + MENU_TOP + 6 * ROW_H + enter
        st.line(rx + 10, ry - 6, rx + MENU_W - MENU_PAD * 2 - 10, ry - 6,
                fill=rgba((28, 34, 50), 0.12 * a_row), width=1)
        pulse = 0.5 + 0.5 * math.sin(t * 4.2)
        st.glow(rx + 40, ry + ROW_H / 2, 32 + 5 * pulse, ACCENT, (0.22 + 0.16 * press) * a_row, blur=26)
        st.rrect(rx + 2, ry + 7, MENU_W - MENU_PAD * 2 - 4, ROW_H - 14, 16,
                 fill=rgba(ACCENT, (0.16 + 0.16 * press) * a_row))
        st.icon(rx + 40, ry + ROW_H / 2, 44, radius=10, alpha=a_row)
        st.text(rx + 80, ry + ROW_H / 2, "DeepSeek Harness", 27, weight="b", color=(250, 251, 255),
                anchor="lm", alpha=a_row * (0.55 + 0.45 * press))
    st.pop()


# ---------------------------------------------------------------- harness window
HARNESS_X, HARNESS_Y, HARNESS_W, HARNESS_H = 92, -290, 398, 580


def draw_harness(st: Stage, t: float):
    """6.6 - 9.6 s: shared items land in the draft attachment rail."""
    a = window(t, 7.0, 0.7, 9.2, 0.45)
    if a <= 0.002:
        return
    enter = (1 - ease_out(prog(t, 7.0, 8.0))) * 60
    x = HARNESS_X + enter

    st.shadow(x, HARNESS_Y, HARNESS_W, HARNESS_H, r=26, blur=28, alpha=0.5 * a, dy=16)
    st.rrect(x, HARNESS_Y, HARNESS_W, HARNESS_H, 26, fill=rgba(GLASS, a), outline=rgba(GLASS_EDGE, a), width=1)

    for i, c in enumerate([(255, 104, 92), (255, 190, 74), (96, 208, 122)]):
        st.circle(x + 28 + i * 18, HARNESS_Y + 26, 4.5, fill=rgba(c, 0.9 * a))
    st.text(x + HARNESS_W / 2 + 14, HARNESS_Y + 26, "DeepSeek Harness", 19, color=INK_DIM, alpha=a)

    st.rrect(x + 26, HARNESS_Y + 68, 210, 62, 14, fill=rgba(GLASS_DEEP, a), outline=rgba(GLASS_EDGE, a))
    st.text(x + 44, HARNESS_Y + 84, "把这几份资料看一下", 18, color=INK_DIM, anchor="lm", alpha=a)
    st.text(x + 44, HARNESS_Y + 110, "顺便整理成一页摘要", 18, color=INK_DIM, anchor="lm", alpha=a)

    reply_a = window(t, 7.6, 0.5, 9.2, 0.45) * a
    if reply_a > 0.002:
        st.rrect(x + 26, HARNESS_Y + 168, 300, 74, 14, fill=rgba(GLASS_DEEP, reply_a),
                 outline=rgba(GLASS_EDGE, reply_a), width=1)
        dots = int((t - 7.6) * 3) % 3 + 1
        for k in range(3):
            r = 4.2 if k < dots else 3.0
            st.circle(x + 60 + k * 22, HARNESS_Y + 205, r, fill=rgba(INK_DIM, (0.95 if k < dots else 0.4) * reply_a))
        st.text(x + 150, HARNESS_Y + 205, "正在读取分享的文件", 14, color=INK_DIM, anchor="lm", alpha=reply_a)

    comp_y = HARNESS_Y + 300
    st.rrect(x + 26, comp_y, HARNESS_W - 52, 236, 20, fill=rgba(GLASS_DEEP, a),
             outline=rgba(GLASS_EDGE, a), width=1)
    st.text(x + 46, comp_y + 40, "帮我总结这几份资料", 20, color=INK, anchor="lm", alpha=a)

    items = [("文档 PDF", (255, 122, 112)), ("截图 PNG", (122, 192, 255)), ("链接", (154, 162, 255))]
    for i, (label, tint) in enumerate(items):
        t0 = 7.15 + i * 0.26
        ap = pop(prog(t, t0, t0 + 0.42))
        if ap <= 0.002:
            continue
        cx = x + 26 + 56 + i * 112
        cy = comp_y + 132
        bw, bh = 108 * ap, 64 * ap
        st.rrect(cx - bw / 2, cy - bh / 2, bw, bh, 12, fill=rgba((40, 47, 68), a * ap),
                 outline=rgba(tint, 0.55 * a * ap), width=1)
        st.rrect(cx - bw / 2 + 10, cy - 15, 22, 30, 6, fill=rgba(tint, a * ap))
        st.text(cx + 22, cy, label, 13, color=INK, alpha=a * ap)

    st.text(x + 26, comp_y + 196, "分享过来的文件会先变成草稿附件", 15, color=INK_FAINT, anchor="lm", alpha=a)


# ---------------------------------------------------------------- capability cards
def card_glyph(st: Stage, i: int, x, y, size, fill):
    if i == 0:  # several files
        st.rrect(x - size * 0.62, y - size * 0.62, size * 0.9, size * 1.1, size * 0.16,
                 outline=fill, width=size * 0.14)
        st.rrect(x - size * 0.28, y - size * 0.44, size * 0.9, size * 1.1, size * 0.16, fill=fill)
    elif i == 1:  # screenshot / image
        st.rrect(x - size * 0.6, y - size * 0.46, size * 1.2, size * 0.92, size * 0.16,
                 outline=fill, width=size * 0.14)
        st.circle(x - size * 0.26, y - size * 0.16, size * 0.12, fill=fill)
        st.line(x - size * 0.34, y + size * 0.36, x - size * 0.02, y - size * 0.02, fill=fill, width=size * 0.14)
        st.line(x - size * 0.02, y - size * 0.02, x + size * 0.34, y + size * 0.36, fill=fill, width=size * 0.14)
    else:  # link
        st.rrect(x - size * 0.66, y - size * 0.2, size * 0.66, size * 0.4, size * 0.2,
                 outline=fill, width=size * 0.14)
        st.rrect(x + size * 0.0, y - size * 0.2, size * 0.66, size * 0.4, size * 0.2,
                 outline=fill, width=size * 0.14)


CARDS = [
    ("多个文件", "一次带走", (96, 150, 255)),
    ("截图", "直接给它看", (120, 205, 255)),
    ("链接和文字", "直接给它读", (154, 162, 255)),
]


def draw_cards(st: Stage, t: float):
    """10.0 - 13.9 s: three capability cards."""
    a_all = window(t, 10.0, 0.4, 13.3, 0.5)
    if a_all <= 0.002:
        return
    st.text(0, -168, "分享什么都能接住", 42, weight="b", color=INK, alpha=a_all)
    cw, ch, gap = 288, 186, 20
    total = cw * 3 + gap * 2
    for i, (title, sub, tint) in enumerate(CARDS):
        p = prog(t, 10.0 + i * 0.22, 10.7 + i * 0.22, ease_out)
        if p <= 0.002:
            continue
        a = a_all * p
        x = -total / 2 + i * (cw + gap)
        y = -26 - (1 - p) * 36
        st.shadow(x, y, cw, ch, r=24, blur=20, alpha=0.4 * a, dy=12)
        st.rrect(x, y, cw, ch, 24, fill=rgba(GLASS, a), outline=rgba(GLASS_EDGE, a), width=1)
        st.rrect(x + 24, y + 24, 44, 44, 12, fill=rgba(tint, 0.9 * a))
        card_glyph(st, i, x + 46, y + 46, 22, rgba((10, 16, 30), 0.9 * a))
        st.text(x + 24, y + 100, title, 30, weight="b", color=INK, anchor="lm", alpha=a)
        st.text(x + 24, y + 140, sub, 22, color=INK_DIM, anchor="lm", alpha=a)


# ---------------------------------------------------------------- slogan
FRICTION = ["不用拖拽", "不用复制粘贴", "不用先存到桌面"]


def draw_slogan(st: Stage, t: float):
    """14.4 - 18.2 s: friction points crossed out, then the one-liner."""
    a_all = window(t, 14.4, 0.4, 17.9, 0.4)
    if a_all <= 0.002:
        return
    for i, line in enumerate(FRICTION):
        p = prog(t, 14.4 + i * 0.4, 14.95 + i * 0.4, ease_out)
        if p <= 0.002:
            continue
        strike = prog(t, 15.9 + i * 0.32, 16.4 + i * 0.32, ease_out)
        dim = mix(INK, INK_FAINT, strike)
        a = a_all * p
        y = -58 + i * 76 - (1 - p) * 16
        st.text(0, y, line, 46, weight="b", color=dim, alpha=a)
        if strike > 0:
            f = font(st.sx(46), "b")
            half = st.d.textlength(line, font=f) / 2 * strike
            cx, cy = st.pt(0, y)
            st.d.line([(cx - half, cy + st.sx(3)), (cx + half, cy + st.sx(3))],
                      fill=rgba((255, 136, 136), 0.85 * a), width=max(1, int(st.sx(3.4))))

    a2 = window(t, 17.0, 0.5, 18.1, 0.4)
    if a2 > 0.002:
        st.text(0, 214, "右键 → 分享 → 直接进对话", 44, weight="b", color=ACCENT_LIGHT, alpha=a2)


# ---------------------------------------------------------------- outro
def draw_outro(st: Stage, t: float):
    a = window(t, 18.4, 0.6, None, 0.1)
    if a <= 0.002:
        return
    p = pop(prog(t, 18.4, 19.3))
    st.glow(0, -176, 158, ACCENT, 0.32 * a * p, blur=70)
    st.icon(0, -176, 156 * (0.86 + 0.14 * p), alpha=a)
    st.text(0, -34, "DSH Share", 64, weight="b", color=INK, alpha=a)

    a2 = window(t, 19.2, 0.5, None, 0.1)
    st.text(0, 42, "DeepSeek Harness 的系统分享入口", 32, color=INK_DIM, alpha=a2)

    a3 = window(t, 19.8, 0.5, None, 0.1)
    st.text(0, 116, "开源免费  ·  macOS 13 起  ·  Apple 芯片与 Intel", 23, color=INK_FAINT, alpha=a3)

    a4 = window(t, 20.4, 0.5, None, 0.1)
    st.text(0, 190, "github.com/bakkhos8/dsh-macos-share", 24, color=ACCENT_LIGHT, alpha=a4, latin=True)


# ---------------------------------------------------------------- frame
def render_frame(st: Stage, t: float):
    draw_background(st, t)
    draw_share_menu(st, t)
    draw_harness(st, t)
    draw_cards(st, t)
    draw_slogan(st, t)
    draw_outro(st, t)

    alpha = max(1 - ease(clamp01(t / 0.6)), ease(clamp01((t - (DURATION - 0.6)) / 0.6)))
    if alpha > 0.002:
        veil = Image.new("RGBA", st.img.size, (0, 0, 0, 255))
        veil.putalpha(int(clamp01(alpha) * 255))
        st.img.alpha_composite(veil)


def render_video(out_base: str, width: int, height: int, fps: int = FPS, zoom: float = 1.0):
    frames_dir = out_base + "-frames"
    os.makedirs(frames_dir, exist_ok=True)
    total = int(round(DURATION * fps))
    for i in range(total):
        st = Stage(width, height, zoom)
        render_frame(st, i / fps)
        st.img.convert("RGB").save(os.path.join(frames_dir, f"f{i:05d}.png"))
        if i % 60 == 0:
            print(f"  frame {i}/{total}", flush=True)
    mp4 = out_base + ".mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps),
         "-i", os.path.join(frames_dir, "f%05d.png"),
         "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "slow",
         "-movflags", "+faststart", mp4],
        check=True,
    )
    print("wrote", mp4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--size", type=int, default=1080, help="square side for --still")
    ap.add_argument("--width", type=int, default=0)
    ap.add_argument("--height", type=int, default=0)
    ap.add_argument("--zoom", type=float, default=0.0, help="override the layout scale")
    ap.add_argument("--out", default=os.path.join(HERE, "dsh-share-promo"))
    ap.add_argument("--still", nargs="*", type=float, default=None)
    args = ap.parse_args()
    width = args.width or args.size
    height = args.height or args.size
    zoom = args.zoom or (1.0 if width == height else 1.28)

    if args.still:
        for t in args.still:
            st = Stage(width, height, zoom)
            render_frame(st, t)
            path = os.path.join(HERE, "stills", f"still-{t:05.1f}.png")
            st.save(path)
            print("wrote", path)
        return

    render_video(os.path.abspath(args.out), width, height, FPS, zoom)


if __name__ == "__main__":
    main()
