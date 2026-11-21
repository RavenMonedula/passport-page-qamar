"""The Passport Page of a Country That Isn't There — make.fun entry.

Draws a two-page passport spread for the Republic of Qamar, a desert
oasis republic: identity page (left) and visas page (right).
Deterministic, no network, PIL only. Writes /output/entry.png.
"""

import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- data

COUNTRY = "REPUBLIC OF QAMAR"
COUNTRY_NATIVE = "JUMHŪRIYAT QAMAR"
DOC_TYPE = "P"
DOC_CODE = "QMR"
DOC_NO = "QMR 002914"
SURNAME = "AMRANI"
GIVEN = "LAYLA NOOR"
NATIONALITY = "QAMARI"
DOB = "14 MAY 1983"
SEX = "F"
POB = "QAMAR CITY, OLD WELL"
ISSUED = "03 MAR 2024"
EXPIRY = "02 MAR 2034"
AUTHORITY = "PASSPORT OFFICE, QAMAR CITY"
PERSONAL = "140583-2914"
SIGNATURE = "Layla Amrani"
OBSERVATIONS = (
    "Holder is a licensed caravan guide, Qamar Caravan Guild No. 27. "
    "Crossing the Great Erg only with a licensed water-bearer; "
    "see endorsement on page 5."
)

ENDORSEMENT_TITLE = "HIGH-DESERT TRANSIT ENDORSEMENT"
ENDORSEMENT_SUB = "THE ERG  ·  ISSUED QAMAR CITY 03 MAR 2024"
ENDORSEMENT_BODY = (
    "THE ERG PASSES ARE CLOSED 15 JUN – 15 SEP. "
    "BEARER MAY CROSS ONLY WITH A LICENSED WATER-BEARER. "
    "REPORT TO THE WELL-HOUSE WARDEN."
)

VISA_TITLE = "SARQ  ·  VISITOR VISA"
VISA_ROWS = [
    ("TYPE", "C · SINGLE ENTRY"),
    ("DURATION OF STAY", "30 DAYS"),
    ("VALID FROM", "01 OCT 2024"),
    ("UNTIL", "30 OCT 2024"),
    ("ISSUED AT", "QAMAR CITY, 20 SEP 2024"),
    ("FEE", "40 QMR"),
]

# (place, kind, date, gate, ink)
STAMPS = [
    ("QAMAR", "DEPARTURE", "02 OCT 2024", "OLD WELL GATE", "red"),
    ("ZELTA", "ARRIVAL", "02 OCT 2024", "", "blue"),
    ("ZELTA", "DEPARTURE", "18 OCT 2024", "", "green"),
    ("QAMAR", "ARRIVAL", "18 OCT 2024", "OLD WELL GATE", "purple"),
    ("QAMAR", "DEPARTURE", "10 FEB 2025", "OLD WELL GATE", "blue"),
    ("SARQ", "ARRIVAL", "11 FEB 2025", "", "green"),
    ("SARQ", "DEPARTURE", "25 FEB 2025", "", "red"),
    ("QAMAR", "ARRIVAL", "26 FEB 2025", "OLD WELL GATE", "purple"),
]

CONDITIONS_BODY = (
    "The bearer must present this passport at the well-house "
    "before crossing the Erg. The border is the water. "
    "The North Erg is closed June–September without a summer permit."
)
FOOTER = (
    "This passport remains the property of the Republic of Qamar. "
    "If found, please return to any Qamari consulate or well-house."
)

# ---------------------------------------------------------------- colours

BG = (34, 30, 27)
PAPER = (245, 239, 221)
PAPER_DARK = (236, 228, 203)
INK = (32, 26, 22)
ACCENT = (164, 74, 31)        # burnt sienna
ACCENT_DARK = (124, 52, 19)
ACCENT_LIGHT = (201, 123, 74)
MUTED = (110, 96, 78)
STAMP_INK = {
    "red": (163, 51, 39),
    "blue": (44, 79, 138),
    "green": (46, 107, 62),
    "purple": (107, 63, 140),
}
VISA_BG = (220, 232, 216)
VISA_BORDER = (122, 154, 114)
PHOTO_BG = (195, 204, 210)
SCARF = (201, 168, 106)
SCARF_DARK = (178, 140, 78)
SKIN = (217, 169, 134)
SKIN_DARK = (198, 148, 112)
ROBE = (58, 47, 42)

