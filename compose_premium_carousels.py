from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "campaign-assets"
LOGO = ROOT / "assets" / "ikaruga-logo-horizontal.png"
GEN = Path(r"C:\Users\Usuario\.codex\generated_images\019ecc1a-02f2-7a81-be35-b373f4e250aa")

W, H = 1080, 1350
RED = (191, 0, 16)
DARK = (18, 18, 18)
INK = (12, 22, 34)
CREAM = (252, 245, 234)
GOLD = (190, 136, 48)

FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"
FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_SERIF_BOLD = r"C:\Windows\Fonts\georgiab.ttf"
FONT_UNICODE = r"C:\Windows\Fonts\ARIALUNI.TTF"
FONT_NIRMALA_BOLD = r"C:\Windows\Fonts\NirmalaB.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def cover_crop(img, size=(W, H), anchor=(0.5, 0.5), zoom=1.0):
    iw, ih = img.size
    tw, th = size
    scale = max(tw / iw, th / ih) * zoom
    nw, nh = int(iw * scale), int(ih * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    max_x = max(0, nw - tw)
    max_y = max(0, nh - th)
    x = int(max_x * anchor[0])
    y = int(max_y * anchor[1])
    return img.crop((x, y, x + tw, y + th))


def round_rect(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, line = [], ""
    for word in words:
        test = f"{line} {word}".strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_w:
            line = test
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def draw_text_block(draw, x, y, text, fnt, fill, max_w, leading=10):
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += draw.textbbox((0, 0), line, font=fnt)[3] + leading
    return y


def fit_text(draw, text, font_path, max_size, min_size, max_w):
    for size in range(max_size, min_size - 1, -2):
        f = font(font_path, size)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_w:
            return f
    return font(font_path, min_size)


def logo_on(canvas, x=64, y=54, w=310):
    logo = Image.open(LOGO).convert("RGBA")
    ratio = w / logo.width
    logo = logo.resize((w, int(logo.height * ratio)), Image.Resampling.LANCZOS)
    pad = 16
    shadow = Image.new("RGBA", (logo.width + pad * 2, logo.height + pad * 2), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((0, 0, shadow.width, shadow.height), 14, fill=(255, 255, 255, 225))
    canvas.alpha_composite(shadow, (x - pad, y - pad))
    canvas.alpha_composite(logo, (x, y))


def top_gradient(base, strength=150):
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    px = ov.load()
    for yy in range(H):
        a = int(max(0, strength * (1 - yy / 760)))
        for xx in range(W):
            px[xx, yy] = (0, 0, 0, a)
    return Image.alpha_composite(base, ov)


def bottom_gradient(base, strength=170):
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    px = ov.load()
    for yy in range(H):
        a = int(max(0, strength * ((yy - 650) / 700)))
        for xx in range(W):
            px[xx, yy] = (0, 0, 0, a)
    return Image.alpha_composite(base, ov)


def make_bg(path, anchor=(0.5, 0.5), zoom=1.0, blur=0):
    img = Image.open(path).convert("RGB")
    img = cover_crop(img, anchor=anchor, zoom=zoom).convert("RGBA")
    if blur:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    img = top_gradient(bottom_gradient(img))
    return img


def draw_quality(draw):
    y = H - 72
    draw.rounded_rectangle((70, y, W - 70, y + 42), 20, fill=(255, 255, 255, 235), outline=(222, 185, 101), width=2)
    txt = "CLASES EN VIVO  ·  ORIENTACIÓN POR NIVEL  ·  CERTIFICACIÓN ACADÉMICA"
    f = fit_text(draw, txt, FONT_BOLD, 26, 18, W - 180)
    tw = draw.textbbox((0, 0), txt, font=f)[2]
    draw.text(((W - tw) / 2, y + 10), txt, font=f, fill=(151, 89, 20))
    foot = "IKARUGA SERVICIOS · Rosario, Argentina"
    ff = font(FONT_REG, 22)
    tw = draw.textbbox((0, 0), foot, font=ff)[2]
    draw.text(((W - tw) / 2, H - 27), foot, font=ff, fill=(255, 255, 255, 225))


def stamp(draw, text, x, y, fill=RED):
    f = font(FONT_BOLD, 32)
    tw = draw.textbbox((0, 0), text, font=f)[2]
    draw.rounded_rectangle((x, y, x + tw + 34, y + 50), 16, fill=fill)
    draw.text((x + 17, y + 9), text, font=f, fill=(255, 255, 255))


def text_panel(canvas, y, title, body, kicker=None, mode="cream"):
    draw = ImageDraw.Draw(canvas)
    fill = (255, 250, 242, 232) if mode == "cream" else (12, 18, 24, 224)
    txt = INK if mode == "cream" else (255, 255, 255)
    x0, x1 = 72, W - 72
    round_rect(draw, (x0, y, x1, y + 390), 26, fill, outline=(221, 184, 102, 210), width=2)
    if kicker:
        stamp(draw, kicker, x0 + 36, y + 34, fill=GOLD if mode == "cream" else RED)
        ty = y + 100
    else:
        ty = y + 44
    tf = fit_text(draw, title, FONT_SERIF_BOLD, 76, 50, x1 - x0 - 72)
    draw_text_block(draw, x0 + 36, ty, title, tf, RED if mode == "cream" else (255, 235, 180), x1 - x0 - 72, 4)
    by = ty + 150
    bf = font(FONT_REG, 35)
    draw_text_block(draw, x0 + 40, by, body, bf, txt, x1 - x0 - 80, 11)


def cover(slug, cfg, base):
    im = make_bg(base, anchor=cfg["anchors"][0], zoom=1.0)
    draw = ImageDraw.Draw(im)
    logo_on(im)
    stamp(draw, cfg["label_top"], 64, 210)
    big1 = f"HALLOWEEN EN"
    big2 = cfg["country"].upper()
    f1 = font(FONT_BOLD, 76)
    f2 = fit_text(draw, big2, FONT_SERIF_BOLD, 114, 72, W - 120)
    draw.text((64, 285), big1, font=f1, fill=(255, 255, 255))
    draw.text((64, 365), big2, font=f2, fill=(255, 224, 170))
    draw.rounded_rectangle((64, 520, W - 120, 665), 22, fill=(255, 255, 255, 222))
    draw_text_block(draw, 95, 548, cfg["cover_body"], font(FONT_BOLD, 38), INK, W - 200, 8)
    draw_quality(draw)
    im.convert("RGB").save(OUT / f"carrusel-{slug}-01.png", quality=95)


def how(slug, cfg, base):
    im = make_bg(base, anchor=cfg["anchors"][1], zoom=1.12, blur=1)
    draw = ImageDraw.Draw(im)
    logo_on(im, 64, 50, 270)
    text_panel(im, 705, "Cómo se vive", cfg["how"], kicker=f"{cfg['flag']} CULTURA")
    draw_quality(draw)
    im.convert("RGB").save(OUT / f"carrusel-{slug}-02.png", quality=95)


def fact(slug, cfg, base):
    im = make_bg(base, anchor=cfg["anchors"][2], zoom=1.22)
    draw = ImageDraw.Draw(im)
    logo_on(im, 64, 50, 270)
    draw.rounded_rectangle((70, 650, W - 70, 1090), 28, fill=(15, 15, 15, 226), outline=(202, 151, 67), width=2)
    stamp(draw, "DATO CURIOSO", 108, 690, fill=RED)
    draw_text_block(draw, 108, 775, cfg["fact"], font(FONT_BOLD, 46), (255, 255, 255), W - 210, 14)
    draw.line((108, 1020, W - 160, 1020), fill=GOLD, width=4)
    draw_quality(draw)
    im.convert("RGB").save(OUT / f"carrusel-{slug}-03.png", quality=95)


def word(slug, cfg, base):
    im = make_bg(base, anchor=cfg["anchors"][3], zoom=1.18)
    draw = ImageDraw.Draw(im)
    logo_on(im, 64, 50, 270)
    draw.rounded_rectangle((96, 500, W - 96, 980), 34, fill=(255, 249, 238, 238), outline=(200, 148, 62), width=3)
    stamp(draw, "PALABRA DEL IDIOMA", 142, 545, fill=GOLD)
    word_font = cfg.get("word_font") or (FONT_UNICODE if cfg.get("unicode_word") else FONT_BOLD)
    wf = fit_text(draw, cfg["word"], word_font, 96, 66, W - 250)
    tw = draw.textbbox((0, 0), cfg["word"], font=wf)[2]
    draw.text(((W - tw) / 2, 645), cfg["word"], font=wf, fill=RED)
    mf = font(FONT_SERIF_BOLD, 54)
    tw = draw.textbbox((0, 0), cfg["meaning"], font=mf)[2]
    draw.text(((W - tw) / 2, 775), cfg["meaning"], font=mf, fill=INK)
    draw_text_block(draw, 150, 875, cfg["word_note"], font(FONT_REG, 30), (44, 44, 44), W - 300, 8)
    draw_quality(draw)
    im.convert("RGB").save(OUT / f"carrusel-{slug}-04.png", quality=95)


def cta(slug, cfg, base):
    im = make_bg(base, anchor=cfg["anchors"][4], zoom=1.08, blur=1)
    draw = ImageDraw.Draw(im)
    logo_on(im, 64, 50, 300)
    draw.rounded_rectangle((70, 560, W - 70, 1085), 34, fill=(255, 250, 242, 235), outline=(211, 164, 75), width=3)
    tf = fit_text(draw, f"¿Te gustaría aprender {cfg['course']}?", FONT_SERIF_BOLD, 72, 48, W - 180)
    draw_text_block(draw, 110, 615, f"¿Te gustaría aprender {cfg['course']}?", tf, INK, W - 190, 8)
    draw.line((110, 790, W - 120, 790), fill=RED, width=5)
    draw_text_block(draw, 110, 840, f"Escribinos {cfg['keyword']} y te contamos opciones, niveles y horarios disponibles.", font(FONT_BOLD, 43), (38, 38, 38), W - 190, 12)
    draw.rounded_rectangle((135, 1110, W - 135, 1195), 42, fill=RED)
    btn = "QUIERO INFO"
    bf = font(FONT_BOLD, 46)
    tw = draw.textbbox((0, 0), btn, font=bf)[2]
    draw.text(((W - tw) / 2, 1128), btn, font=bf, fill=(255, 255, 255))
    draw_quality(draw)
    im.convert("RGB").save(OUT / f"carrusel-{slug}-05.png", quality=95)


configs = {
    "china": {
        "base": "call_zNPqe8Vh5Y7BxEeotL0Zlk9j.png",
        "flag": "🇨🇳", "label_top": "CHINO", "country": "China", "course": "chino",
        "cover_body": "Ciudades grandes, escuelas de idiomas y una mirada internacional de octubre.",
        "how": "En China, Halloween aparece sobre todo en grandes ciudades, centros comerciales, escuelas de idiomas y espacios internacionales.",
        "fact": "China tiene tradiciones propias vinculadas a ancestros y mundo espiritual, pero no son lo mismo que Halloween.",
        "word": "鬼 · Gui", "meaning": "Fantasma / espíritu",
        "unicode_word": True,
        "word_note": "Una palabra simple para abrir una conversación cultural sin mezclar festividades.",
        "keyword": "CHINO",
        "anchors": [(0.60, .35), (.25, .45), (.82, .20), (.55, .82), (.72, .48)],
    },
    "tailandia": {
        "base": "call_LnJC7ydXP2hkBdWtzkGybFhz.png",
        "flag": "🇹🇭", "label_top": "TAILANDÉS", "country": "Tailandia", "course": "tailandés",
        "cover_body": "Relatos de espíritus, turismo y una forma distinta de vivir octubre.",
        "how": "En Tailandia, Halloween se mezcla con espacios turísticos, centros comerciales, escuelas internacionales y eventos temáticos.",
        "fact": "Las historias de espíritus tienen mucha presencia en películas, leyendas y relatos cotidianos tailandeses.",
        "word": "ผี · Phi", "meaning": "Espíritu / fantasma",
        "unicode_word": True,
        "word_font": FONT_NIRMALA_BOLD,
        "word_note": "Una palabra breve, cultural y muy útil para jugar con el misterio del mes.",
        "keyword": "TAILANDÉS",
        "anchors": [(0.50, .40), (.15, .55), (.82, .28), (.45, .78), (.74, .55)],
    },
    "alemania": {
        "base": "call_AA9eeSKghS9Wedo1o0HbAabc.png",
        "flag": "🇩🇪", "label_top": "ALEMÁN", "country": "Alemania", "course": "alemán",
        "cover_body": "Bosques, castillos, otoño y misterio con estética europea.",
        "how": "En Alemania, Halloween es una celebración moderna que convive con una temporada marcada por otoño, calabazas y paisajes históricos.",
        "fact": "Octubre combina muy bien con ferias, cosecha, calabazas y ambientación otoñal.",
        "word": "Geheimnis", "meaning": "Misterio / secreto",
        "word_note": "Una palabra potente para conectar idioma, cultura y una estética elegante de octubre.",
        "keyword": "ALEMÁN",
        "anchors": [(0.47, .35), (.20, .50), (.86, .25), (.50, .82), (.78, .52)],
    },
    "italia": {
        "base": "call_z371c1NyIsWbm5q01cqgzYCS.png",
        "flag": "🇮🇹", "label_top": "ITALIANO", "country": "Italia", "course": "italiano",
        "cover_body": "Historia, memoria, velas y una temporada llena de tradición.",
        "how": "En Italia, Halloween moderno convive con Todos los Santos y el Día de los Difuntos.",
        "fact": "El 1 y 2 de noviembre tienen una fuerte carga cultural y familiar en muchas regiones italianas.",
        "word": "Mistero", "meaning": "Misterio",
        "word_note": "Una puerta simple para hablar de historia, ciudades antiguas y tradiciones.",
        "keyword": "ITALIANO",
        "anchors": [(0.44, .36), (.22, .48), (.76, .26), (.52, .78), (.80, .50)],
    },
    "ingles": {
        "base": "call_Hhjt8BECXVsFJh54d8JkjlIi.png",
        "flag": "🇺🇸", "label_top": "INGLÉS", "country": "Estados Unidos", "course": "inglés",
        "cover_body": "Casas decoradas, películas, dulces y referencias culturales que aparecen en todo el mundo.",
        "how": "En Estados Unidos, Halloween se vive en barrios, escuelas, casas decoradas y cultura popular.",
        "fact": "Es una de las fechas más visibles en series, películas y redes; aprender inglés también abre referencias culturales.",
        "word": "Trick or treat", "meaning": "La frase clásica",
        "word_note": "La expresión más conocida de Halloween y una excusa perfecta para aprender cultura cotidiana.",
        "keyword": "INGLÉS",
        "anchors": [(0.45, .30), (.18, .50), (.82, .35), (.48, .80), (.78, .55)],
    },
}


def main():
    OUT.mkdir(exist_ok=True)
    for slug, cfg in configs.items():
        base = GEN / cfg["base"]
        cover(slug, cfg, base)
        how(slug, cfg, base)
        fact(slug, cfg, base)
        word(slug, cfg, base)
        cta(slug, cfg, base)
        print(f"ok {slug}")


if __name__ == "__main__":
    main()
