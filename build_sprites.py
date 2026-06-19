# -*- coding: utf-8 -*-
"""Détoure le fond noir des deux planches (ships / meteorites) et exporte
des sprites transparents encodés en base64 dans sprites.js (data-URI).
Pas de scipy : flood-fill et labellisation faits maison avec numpy."""
import base64, io, json
import numpy as np
from PIL import Image, ImageFilter

HERE = r"C:\Users\Utilisateur\OneDrive\Code\verb-blaster"
WORK = 760          # résolution de travail (planche carrée)
BRIGHT = 232        # seuil de luminance : au-dessus = fond (blanc)
FEATHER = 1.1       # flou du masque alpha (anti-aliasing des bords)

def load(name):
    im = Image.open(f"{HERE}\\{name}").convert("RGB").resize((WORK, WORK), Image.LANCZOS)
    return np.asarray(im).astype(np.int16)

def luminance(rgb):
    return (0.299*rgb[..., 0] + 0.587*rgb[..., 1] + 0.114*rgb[..., 2])

def dilate(mask):
    out = mask.copy()
    out[1:, :]  |= mask[:-1, :]
    out[:-1, :] |= mask[1:, :]
    out[:, 1:]  |= mask[:, :-1]
    out[:, :-1] |= mask[:, 1:]
    return out

def background_mask(rgb):
    """fond = pixels clairs (blancs) connectés au bord de la zone."""
    bright = luminance(rgb) > BRIGHT
    seed = np.zeros_like(bright)
    seed[0, :] = bright[0, :]; seed[-1, :] = bright[-1, :]
    seed[:, 0] = bright[:, 0]; seed[:, -1] = bright[:, -1]
    prev = -1
    while seed.sum() != prev:
        prev = seed.sum()
        seed = dilate(seed) & bright
    return seed  # True = fond à rendre transparent

def to_rgba(rgb, bg):
    h, w = bg.shape
    alpha = np.where(bg, 0, 255).astype(np.uint8)
    rgba = np.dstack([rgb.astype(np.uint8), alpha])
    img = Image.fromarray(rgba, "RGBA")
    # adoucit le bord alpha
    a = img.getchannel("A").filter(ImageFilter.GaussianBlur(FEATHER))
    img.putalpha(a)
    return img

def trim(img, pad=2):
    bbox = img.getbbox()
    if not bbox:
        return img
    l, t, r, b = bbox
    l = max(0, l-pad); t = max(0, t-pad)
    r = min(img.width, r+pad); b = min(img.height, b+pad)
    return img.crop((l, t, r, b))

def downscale(img, maxdim):
    s = maxdim / max(img.width, img.height)
    if s < 1:
        img = img.resize((max(1,round(img.width*s)), max(1,round(img.height*s))), Image.LANCZOS)
    return img

def to_uri(img):
    buf = io.BytesIO()
    img.save(buf, "PNG", optimize=True)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

# ---------------- VAISSEAUX : grille 4x2, détourage par cellule ----------------
ships_rgb = load("ships.png")
cw, ch = WORK//4, WORK//2
ships = []
for r in range(2):
    for c in range(4):
        cell = ships_rgb[r*ch:(r+1)*ch, c*cw:(c+1)*cw]
        bg = background_mask(cell)
        img = trim(to_rgba(cell, bg))
        img = downscale(img, 230)
        ships.append({"uri": to_uri(img), "w": img.width, "h": img.height})
        print(f"ship {len(ships)-1}: {img.width}x{img.height}")

# ---------------- METEORITES : détourage global + labellisation maison ----------
met_rgb = load("meteorites.png")
bg = background_mask(met_rgb)
fg = ~bg
# labellisation par propagation d'indices (basse résolution pour la vitesse)
SCALE = 4
small = fg[::SCALE, ::SCALE]
H, Wd = small.shape
idx = np.arange(H*Wd, dtype=np.int64).reshape(H, Wd)
lab = np.where(small, idx, -1)
changed = True
while changed:
    changed = False
    for shift in range(4):
        cur = lab.copy()
        if shift == 0: cur[1:, :]  = np.where((lab[1:,:]>=0)&(lab[:-1,:]>=0), np.minimum(lab[1:,:], lab[:-1,:]), lab[1:,:])
        if shift == 1: cur[:-1, :] = np.where((lab[:-1,:]>=0)&(lab[1:,:]>=0), np.minimum(lab[:-1,:], lab[1:,:]), lab[:-1,:])
        if shift == 2: cur[:, 1:]  = np.where((lab[:,1:]>=0)&(lab[:,:-1]>=0), np.minimum(lab[:,1:], lab[:,:-1]), lab[:,1:])
        if shift == 3: cur[:, :-1] = np.where((lab[:,:-1]>=0)&(lab[:,1:]>=0), np.minimum(lab[:,:-1], lab[:,1:]), lab[:,:-1])
        if not np.array_equal(cur, lab):
            changed = True; lab = cur

full = to_rgba(met_rgb, bg)
meteors = []
for v in np.unique(lab):
    if v < 0:
        continue
    ys, xs = np.where(lab == v)
    if len(xs) < 30:        # ignore le bruit / petits débris isolés
        continue
    x0, x1 = xs.min()*SCALE, (xs.max()+1)*SCALE
    y0, y1 = ys.min()*SCALE, (ys.max()+1)*SCALE
    crop = full.crop((x0, y0, x1, y1))
    crop = trim(crop)
    if crop.width < 24 or crop.height < 24:
        continue
    crop = downscale(crop, 190)
    meteors.append({"uri": to_uri(crop), "w": crop.width, "h": crop.height,
                    "area": int(len(xs))})

# garde les plus gros (vrais blocs), trie par taille décroissante
meteors.sort(key=lambda m: -m["area"])
for m in meteors:
    m.pop("area")
print(f"meteorites detectees: {len(meteors)}")

with open(f"{HERE}\\sprites.js", "w", encoding="utf-8") as f:
    f.write("// Sprites detoures (genere par build_sprites.py) — data-URI, pas de tainting canvas\n")
    f.write("window.SHIP_SPRITES = " + json.dumps(ships) + ";\n")
    f.write("window.METEOR_SPRITES = " + json.dumps(meteors) + ";\n")

import os
print("sprites.js:", round(os.path.getsize(f"{HERE}\\sprites.js")/1024), "KB")
