from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import textwrap

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "assets"
OUT = BASE / "campaign-assets"
OUT.mkdir(exist_ok=True)

LOGO = ASSETS / "ikaruga-logo-horizontal.png"

W, H = 1080, 1350
SW, SH = 1080, 1920

RED = "#C90012"
RED_DARK = "#8F000B"
INK = "#171719"
CREAM = "#FFF7EA"
PAPER = "#FFFDF7"
GOLD = "#B7832F"
MUTED = "#595E68"

FONT_DIR = Path("C:/Windows/Fonts")
FONT_BOLD = FONT_DIR / "arialbd.ttf"
FONT_REG = FONT_DIR / "arial.ttf"
FONT_BLACK = FONT_DIR / "impact.ttf"
FONT_ITALIC = FONT_DIR / "ariali.ttf"


def font(size, weight="regular"):
    path = FONT_REG
    if weight == "bold":
        path = FONT_BOLD
    if weight == "black":
        path = FONT_BLACK if FONT_BLACK.exists() else FONT_BOLD
    if weight == "italic":
        path = FONT_ITALIC if FONT_ITALIC.exists() else FONT_REG
    return ImageFont.truetype(str(path), size)


def text_size(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap(draw, text, fnt, width):
    words = text.split()
    lines = []
    cur = ""
    for word in words:
        test = f"{cur} {word}".strip()
        if text_size(draw, test, fnt)[0] <= width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, xy, text, fnt, fill, width, line_gap=10, center=False):
    x, y = xy
    for line in wrap(draw, text, fnt, width):
        tw, th = text_size(draw, line, fnt)
        lx = x + (width - tw) / 2 if center else x
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += th + line_gap
    return y


def gradient_bg(w, h, accent=RED, dark=False):
    img = Image.new("RGB", (w, h), INK if dark else CREAM)
    px = img.load()
    ar = int(accent[1:3], 16), int(accent[3:5], 16), int(accent[5:7], 16)
    base1 = (24, 24, 25) if dark else (255, 250, 242)
    base2 = (48, 28, 22) if dark else (247, 235, 218)
    for y in range(h):
        t = y / max(1, h - 1)
        for x in range(w):
            dx = (x - w * .85) / w
            dy = (y - h * .14) / h
            glow = max(0, 1 - math.sqrt(dx * dx + dy * dy) * 3.0)
            r = int(base1[0] * (1 - t) + base2[0] * t)
            g = int(base1[1] * (1 - t) + base2[1] * t)
            b = int(base1[2] * (1 - t) + base2[2] * t)
            r = int(r * (1 - glow * .22) + ar[0] * glow * .22)
            g = int(g * (1 - glow * .22) + ar[1] * glow * .22)
            b = int(b * (1 - glow * .22) + ar[2] * glow * .22)
            px[x, y] = (r, g, b)
    return img.convert("RGBA")


def add_logo(img, x=68, y=54, width=300):
    if not LOGO.exists():
        return
    logo = Image.open(LOGO).convert("RGBA")
    ratio = width / logo.width
    logo = logo.resize((width, int(logo.height * ratio)), Image.LANCZOS)
    img.alpha_composite(logo, (x, y))


def rounded(draw, box, fill, outline=None, width=2, radius=20):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def brush(draw, x, y, w, h, color):
    points = [(x, y + 18), (x + w * .10, y), (x + w * .90, y + 8), (x + w, y + 22),
              (x + w * .94, y + h - 6), (x + w * .16, y + h), (x, y + h - 14)]
    draw.polygon(points, fill=color)
    for i in range(9):
        yy = y + 10 + i * h / 10
        draw.line((x + 20, yy, x + w - 24, yy - 5), fill=(255, 255, 255, 38), width=3)


def footer(draw, w, h):
    badge_y = h - 150
    rounded(draw, (88, badge_y, w - 88, badge_y + 58), "#FFFFFF", outline="#E7D8C4", radius=14)
    badge = "CLASES EN VIVO  ·  ORIENTACIÓN POR NIVEL  ·  CERTIFICACIÓN ACADÉMICA"
    tw, _ = text_size(draw, badge, font(22, "bold"))
    draw.text(((w - tw) / 2, badge_y + 17), badge, font=font(22, "bold"), fill=GOLD)
    draw.line((90, h - 74, w - 90, h - 74), fill=GOLD, width=2)
    txt = "IKARUGA SERVICIOS · Rosario, Argentina"
    tw, _ = text_size(draw, txt, font(24, "regular"))
    draw.text(((w - tw) / 2, h - 56), txt, font=font(24), fill=INK)


