import math
import shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "campaign-assets"
LOGO = ROOT / "assets" / "ikaruga-logo-horizontal.png"
W, H = 1080, 1920

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_SERIF = r"C:\Windows\Fonts\georgiab.ttf"

RED = (207, 0, 18)
DARK = (17, 12, 12)
CHARCOAL = (27, 27, 29)
CREAM = (255, 248, 236)
GOLD = (196, 142, 50)
WHITE = (255, 255, 255)

OPTIONS = ["15% OFF", "20% OFF", "25% OFF", "30% OFF", "BONUS", "SEGUÍ"]
COLORS = [RED, CHARCOAL, GOLD, CREAM, (155, 0, 12), (245, 239, 225)]


def font(path, size):
    return ImageFont.truetype(path, size)


def center_text(draw, xy, text, fnt, fill):
    x, y = xy
    box = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - (box[2] - box[0]) / 2, y - (box[3] - box[1]) / 2), text, font=fnt, fill=fill)


def logo(canvas):
    im = Image.open(LOGO).convert("RGBA")
    im.thumbnail((440, 150), Image.Resampling.LANCZOS)
    x = (W - im.width) // 2
    bg = Image.new("RGBA", (im.width + 48, im.height + 36), (255, 255, 255, 232))
    ImageDraw.Draw(bg).rounded_rectangle((0, 0, bg.width, bg.height), 20, fill=(255, 255, 255, 232))
    canvas.alpha_composite(bg, (x - 24, 70))
    canvas.alpha_composite(im, (x, 88))


def wheel_image(size=850):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    bbox = (20, 20, size - 20, size - 20)
    n = len(OPTIONS)
    for i, opt in enumerate(OPTIONS):
        start = -90 + i * 360 / n
        end = -90 + (i + 1) * 360 / n
        d.pieslice(bbox, start, end, fill=COLORS[i])
        d.arc(bbox, start, end, fill=CREAM, width=4)
        angle = math.radians((start + end) / 2)
        tx = size / 2 + math.cos(angle) * size * 0.29
        ty = size / 2 + math.sin(angle) * size * 0.29
        text_layer = Image.new("RGBA", (250, 80), (0, 0, 0, 0))
        td = ImageDraw.Draw(text_layer)
        f = font(FONT_BOLD, 34 if len(opt) <= 7 else 30)
        fill = DARK if COLORS[i] in [CREAM, (245, 239, 225)] else WHITE
        center_text(td, (125, 40), opt, f, fill)
        text_layer = text_layer.rotate((start + end) / 2 + 90, expand=True, resample=Image.Resampling.BICUBIC)
        im.alpha_composite(text_layer, (int(tx - text_layer.width / 2), int(ty - text_layer.height / 2)))
    d.ellipse((size * .38, size * .38, size * .62, size * .62), fill=DARK, outline=CREAM, width=6)
    center_text(d, (size / 2, size / 2), "IK", font(FONT_BOLD, 66), WHITE)
    d.ellipse(bbox, outline=CREAM, width=7)
    return im


BASE_WHEEL = wheel_image()


def draw_static(result, angle):
    canvas = Image.new("RGBA", (W, H), (22, 9, 9, 255))
    d = ImageDraw.Draw(canvas)
    for y in range(H):
        a = y / H
        col = (int(18 + 55 * a), int(9 + 10 * a), int(9 + 6 * a), 255)
        d.line((0, y, W, y), fill=col)
    d.ellipse((735, 70, 1180, 500), outline=(200, 0, 18, 170), width=10)
    d.ellipse((-130, 1250, 260, 1650), outline=(196, 142, 50, 90), width=6)
    logo(canvas)
    center_text(d, (W / 2, 250), "MISTERIOS DEL MUNDO", font(FONT_BOLD, 34), RED)
    center_text(d, (W / 2, 345), "Ruleta Halloween", font(FONT_SERIF, 72), CREAM)
    center_text(d, (W / 2, 420), "Girás, capturás y desbloqueás tu beneficio", font(FONT_REG, 34), WHITE)
    wheel = BASE_WHEEL.rotate(angle, resample=Image.Resampling.BICUBIC)
    canvas.alpha_composite(wheel, ((W - wheel.width) // 2, 555))
    pointer = [(W // 2, 520), (W // 2 - 45, 600), (W // 2 + 45, 600)]
    d.polygon(pointer, fill=GOLD)
    d.rounded_rectangle((92, 1430, W - 92, 1535), 38, fill=RED)
    center_text(d, (W / 2, 1482), "Hacé captura y mandanos tu resultado", font(FONT_BOLD, 42), WHITE)
    d.rounded_rectangle((96, 1588, W - 96, 1715), 24, fill=(255, 248, 236, 245), outline=GOLD, width=3)
    center_text(d, (W / 2, 1635), f"Resultado ejemplo: {result}", font(FONT_BOLD, 38), DARK)
    center_text(d, (W / 2, 1684), "Válido 24 hs · cursos grupales disponibles", font(FONT_REG, 29), (60, 60, 60))
    center_text(d, (W / 2, 1845), "IKARUGA SERVICIOS · Rosario, Argentina", font(FONT_REG, 28), CREAM)
    return canvas.convert("P", palette=Image.Palette.ADAPTIVE)


def result_angle(result):
    idx = OPTIONS.index(result)
    seg = 360 / len(OPTIONS)
    center = -90 + idx * seg + seg / 2
    return center + 90


def make_gif(result, name):
    final = result_angle(result)
    frames = []
    # two slow rotations plus landing, enough for story capture without feeling frenetic
    for i in range(54):
        t = i / 53
        ease = 1 - (1 - t) ** 3
        angle = 720 * (1 - ease) + final * ease
        frames.append(draw_static(result, angle))
    path = OUT / name
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=95, loop=0, optimize=True)
    return path


def main():
    OUT.mkdir(exist_ok=True)
    targets = {
        "15% OFF": "ruleta-halloween-15-off.gif",
        "20% OFF": "ruleta-halloween-20-off.gif",
        "25% OFF": "ruleta-halloween-25-off.gif",
        "30% OFF": "ruleta-halloween-30-off.gif",
        "SEGUÍ": "ruleta-halloween-segui-participando.gif",
    }
    for result, name in targets.items():
        print(make_gif(result, name))
    # keep the main file as the strongest commercial outcome without deleting the variant.
    shutil.copyfile(OUT / "ruleta-halloween-25-off.gif", OUT / "ruleta-halloween-ikaruga.gif")


if __name__ == "__main__":
    main()
