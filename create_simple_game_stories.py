from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "campaign-assets"
LOGO = ROOT / "assets" / "ikaruga-logo-horizontal.png"

W, H = 1080, 1920
RED = (207, 0, 18)
DARK = (18, 13, 13)
CHARCOAL = (28, 28, 30)
CREAM = (255, 248, 236)
GOLD = (196, 142, 50)

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_SERIF = r"C:\Windows\Fonts\georgiab.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def center(draw, y, text, fnt, fill, x=W // 2):
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - (box[2] - box[0]) / 2, y), text, font=fnt, fill=fill)


def wrap(draw, text, fnt, width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = f"{line} {word}".strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= width:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_wrapped(draw, xy, text, fnt, fill, width, gap=10):
    x, y = xy
    for line in wrap(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += draw.textbbox((0, 0), line, font=fnt)[3] + gap
    return y


def add_logo(canvas):
    logo = Image.open(LOGO).convert("RGBA")
    logo.thumbnail((390, 140), Image.Resampling.LANCZOS)
    bg = Image.new("RGBA", (logo.width + 44, logo.height + 32), (255, 255, 255, 236))
    ImageDraw.Draw(bg).rounded_rectangle((0, 0, bg.width, bg.height), 18, fill=(255, 255, 255, 236))
    x = (W - bg.width) // 2
    canvas.alpha_composite(bg, (x, 70))
    canvas.alpha_composite(logo, (x + 22, 86))


def base():
    im = Image.new("RGBA", (W, H), (28, 10, 10, 255))
    d = ImageDraw.Draw(im)
    for y in range(H):
        a = y / H
        d.line((0, y, W, y), fill=(int(26 + a * 35), int(10 + a * 12), int(10 + a * 8), 255))
    d.ellipse((720, 30, 1250, 520), outline=(207, 0, 18, 150), width=12)
    d.ellipse((-160, 1260, 300, 1760), outline=(196, 142, 50, 100), width=7)
    for x, y, r in [(90, 300, 6), (970, 780, 5), (140, 1080, 4), (900, 1450, 6)]:
        d.ellipse((x-r, y-r, x+r, y+r), fill=GOLD)
    add_logo(im)
    return im


def quality(draw):
    draw.rounded_rectangle((95, H - 155, W - 95, H - 98), 28, fill=(255, 248, 236, 240), outline=GOLD, width=2)
    center(draw, H - 141, "CLASES EN VIVO · ORIENTACIÓN POR NIVEL · CERTIFICACIÓN ACADÉMICA", font(FONT_BOLD, 24), (144, 91, 26))
    center(draw, H - 62, "IKARUGA SERVICIOS · Rosario, Argentina", font(FONT_REG, 28), CREAM)


def make_idioma_capture():
    im = base()
    d = ImageDraw.Draw(im)
    center(d, 245, "HISTORIA · JUEGO SIMPLE", font(FONT_BOLD, 28), RED)
    center(d, 330, "Capturá tu idioma", font(FONT_SERIF, 76), CREAM)
    center(d, 425, "Hacé screenshot y mandanos el resultado por DM", font(FONT_REG, 34), (255, 255, 255))

    labels = ["JAPONÉS", "COREANO", "CHINO", "TAILANDÉS", "ALEMÁN", "ITALIANO", "INGLÉS"]
    positions = [(120, 610), (390, 610), (660, 610), (255, 805), (525, 805), (120, 1000), (660, 1000)]
    for i, (label, pos) in enumerate(zip(labels, positions)):
        x, y = pos
        fill = RED if i % 2 == 0 else CHARCOAL
        d.rounded_rectangle((x, y, x + 300, y + 130), 30, fill=fill, outline=GOLD, width=3)
        center(d, y + 43, label, font(FONT_BOLD, 30), CREAM, x + 150)

    d.rounded_rectangle((95, 1235, W - 95, 1445), 28, fill=(255, 248, 236, 242), outline=GOLD, width=3)
    draw_wrapped(d, (135, 1268), "Si justo capturás el idioma que querés estudiar, mandanos la captura y activamos tu beneficio Halloween.", font(FONT_BOLD, 40), DARK, W - 270, 12)
    d.rounded_rectangle((120, 1510, W - 120, 1605), 45, fill=RED)
    center(d, 1531, "CAPTURÁ · ENVIÁ · ACTIVÁ", font(FONT_BOLD, 42), CREAM)
    quality(d)
    im.convert("RGB").save(OUT / "story-captura-tu-idioma.png", quality=95)


def make_reto_express():
    im = base()
    d = ImageDraw.Draw(im)
    center(d, 245, "HISTORIA · DESAFÍO", font(FONT_BOLD, 28), RED)
    center(d, 330, "Reto express", font(FONT_SERIF, 84), CREAM)
    center(d, 430, "Elegí un idioma y mandanos tu respuesta", font(FONT_REG, 36), (255, 255, 255))

    d.rounded_rectangle((100, 610, W - 100, 1080), 36, fill=(255, 248, 236, 242), outline=GOLD, width=3)
    center(d, 665, "¿Qué idioma querés empezar?", font(FONT_BOLD, 46), DARK)
    opts = [("A", "Asia"), ("B", "Europa"), ("C", "Inglés global")]
    for idx, (letter, label) in enumerate(opts):
        x = 155 + idx * 255
        y = 780
        d.rounded_rectangle((x, y, x + 215, y + 180), 28, fill=RED if idx != 1 else CHARCOAL)
        center(d, y + 32, letter, font(FONT_BOLD, 74), CREAM, x + 107)
        center(d, y + 120, label, font(FONT_BOLD, 26), CREAM, x + 107)

    d.rounded_rectangle((115, 1165, W - 115, 1395), 30, fill=(24, 24, 26, 235), outline=GOLD, width=3)
    draw_wrapped(d, (155, 1210), "Respondé A, B o C por DM. Sumá tu país y activamos tu beneficio Halloween.", font(FONT_BOLD, 39), CREAM, W - 310, 13)
    d.rounded_rectangle((120, 1510, W - 120, 1605), 45, fill=RED)
    center(d, 1531, "RESPONDÉ POR DM", font(FONT_BOLD, 44), CREAM)
    quality(d)
    im.convert("RGB").save(OUT / "story-reto-express-idioma.png", quality=95)


if __name__ == "__main__":
    make_idioma_capture()
    make_reto_express()