def red_tag(draw, xy, text, fnt=None):
    x, y = xy
    fnt = fnt or font(28, "bold")
    tw, th = text_size(draw, text, fnt)
    rounded(draw, (x, y, x + tw + 44, y + th + 24), RED, radius=12)
    draw.text((x + 22, y + 11), text, font=fnt, fill="white")


def draw_flag(draw, x, y, code, scale=1.0):
    w, h = int(82 * scale), int(54 * scale)
    draw.rounded_rectangle((x - 6, y - 6, x + w + 6, y + h + 6), radius=10, fill="#FFFFFF", outline="#E7D8C4", width=2)
    if code == "jp":
        draw.rectangle((x, y, x + w, y + h), fill="#FFFFFF")
        draw.ellipse((x + w * .35, y + h * .18, x + w * .65, y + h * .82), fill="#BC002D")
    elif code == "kr":
        draw.rectangle((x, y, x + w, y + h), fill="#FFFFFF")
        draw.pieslice((x + w*.34, y + h*.20, x + w*.66, y + h*.80), 90, 270, fill="#CD2E3A")
        draw.pieslice((x + w*.34, y + h*.20, x + w*.66, y + h*.80), 270, 90, fill="#0047A0")
        draw.ellipse((x + w*.42, y + h*.20, x + w*.58, y + h*.50), fill="#0047A0")
        draw.ellipse((x + w*.42, y + h*.50, x + w*.58, y + h*.80), fill="#CD2E3A")
    elif code == "cn":
        draw.rectangle((x, y, x + w, y + h), fill="#DE2910")
        draw.polygon([(x+16,y+10),(x+20,y+23),(x+8,y+15),(x+24,y+15),(x+12,y+23)], fill="#FFDE00")
    elif code == "th":
        bands = [("#A51931", 1), ("#FFFFFF", 1), ("#2D2A4A", 2), ("#FFFFFF", 1), ("#A51931", 1)]
        yy = y
        unit = h / 6
        for color, mult in bands:
            draw.rectangle((x, yy, x + w, yy + unit * mult), fill=color)
            yy += unit * mult
    elif code == "de":
        draw.rectangle((x, y, x + w, y + h/3), fill="#000000")
        draw.rectangle((x, y + h/3, x + w, y + 2*h/3), fill="#DD0000")
        draw.rectangle((x, y + 2*h/3, x + w, y + h), fill="#FFCE00")
    elif code == "it":
        draw.rectangle((x, y, x + w/3, y + h), fill="#009246")
        draw.rectangle((x + w/3, y, x + 2*w/3, y + h), fill="#FFFFFF")
        draw.rectangle((x + 2*w/3, y, x + w, y + h), fill="#CE2B37")
    elif code == "us":
        stripe = h / 13
        for i in range(13):
            draw.rectangle((x, y + i*stripe, x + w, y + (i+1)*stripe), fill="#B22234" if i % 2 == 0 else "#FFFFFF")
        draw.rectangle((x, y, x + w*.42, y + stripe*7), fill="#3C3B6E")
    draw.rounded_rectangle((x, y, x + w, y + h), radius=6, outline="#D9C7AA", width=1)


def seal(draw, cx, cy, label):
    draw.ellipse((cx - 88, cy - 88, cx + 88, cy + 88), fill=RED, outline=GOLD, width=5)
    lines = label.split()
    y = cy - 24 * len(lines)
    for line in lines:
        tw, th = text_size(draw, line, font(26, "bold"))
        draw.text((cx - tw / 2, y), line, font=font(26, "bold"), fill="white")
        y += 34


def base_slide(title, subtitle, eyebrow, filename, dark=False, accent=RED):
    img = gradient_bg(W, H, accent=accent, dark=dark)
    d = ImageDraw.Draw(img)
    add_logo(img, width=320)
    d.text((72, 210), eyebrow.upper(), font=font(28, "bold"), fill=RED if not dark else GOLD)
    y = draw_wrapped(d, (72, 265), title, font(78, "black"), "white" if dark else INK, 900, line_gap=8)
    y = draw_wrapped(d, (76, y + 20), subtitle, font(34, "regular"), "#F7EFE3" if dark else MUTED, 850, line_gap=10)
    footer(d, W, H)
    return img


def save(img, name):
    path = OUT / name
    img.convert("RGB").save(path, quality=95)
    return path


