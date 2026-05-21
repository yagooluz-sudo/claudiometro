"""Generates claudinho.ico — renders at 256 px then nearest-neighbour scales down."""
import json
from pathlib import Path
from PIL import Image, ImageDraw

SCRIPT_DIR = Path(__file__).parent
ANIM_DIR   = SCRIPT_DIR.parent / "tools" / "claudepix_data"
OUT        = SCRIPT_DIR / "claudinho.ico"

data    = json.loads((ANIM_DIR / "work_coding.json").read_text())
palette = data["palette"]
grid    = data["frames"][0]["grid"]

BASE = 256   # render everything at this size, scale down from here
CELL = 11    # 20 × 11 = 220 px of art inside a 256 px canvas

def render_base() -> Image.Image:
    img = Image.new("RGBA", (BASE, BASE), (0, 0, 0, 0))
    d   = ImageDraw.Draw(img)

    # Rounded dark background
    r = BASE // 7
    d.rounded_rectangle([0, 0, BASE - 1, BASE - 1], radius=r, fill="#1a1a1a")
    d.rounded_rectangle([0, 0, BASE - 1, BASE - 1], radius=r,
                        outline="#d97757", width=4)

    # Centre the 220×220 art
    pad = (BASE - 20 * CELL) // 2
    for y, row in enumerate(grid):
        for x, idx in enumerate(row):
            color = palette[idx]
            if color == "transparent":
                continue
            x0 = pad + x * CELL
            y0 = pad + y * CELL
            d.rectangle([x0, y0, x0 + CELL - 1, y0 + CELL - 1], fill=color)

    return img

base = render_base()

sizes  = [256, 128, 64, 48, 32, 16]
frames = [base.resize((s, s), Image.NEAREST) for s in sizes]

frames[0].save(OUT, format="ICO", sizes=[(s, s) for s in sizes],
               append_images=frames[1:])
print(f"Salvo: {OUT}")
