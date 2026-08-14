"""Draws the AFKing tray/app icon (a little coffee mug).

Green mug = active (you're being kept "online"), gray = paused.
Used both at runtime by the tray app and at build time to generate the
.ico embedded in the exe.
"""

from PIL import Image, ImageDraw

GREEN = (46, 204, 113, 255)
GRAY = (149, 165, 166, 255)
WHITE = (255, 255, 255, 255)


def make_image(active=True, size=64):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = size

    # Background disc, colour-coded by state.
    d.ellipse([2, 2, s - 2, s - 2], fill=GREEN if active else GRAY)

    # Mug body.
    d.rounded_rectangle(
        [s * 0.30, s * 0.34, s * 0.60, s * 0.70],
        radius=s * 0.05,
        fill=WHITE,
    )
    # Handle.
    d.ellipse(
        [s * 0.58, s * 0.40, s * 0.76, s * 0.60],
        outline=WHITE,
        width=max(2, int(s * 0.05)),
    )
    # Two little wisps of steam.
    steam_w = max(2, int(s * 0.045))
    d.line([s * 0.39, s * 0.18, s * 0.39, s * 0.28], fill=WHITE, width=steam_w)
    d.line([s * 0.50, s * 0.18, s * 0.50, s * 0.28], fill=WHITE, width=steam_w)

    return img