countries = [
    {
        "slug": "japon",
        "name": "Japón",
        "lang": "Japonés",
        "accent": "#C90012",
        "word": "仮装 · Kasou",
        "meaning": "Disfraz / caracterización",
        "focus": "En Japón, Halloween se vive como una experiencia visual y urbana: disfraces, cosplay, fotos y eventos temáticos.",
        "curious": "Shibuya se hizo famosa por sus reuniones de Halloween, aunque en los últimos años se comunica con más control para cuidar el orden público.",
        "cta": "Escribinos JAPÓN y conocé cómo empezar.",
    },
    {
        "slug": "corea",
        "name": "Corea",
        "lang": "Coreano",
        "accent": "#D71920",
        "word": "분장 · Bun-jang",
        "meaning": "Maquillaje o caracterización",
        "focus": "En Corea, Halloween aparece como celebración moderna: cafés temáticos, moda, cultura pop y eventos urbanos.",
        "curious": "No es una tradición antigua coreana; por eso conviene contarlo como fenómeno cultural actual, con tono respetuoso.",
        "cta": "Escribinos COREANO y te orientamos.",
    },
    {
        "slug": "tailandia",
        "name": "Tailandia",
        "lang": "Tailandés",
        "accent": "#A10022",
        "word": "ผี · Phi",
        "meaning": "Espíritu / fantasma",
        "focus": "En Tailandia, Halloween se mezcla con turismo, centros comerciales y una cultura popular llena de relatos de espíritus.",
        "curious": "Las historias de espíritus tienen mucha presencia en películas, leyendas y relatos cotidianos tailandeses.",
        "cta": "Escribinos TAILANDÉS y descubrí un idioma distinto.",
    },
    {
        "slug": "alemania",
        "name": "Alemania",
        "lang": "Alemán",
        "accent": "#111111",
        "word": "Geheimnis",
        "meaning": "Misterio / secreto",
        "focus": "Alemania permite una estética de otoño, bosques, castillos, cuentos y misterio elegante.",
        "curious": "Octubre combina muy bien con ferias, cosecha, calabazas y paisajes otoñales.",
        "cta": "Escribinos ALEMÁN y organizá tu próximo nivel.",
    },
    {
        "slug": "china",
        "name": "China",
        "lang": "Chino",
        "accent": "#B00012",
        "word": "鬼 · Gui",
        "meaning": "Fantasma / espíritu",
        "focus": "En China, Halloween aparece sobre todo en grandes ciudades, escuelas de idiomas y espacios internacionales.",
        "curious": "China tiene tradiciones propias vinculadas a ancestros y mundo espiritual, pero no son lo mismo que Halloween.",
        "cta": "Escribinos CHINO y conocé los recorridos.",
    },
    {
        "slug": "italia",
        "name": "Italia",
        "lang": "Italiano",
        "accent": "#8E1B16",
        "word": "Mistero",
        "meaning": "Misterio",
        "focus": "En Italia, Halloween moderno convive con Todos los Santos, Día de los Difuntos, historia y memoria familiar.",
        "curious": "El 1 y 2 de noviembre tienen una fuerte carga cultural y religiosa en muchas regiones italianas.",
        "cta": "Escribinos ITALIANO y empezá a estudiar cultura viva.",
    },
    {
        "slug": "ingles",
        "name": "Estados Unidos",
        "lang": "Inglés",
        "accent": "#0E3368",
        "word": "Trick or treat",
        "meaning": "La frase clásica de Halloween",
        "focus": "En Estados Unidos, Halloween se vive en comunidad: casas decoradas, dulces, disfraces, películas y barrios preparados.",
        "curious": "Es una de las fechas más visibles de la cultura popular estadounidense y aparece todo el tiempo en series y películas.",
        "cta": "Escribinos INGLÉS y elegí tu próximo comienzo.",
    },
]


def draw_pattern(d, accent):
    for i in range(0, W, 120):
        d.line((i, 0, i - 380, H), fill=(183, 131, 47, 28), width=2)
    d.ellipse((W - 240, 90, W + 110, 440), outline=accent, width=18)
    d.ellipse((-140, H - 230, 230, H + 130), outline=RED, width=16)