# ---------------------------------------------------------------- fonts

FD = "/usr/share/fonts/truetype/dejavu/"


def font(name, size):
    return ImageFont.truetype(FD + name, size)


SERIF = lambda s: font("DejaVuSerif.ttf", s)          # noqa: E731
SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)   # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)            # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)     # noqa: E731
MONO = lambda s: font("DejaVuSansMono.ttf", s)        # noqa: E731

W, H = 1024, 1024

# ---------------------------------------------------------------- MRZ (ICAO 9303)


def _mrz_val(c):
    if c == "<":
        return 0
    if c.isdigit():
        return int(c)
    return ord(c) - 55  # A=10 ... Z=35


def _mrz_check(s):
    w = (7, 3, 1)
    return str(sum(_mrz_val(c) * w[i % 3] for i, c in enumerate(s)) % 10)


def mrz_lines():
    line1 = "P<QMRAMRANI<<LAYLA<NOOR".ljust(44, "<")
    doc = "QMR002914"
    dob = "830514"
    exp = "340302"
    pers = "1405832914".ljust(14, "<")
    core = (
        doc + _mrz_check(doc)
        + "QMR"
        + dob + _mrz_check(dob)
        + "F"
        + exp + _mrz_check(exp)
        + pers + _mrz_check(pers)
    )
    line2 = core + _mrz_check(core)
    assert len(line1) == 44 and len(line2) == 44
    return line1, line2


# ---------------------------------------------------------------- helpers


def spaced(d, xy, text, fnt, fill, tracking=1):
    """Draw text with extra letter spacing (small-caps look)."""
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill)
        x += d.textlength(ch, font=fnt) + tracking


def spaced_w(d, text, fnt, tracking=1):
    return sum(d.textlength(c, font=fnt) + tracking for c in text) - tracking


def wrap(d, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(draw, text, path, start, max_w):
    size = start
    while size > 8:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, 8)


def label_value(d, x, y, label, value, vsize=17, vfont=None, label_size=10):
    d.text((x, y), label, font=SANS(label_size), fill=MUTED)
    vf = vfont or SERIF_B(vsize)
    d.text((x, y + label_size + 3), value, font=vf, fill=INK)


# ---------------------------------------------------------------- emblem


def emblem_layer(size):
    """Crescent moon over a well, inside a ring. Accent colour."""
    s = size
    lay = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    cx, cy, r = s // 2, s // 2, s // 2 - 3
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ACCENT + (255,), width=3)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
              outline=ACCENT + (255,), width=1)
    # crescent moon: filled disc, then a paper-coloured disc offset
    mx, my, mr = cx, cy - r // 3, r // 3
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=ACCENT + (255,))
    d.ellipse([mx - mr + 8, my - mr - 3, mx + mr + 8, my + mr - 3],
              fill=PAPER + (255,))
    # the well: stone rim + water
    wx0, wx1 = cx - r // 2, cx + r // 2
    wy = cy + r // 4
    d.polygon([(wx0, wy + 12), (wx1, wy + 12), (wx1 - 5, wy), (wx0 + 5, wy)],
              fill=ACCENT + (255,))
    d.rectangle([wx0 + 4, wy + 2, wx1 - 4, wy + 6], fill=(250, 246, 232, 255))
    d.line([wx0 + 2, wy - 8, wx1 - 2, wy - 8], fill=ACCENT + (255,), width=2)
    d.line([wx0 + 2, wy - 8, wx0 + 2, wy], fill=ACCENT + (255,), width=2)
    d.line([wx1 - 2, wy - 8, wx1 - 2, wy], fill=ACCENT + (255,), width=2)
    return lay


# ---------------------------------------------------------------- portrait


