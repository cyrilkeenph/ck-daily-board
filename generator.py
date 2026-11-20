from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

W, H = 1080, 2400
OUT = "."

F = "/usr/share/fonts/opentype/inter/"
ANTON = "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf"
def f(name, size): return ImageFont.truetype(F + name, size)
def anton(size): return ImageFont.truetype(ANTON, size)

import json, sys
SITE = sys.argv[1] if len(sys.argv) > 1 else "."
DATA = json.load(open(SITE + "/todos.json"))
DAYS = [(d["day"], d["subtitle"], d["accent"], d["focus"], d["am"]) for d in DATA["days"]]
OUT = SITE

def hexrgb(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def background(accent):
    a = hexrgb(accent)
    img = Image.new("RGB", (W, H), (12, 13, 18))
    # vertical gradient
    d = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        c = tuple(int(12 + (22 - 12) * t) for _ in range(3))
        d.line([(0, y), (W, y)], fill=(c[0], c[1], c[2] + 4))
    # soft accent glows
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse([-300, -250, 900, 700], fill=tuple(int(v * 0.55) for v in a))
    g.ellipse([500, 1700, 1500, 2700], fill=tuple(int(v * 0.30) for v in a))
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    img = Image.blend(img, Image.eval(Image.merge("RGB", [ch for ch in glow.split()]), lambda v: v), 0.0)
    from PIL import ImageChops
    img = ImageChops.add(img, glow)
    return img

def card(img, box, radius=36):
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    o = ImageDraw.Draw(overlay)
    o.rounded_rectangle(box, radius, fill=(255, 255, 255, 18), outline=(255, 255, 255, 38), width=2)
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB"))

def text_w(d, s, font): return d.textlength(s, font=font)

for idx, (day, sub, accent, focus, mid) in enumerate(DAYS, 1):
    A = hexrgb(accent)
    img = background(accent)
    d = ImageDraw.Draw(img)
    X = 80
    y = 780  # keep top area clear for the lock-screen clock

    # Day title
    d.text((X, y), day, font=anton(150), fill=A)
    y += 205
    d.text((X + 4, y), sub.upper(), font=f("Inter-SemiBold.otf", 38), fill=(235, 235, 240))
    y += 85

    # Focus card
    top = y
    rows = len(focus)
    step = 92 if rows <= 4 else max(60, int(368 / rows))
    card_h = 95 + rows * step + 20
    card(img, [X - 20, top, W - X + 20, top + card_h])
    d = ImageDraw.Draw(img)
    d.text((X + 20, top + 32), "TODAY'S FOCUS", font=f("Inter-Bold.otf", 28), fill=A)
    ry = top + 100
    for item in focus:
        d.rounded_rectangle([X + 20, ry + 4, X + 66, ry + 50], 10, outline=A, width=4)
        d.text((X + 92, ry + 4), item, font=f("Inter-Medium.otf", 39), fill=(245, 245, 248))
        ry += step
    y = top + card_h + 28

    # Daily flow card
    flow = [
        ("7 AM", "Wake up"),
        ("8 AM", "Gym / workout"),
        ("AM", mid),
        ("1 PM", "Paayo Café: quality & posting"),
        ("9 PM", "Head home"),
        ("10 PM", "Designs & proposals until 1 AM"),
    ]
    if day == "SUNDAY":
        flow[2] = ("AM", "Rest & recharge")
        flow[5] = ("10 PM", "Light planning, sleep early")
    top = y
    card_h = 90 + len(flow) * 56 + 14
    card(img, [X - 20, top, W - X + 20, top + card_h])
    d = ImageDraw.Draw(img)
    d.text((X + 20, top + 30), "DAILY FLOW", font=f("Inter-Bold.otf", 28), fill=A)
    ry = top + 92
    for t, label in flow:
        d.text((X + 20, ry), t, font=f("Inter-Bold.otf", 32), fill=A)
        d.text((X + 190, ry), label, font=f("Inter-Regular.otf", 33), fill=(220, 222, 230))
        ry += 56
    y = top + card_h + 28

    # Monthly bills banner
    bh = 96
    d.rounded_rectangle([X - 20, y, W - X + 20, y + bh], 30, fill=A)
    s = DATA["bills"]
    fnt = f("Inter-Bold.otf", 34)
    d.text(((W - text_w(d, s, fnt)) / 2, y + 28), s, font=fnt, fill=(16, 16, 20))

    img.save(f"{OUT}/{day.title()}.png", optimize=True)
    print("saved", day, "bottom at", y + bh)