def carousel_slide(country, idx):
    accent = country["accent"]
    img = gradient_bg(W, H, accent=accent, dark=False)
    d = ImageDraw.Draw(img)
    draw_pattern(d, accent)
    add_logo(img, width=300)
    red_tag(d, (72, 190), f"IKARUGA MISTERIOS DEL MUNDO")
    d.text((72, 260), f"{idx}/5", font=font(28, "bold"), fill=GOLD)
    if idx == 1:
        d.text((72, 320), f"Halloween en", font=font(58, "bold"), fill=INK)
        d.text((72, 382), country["name"], font=font(112, "black"), fill=RED)
        seal(d, 805, 410, country["lang"].upper())
        draw_wrapped(d, (72, 565), "Una mirada cultural para descubrir cómo una fecha global cambia según el país.", font(38), MUTED, 850)
    elif idx == 2:
        d.text((72, 320), "Cómo se vive", font=font(82, "black"), fill=INK)
        rounded(d, (72, 455, 1008, 800), "#FFFFFF", outline="#E7D8C4", radius=18)
        draw_wrapped(d, (112, 505), country["focus"], font(44, "bold"), INK, 840, line_gap=13)
    elif idx == 3:
        d.text((72, 320), "Dato curioso", font=font(82, "black"), fill=INK)
        brush(d, 72, 440, 710, 90, RED)
        d.text((112, 455), "para guardar", font=font(48, "black"), fill="white")
        draw_wrapped(d, (72, 585), country["curious"], font(42, "regular"), INK, 880, line_gap=14)
    elif idx == 4:
        d.text((72, 320), "Una palabra", font=font(78, "black"), fill=INK)
        rounded(d, (72, 455, 1008, 735), INK, outline=GOLD, radius=18)
        tw, _ = text_size(d, country["word"], font(68, "bold"))
        d.text(((W - tw) / 2, 525), country["word"], font=font(68, "bold"), fill="white")
        tw, _ = text_size(d, country["meaning"], font(38))
        d.text(((W - tw) / 2, 620), country["meaning"], font=font(38), fill="#F7EFE3")
        draw_wrapped(d, (72, 820), "Aprender un idioma también es aprender cómo nombra el mundo otra cultura.", font(38), MUTED, 880)
    elif idx == 5:
        d.text((72, 305), "¿Te gustaría", font=font(68, "black"), fill=INK)
        d.text((72, 375), f"aprender {country['lang']}?", font=font(72, "black"), fill=RED)
        rounded(d, (72, 535, 1008, 735), "#FFFFFF", outline="#E7D8C4", radius=18)
        draw_wrapped(d, (112, 580), country["cta"], font(46, "bold"), INK, 840, line_gap=14)
        brush(d, 72, 835, 650, 92, RED)
        d.text((112, 852), "Respondé por mensaje", font=font(46, "black"), fill="white")
    footer(d, W, H)
    return img


def launch_post():
    img = gradient_bg(W, H, accent=RED, dark=False)
    d = ImageDraw.Draw(img)
    draw_pattern(d, RED)
    add_logo(img, width=330)
    # Premium top marker, public-facing: no internal "campaña" wording.
    d.text((72, 205), "OCTUBRE EN IKARUGA", font=font(30, "bold"), fill=RED)
    d.text((72, 260), "Misterios", font=font(100, "black"), fill=INK)
    d.text((72, 355), "del Mundo", font=font(100, "black"), fill=RED)
    draw_wrapped(
        d,
        (76, 490),
        "Un viaje cultural por Halloween, los idiomas y las formas en que cada país cuenta sus propias historias.",
        font(38, "regular"),
        MUTED,
        860,
        line_gap=12,
    )
    # Elegant passport panel.
    rounded(d, (72, 660, 1008, 1072), "#FFFFFF", outline="#E7D8C4", radius=22)
    d.text((112, 705), "IDIOMAS PARA DESCUBRIR", font=font(30, "bold"), fill=GOLD)
    items = [
        ("jp", "Japonés"), ("kr", "Coreano"), ("cn", "Chino"), ("th", "Tailandés"),
        ("de", "Alemán"), ("it", "Italiano"), ("us", "Inglés")
    ]
    for idx, (code, label) in enumerate(items):
        col = idx % 2
        row = idx // 2
        x = 112 + col * 430
        y = 765 + row * 75
        draw_flag(d, x, y, code, scale=.62)
        d.text((x + 72, y + 8), label, font=font(34, "bold"), fill=INK)
    # Quality seal integrated in the public image.
    rounded(d, (72, 1110, 1008, 1192), RED, radius=16)
    d.text((112, 1122), "Cultura, idioma y oportunidades", font=font(35, "black"), fill="white")
    d.text((112, 1164), "Un octubre para descubrir el mundo desde una nueva lengua.", font=font(24, "bold"), fill="#FFF7EA")
    footer(d, W, H)
    save(img, "00-lanzamiento-campania.png")