def portrait_layer(w, h):
    """Flat-style dignified portrait: sand headscarf, dark robe, pale backdrop."""
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rectangle([0, 0, w, h], fill=PHOTO_BG + (255,))
    # shoulders / robe
    d.ellipse([w * 0.08, h * 0.78, w * 0.92, h * 1.25], fill=ROBE + (255,))
    d.polygon([(w * 0.30, h), (w * 0.42, h * 0.80), (w * 0.58, h * 0.80),
               (w * 0.70, h)], fill=(46, 36, 33, 255))
    # neck
    d.rectangle([w * 0.43, h * 0.62, w * 0.57, h * 0.82], fill=SKIN_DARK + (255,))
    # headscarf: outer shape covering the whole head
    d.ellipse([w * 0.16, h * 0.02, w * 0.84, h * 0.74], fill=SCARF + (255,))
    # wide shoulder drapes (shawl panels, not hair falls)
    d.polygon([(w * 0.16, h * 0.48), (w * 0.30, h * 0.40), (w * 0.36, h * 0.82),
               (w * 0.06, h * 0.98)], fill=SCARF + (255,))
    d.polygon([(w * 0.84, h * 0.48), (w * 0.70, h * 0.40), (w * 0.64, h * 0.82),
               (w * 0.94, h * 0.98)], fill=SCARF + (255,))
    d.line([w * 0.30, h * 0.40, w * 0.36, h * 0.82], fill=SCARF_DARK + (255,), width=2)
    d.line([w * 0.70, h * 0.40, w * 0.64, h * 0.82], fill=SCARF_DARK + (255,), width=2)
    # face opening, lower and narrower so the scarf frames it
    d.ellipse([w * 0.34, h * 0.20, w * 0.66, h * 0.60], fill=SKIN + (255,))
    # forehead band of the wrap
    d.pieslice([w * 0.28, h * 0.10, w * 0.72, h * 0.38], 180, 360,
               fill=SCARF_DARK + (255,))
    # chin wrap band under the face
    d.arc([w * 0.30, h * 0.42, w * 0.70, h * 0.72], 15, 165,
          fill=SCARF_DARK + (255,), width=7)
    # side knot where the wrap is tied
    d.ellipse([w * 0.68, h * 0.46, w * 0.76, h * 0.54], fill=SCARF_DARK + (255,))
    # brows
    d.arc([w * 0.38, h * 0.33, w * 0.48, h * 0.40], 200, 340, fill=INK + (255,), width=2)
    d.arc([w * 0.52, h * 0.33, w * 0.62, h * 0.40], 200, 340, fill=INK + (255,), width=2)
    # eyes
    d.ellipse([w * 0.405, h * 0.405, w * 0.455, h * 0.43], fill=INK + (255,))
    d.ellipse([w * 0.545, h * 0.405, w * 0.595, h * 0.43], fill=INK + (255,))
    # nose + mouth
    d.line([w * 0.50, h * 0.44, w * 0.49, h * 0.51], fill=SKIN_DARK + (255,), width=2)
    d.line([w * 0.46, h * 0.555, w * 0.54, h * 0.555], fill=(122, 62, 52, 255), width=2)
    # scarf fold lines on the crown
    d.arc([w * 0.24, h * 0.06, w * 0.58, h * 0.26], 300, 30, fill=SCARF_DARK + (255,), width=2)
    d.arc([w * 0.42, h * 0.06, w * 0.76, h * 0.26], 150, 240, fill=SCARF_DARK + (255,), width=2)
    return lay


# ---------------------------------------------------------------- stamps