def story_ruleta():
    img = gradient_bg(SW, SH, accent=RED, dark=True)
    d = ImageDraw.Draw(img)
    add_logo(img, x=70, y=70, width=350)
    d.text((70, 260), "HISTORIA · JUEGO", font=font(30, "bold"), fill=GOLD)
    draw_wrapped(d, (70, 335), "Ruleta Misterios del Mundo", font(82, "black"), "white", 880, line_gap=6)
    cx, cy, r = SW // 2, 900, 330
    colors = [RED, INK, GOLD, "#FFF7EA", RED_DARK, "#2B2B2B", "#D6A94D", "#FFFFFF"]
    labels = ["15%", "20%", "25%", "30%", "BONUS", "SORPRESA", "CLASE", "OTRA"]
    for i in range(8):
        start = i * 45 - 90
        end = start + 45
        d.pieslice((cx-r, cy-r, cx+r, cy+r), start, end, fill=colors[i], outline="#FFF7EA", width=4)
    d.ellipse((cx-105, cy-105, cx+105, cy+105), fill=INK, outline="#FFF7EA", width=8)
    d.text((cx-43, cy-42), "IK", font=font(70, "black"), fill="white")
    d.polygon([(cx, cy-r-48), (cx-34, cy-r-2), (cx+34, cy-r-2)], fill=GOLD)
    d.text((90, 1310), "Girás, capturás y desbloqueás", font=font(54, "black"), fill="white")
    draw_wrapped(d, (90, 1395), "Mandanos tu captura por mensaje privado y aplicamos el beneficio a cursos grupales disponibles.", font(38), "#F7EFE3", 880)
    rounded(d, (90, 1645, 990, 1745), RED, radius=18)
    d.text((148, 1670), "Beneficio válido por 24 horas", font=font(42, "bold"), fill="white")
    save(img, "story-ruleta-misterios-del-mundo.png")


def story_puertas():
    img = gradient_bg(SW, SH, accent=RED, dark=False)
    d = ImageDraw.Draw(img)
    add_logo(img, x=70, y=70, width=350)
    d.text((70, 270), "HISTORIA · INTERACCIÓN", font=font(30, "bold"), fill=RED)
    draw_wrapped(d, (70, 350), "Elegí una puerta cultural", font(82, "black"), INK, 890)
    labels = [("A", "Asia"), ("B", "Europa"), ("C", "Inglés global")]
    x0 = 90
    for i, (letter, label) in enumerate(labels):
        x = x0 + i * 320
        rounded(d, (x, 620, x + 260, 1120), RED if i == 0 else INK if i == 1 else GOLD, radius=22)
        d.text((x + 86, 735), letter, font=font(120, "black"), fill="white")
        tw, _ = text_size(d, label, font(36, "bold"))
        d.text((x + (260 - tw)/2, 960), label, font=font(36, "bold"), fill="white")
    draw_wrapped(d, (90, 1260), "Respondé A, B o C y te mandamos una recomendación de idioma para empezar.", font(44, "bold"), INK, 900, line_gap=14, center=True)
    footer(d, SW, SH)
    save(img, "story-elegi-una-puerta-cultural.png")


def story_pasaporte():
    img = gradient_bg(SW, SH, accent=GOLD, dark=True)
    d = ImageDraw.Draw(img)
    add_logo(img, x=70, y=70, width=350)
    d.text((70, 270), "HISTORIA · PASAPORTE", font=font(30, "bold"), fill=GOLD)
    draw_wrapped(d, (70, 350), "Elegí tu sello IKARUGA", font(82, "black"), "white", 880)
    countries_labels = ["Japón", "Corea", "China", "Tailandia", "Alemania", "Italia", "Inglés"]
    positions = [(220, 680), (540, 680), (860, 680), (220, 1000), (540, 1000), (860, 1000), (540, 1320)]
    for label, pos in zip(countries_labels, positions):
        seal(d, pos[0], pos[1], label.upper())
    draw_wrapped(d, (110, 1540), "Cada sello revela un idioma y una oportunidad para empezar.", font(42, "bold"), "#F7EFE3", 860, center=True)
    save(img, "story-pasaporte-cultural-ikaruga.png")


def all_assets():
    launch_post()
    for c in countries:
        for i in range(1, 6):
            save(carousel_slide(c, i), f"carrusel-{c['slug']}-{i:02d}.png")
    story_ruleta()
    story_puertas()
    story_pasaporte()


if __name__ == "__main__":
    all_assets()
    print(f"Assets generated in {OUT}")