def stamp_layer(place, kind, date, gate, ink_name, rot):
    """One rubber stamp, drawn straight then rotated."""
    ink = STAMP_INK[ink_name]
    sw, sh = 208, 92
    lay = Image.new("RGBA", (sw + 24, sh + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x0, y0, x1, y1 = 12, 12, 12 + sw, 12 + sh
    d.rounded_rectangle([x0, y0, x1, y1], radius=8, outline=ink + (230,), width=3)
    d.line([x0 + 8, y0 + 30, x1 - 8, y0 + 30], fill=ink + (230,), width=1)
    d.line([x0 + 8, y1 - 24, x1 - 8, y1 - 24], fill=ink + (230,), width=1)
    cx = (x0 + x1) // 2
    f_place = fit_font(d, place, "DejaVuSans-Bold.ttf", 17, sw - 24)
    d.text((cx, y0 + 6), place, font=f_place, fill=ink + (235,), anchor="ma")
    f_kind = fit_font(d, kind, "DejaVuSans.ttf", 12, sw - 24)
    d.text((cx, y0 + 32), kind, font=f_kind, fill=ink + (235,), anchor="ma")
    d.text((cx, y0 + 48), date, font=SANS_B(14), fill=ink + (235,), anchor="ma")
    if gate:
        d.text((cx, y1 - 21), gate, font=SANS(9), fill=ink + (220,), anchor="ma")
    return lay.rotate(rot, resample=Image.BICUBIC, expand=True)


# ---------------------------------------------------------------- pages

def draw_left_page(img):
    x0, y0, pw, ph = 26, 36, 472, 952
    d = ImageDraw.Draw(img, "RGBA")
    # paper + faint watermark rings
    d.rectangle([x0, y0, x0 + pw, y0 + ph], fill=PAPER + (255,))
    d.ellipse([x0 + 120, y0 + 330, x0 + 360, y0 + 570],
              outline=ACCENT_LIGHT + (28,), width=2)
    d.ellipse([x0 + 150, y0 + 360, x0 + 330, y0 + 540],
              outline=ACCENT_LIGHT + (28,), width=1)
    d.rectangle([x0 + 5, y0 + 5, x0 + pw - 5, y0 + ph - 5],
                outline=ACCENT + (120,), width=1)
    d = ImageDraw.Draw(img)

    # emblem
    emb = emblem_layer(64)
    img.paste(emb, (x0 + pw // 2 - 32, y0 + 14), emb)

    # country header
    d.text((x0 + pw // 2, y0 + 88), COUNTRY, font=SERIF_B(31),
           fill=ACCENT_DARK, anchor="ma")
    d.text((x0 + pw // 2, y0 + 124), COUNTRY_NATIVE, font=SERIF(15),
           fill=INK, anchor="ma")
    spaced(d, (x0 + pw // 2 - spaced_w(d, "PASSPORT  ·  PASAPOR",
           SANS(12), 2) // 2, y0 + 146), "PASSPORT  ·  PASAPOR",
           SANS(12), MUTED, 2)
    d.line([x0 + 24, y0 + 170, x0 + pw - 24, y0 + 170], fill=INK, width=1)
    d.line([x0 + 24, y0 + 173, x0 + pw - 24, y0 + 173], fill=INK, width=1)

    # photo
    px, py, pwid, phei = x0 + 26, y0 + 188, 128, 164
    d.rectangle([px - 3, py - 3, px + pwid + 3, py + phei + 3],
                outline=INK, width=1, fill=(255, 255, 255, 255))
    por = portrait_layer(pwid, phei)
    img.paste(por, (px, py), por)
    d.text((px, py + phei + 6), "PHOTOGRAPH", font=SANS(8), fill=MUTED)

    # fields right of photo
    fx = x0 + 178
    label_value(d, fx, y0 + 188, "TYPE", DOC_TYPE, 17)
    label_value(d, fx + 62, y0 + 188, "CODE", DOC_CODE, 17)
    label_value(d, fx + 128, y0 + 188, "PASSPORT No.", DOC_NO, 17)
    label_value(d, fx, y0 + 240, "SURNAME", SURNAME, 18)
    label_value(d, fx, y0 + 292, "GIVEN NAMES", GIVEN, 18)
    label_value(d, fx, y0 + 344, "NATIONALITY", NATIONALITY, 17)
    label_value(d, fx, y0 + 396, "DATE OF BIRTH", DOB, 17)
    label_value(d, fx + 150, y0 + 396, "SEX", SEX, 17)
    label_value(d, fx, y0 + 448, "PLACE OF BIRTH", POB, 16)
    label_value(d, fx, y0 + 500, "DATE OF ISSUE", ISSUED, 17)
    label_value(d, fx + 150, y0 + 500, "DATE OF EXPIRY", EXPIRY, 17)
    label_value(d, fx, y0 + 552, "AUTHORITY", AUTHORITY, 15)
    label_value(d, fx, y0 + 604, "PERSONAL No.", PERSONAL, 17)

    # signature (slanted serif, own layer, rotated)
    sig = Image.new("RGBA", (300, 44), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sig)
    sd.text((4, 6), SIGNATURE, font=SERIF(24), fill=(38, 42, 90, 255))
    sig = sig.rotate(-3, resample=Image.BICUBIC, expand=True)
    img.paste(sig, (x0 + 26, y0 + 668), sig)
    d.line([x0 + 26, y0 + 700, x0 + 250, y0 + 700], fill=INK, width=1)
    d.text((x0 + 26, y0 + 706), "HOLDER'S SIGNATURE", font=SANS(8), fill=MUTED)

    # ghost image, bottom-right of the data area
    ghost = portrait_layer(84, 108)
    faded = Image.new("RGBA", ghost.size, PAPER + (255,))
    ghost = Image.blend(faded, ghost, 0.30)
    img.paste(ghost, (x0 + pw - 118, y0 + 612), ghost)
    d.text((x0 + pw - 118, y0 + 724), "GHOST IMAGE", font=SANS(7), fill=MUTED)

    # observations box
    bx, by, bw = x0 + 26, y0 + 742, pw - 52
    d.rectangle([bx, by, bx + bw, by + 76], outline=ACCENT, width=1)
    d.text((bx + 8, by + 6), "OBSERVATIONS", font=SANS_B(10), fill=ACCENT_DARK)
    lines = wrap(d, OBSERVATIONS, SANS(11), bw - 16)
    yy = by + 22
    for ln in lines:
        d.text((bx + 8, yy), ln, font=SANS(11), fill=INK)
        yy += 14

    # MRZ strip
    l1, l2 = mrz_lines()
    mx, my, mw = x0 + 26, y0 + 838, pw - 52
    d.rectangle([mx, my, mx + mw, my + 62], outline=ACCENT, width=1)
    mf = MONO(15)
    while d.textlength(l1, font=mf) > mw - 16 and mf.size > 8:
        mf = MONO(mf.size - 1)
    d.text((mx + 8, my + 7), l1, font=mf, fill=INK)
    d.text((mx + 8, my + 32), l2, font=mf, fill=INK)

    d.text((x0 + 22, y0 + ph - 26), "2", font=SERIF(13), fill=MUTED)


def draw_right_page(img):
    x0, y0, pw, ph = 526, 36, 472, 952
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([x0, y0, x0 + pw, y0 + ph], fill=PAPER + (255,))
    d.ellipse([x0 + 110, y0 + 420, x0 + 360, y0 + 670],
              outline=ACCENT_LIGHT + (24,), width=2)
    d.rectangle([x0 + 5, y0 + 5, x0 + pw - 5, y0 + ph - 5],
                outline=ACCENT + (120,), width=1)
    d = ImageDraw.Draw(img)

    # header
    d.text((x0 + 22, y0 + 16), "VISAS  ·  VIZE", font=SERIF_B(26),
           fill=ACCENT_DARK)
    d.text((x0 + pw - 22, y0 + 20), "5", font=SERIF(14), fill=MUTED, anchor="ra")
    d.text((x0 + 22, y0 + 50), "ENTRY AND EXIT STAMPS — TRAVEL HISTORY",
           font=SANS(9), fill=MUTED)

    # endorsement box
    ex, ey, ew = x0 + 22, y0 + 70, pw - 44
    d.rectangle([ex, ey, ex + ew, ey + 118], outline=INK, width=1)
    d.text((ex + 10, ey + 8), ENDORSEMENT_TITLE, font=SANS_B(11),
           fill=ACCENT_DARK)
    d.text((ex + 10, ey + 24), ENDORSEMENT_SUB, font=SANS(9), fill=MUTED)
    lines = wrap(d, ENDORSEMENT_BODY, SANS(11), ew - 140)
    yy = ey + 42
    for ln in lines:
        d.text((ex + 10, yy), ln, font=SANS(11), fill=INK)
        yy += 14
    # round fee seal overlapping the endorsement box's bottom-right corner
    seal = Image.new("RGBA", (104, 104), (0, 0, 0, 0))
    sd = ImageDraw.Draw(seal)
    sd.ellipse([5, 5, 99, 99], outline=STAMP_INK["red"] + (235,), width=3)
    sd.ellipse([12, 12, 92, 92], outline=STAMP_INK["red"] + (200,), width=1)
    sd.text((52, 26), "WELL TAX", font=SANS_B(11),
            fill=STAMP_INK["red"] + (235,), anchor="ma")
    sd.text((52, 42), "PAID", font=SANS_B(13),
            fill=STAMP_INK["red"] + (235,), anchor="ma")
    sd.text((52, 60), "6 QMR", font=SANS_B(12),
            fill=STAMP_INK["red"] + (235,), anchor="ma")
    seal = seal.rotate(12, resample=Image.BICUBIC, expand=True)
    img.paste(seal, (x0 + pw - 122, y0 + 98), seal)

    # visa sticker (pale green)
    vx, vy, vw = x0 + 22, y0 + 204, pw - 44
    d.rectangle([vx, vy, vx + vw, vy + 128], fill=VISA_BG + (255,),
                outline=VISA_BORDER, width=2)
    d.text((vx + 12, vy + 8), VISA_TITLE, font=SANS_B(13), fill=(46, 90, 52))
    d.text((vx + vw - 12, vy + 8), "C", font=SERIF_B(16), fill=(46, 90, 52),
           anchor="ra")
    yy = vy + 32
    for lab, val in VISA_ROWS:
        d.text((vx + 12, yy), lab, font=SANS(9), fill=MUTED)
        d.text((vx + 150, yy), val, font=SANS_B(11), fill=INK)
        yy += 15

    # stamps grid: 2 columns x 4 rows
    rots = [-2, 2, 3, -3, 2, -2, -3, 3]
    gx, gy = x0 + 14, y0 + 348
    cw, rh = 226, 100
    for i, (place, kind, date, gate, ink_name) in enumerate(STAMPS):
        st = stamp_layer(place, kind, date, gate, ink_name, rots[i])
        col, row = i % 2, i // 2
        img.paste(st, (gx + col * cw - 6, gy + row * rh - 6), st)

    # conditions box
    cx, cy, cw2 = x0 + 22, y0 + 762, pw - 44
    d.rectangle([cx, cy, cx + cw2, cy + 26], fill=ACCENT_DARK + (255,))
    d.text((cx + 10, cy + 6), "CONDITIONS OF ISSUE", font=SANS_B(11),
           fill=(250, 246, 232))
    d.rectangle([cx, cy + 26, cx + cw2, cy + 118], outline=ACCENT, width=1)
    lines = wrap(d, CONDITIONS_BODY, SANS(11), cw2 - 20)
    yy = cy + 34
    for ln in lines:
        d.text((cx + 10, yy), ln, font=SANS(11), fill=INK)
        yy += 14
    d.text((cx + 10, cy + 96), "No. 002914  ·  Fee paid at issue",
           font=SANS(9), fill=MUTED)

    # footer
    lines = wrap(d, FOOTER, SERIF(11), pw - 44)
    yy = y0 + 896
    for ln in lines:
        d.text((x0 + 22, yy), ln, font=SERIF(11), fill=MUTED)
        yy += 14


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # centre gutter shadow
    d.rectangle([498, 36, 526, 988], fill=(12, 10, 9))
    d.rectangle([494, 36, 498, 988], fill=(60, 54, 48))
    d.rectangle([526, 36, 530, 988], fill=(60, 54, 48))
    draw_left_page(img)
    draw_right_page(img)

    os.makedirs("/output", exist_ok=True)
    img.save("/output/entry.png")
    size = os.path.getsize("/output/entry.png")
    print("saved /output/entry.png", img.size, size, "bytes")
    assert img.size == (1024, 1024)
    assert size <= 1048576


if __name__ == "__main__":
    main()
