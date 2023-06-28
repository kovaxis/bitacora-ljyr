#!/usr/bin/env python3

import sys
import re
import html
import json
import os
from PIL import Image
import zipfile
import shutil

# Extract the zipped content
print("extracting archive...", flush=True, end="")
with zipfile.ZipFile(sys.argv[1], "r") as file:
    try:
        shutil.rmtree("./src_doc")
    except OSError:
        pass
    os.mkdir("./src_doc")
    file.extractall("./src_doc")
print(" done")

# Parse game data from the htmlified Google Docs document
print("parsing game metadata...", flush=True, end="")
with open("src_doc/Bitacora.html", "r") as file:
    src = file.read()

flags = re.MULTILINE | re.DOTALL

re_img = re.compile(r'src="([^"]+)"', flags)
re_txt = re.compile(r'>([^<]+)<', flags)


images = []
i = 0
while True:
    img_match = re_img.search(src[i:])
    if not img_match:
        break
    i += img_match.end()
    images.append({
        "src": img_match[1],
        "at": i,
    })


def clean_text(txt: str, unescape: bool, end_dot: bool):
    if unescape:
        txt = html.unescape(txt)
    txt = txt.strip()
    if txt:
        txt = txt[0].upper() + txt[1:]
    if end_dot:
        if txt and txt[-1] != ".":
            txt += "."
    else:
        while txt and txt[-1] == ".":
            txt = txt[:-1]
    return txt


games = []
for img_i, img in enumerate(images):
    end: int = len(src) if img_i + 1 == len(images) else images[img_i+1]['at']

    i = img['at']

    title_match = re_txt.search(src[i:end])
    if not title_match:
        raise Exception(f"no title for image {img}")
    i += title_match.end()

    obj_match = re_txt.search(src[i:end])
    if not obj_match:
        raise Exception(f"no objective for image {img}")
    i += obj_match.end()

    desc_match = re_txt.search(src[i:end])
    if not desc_match:
        raise Exception(f"no description for image {img}")
    i += desc_match.end()

    extra_match = re_txt.search(src[i:end])
    if extra_match:
        raise Exception(f"found extra text '{extra_match[1]}' for image {img}")

    game = {
        "image": f"{img['src']}.jpg",
        "title": clean_text(title_match[1], True, False),
        "obj": clean_text(obj_match[1], False, False),
        "desc": clean_text(desc_match[1], True, True),
    }
    games.append(game)

with open("gamedata.js", "w") as file:
    file.write("rawGameData=")
    json.dump(games, file)

print(" done")

print(f"got {len(games)} games")
for game in games:
    if not game['image'] or not game['title'] or not game['obj'] or not game['desc']:
        print(f"invalid game {game}")

# Now, resize all images
print("thumbnailing images...", flush=True, end="")
imgw = 110
imgh = 120
bg = Image.new('RGBA', (imgw, imgh), (255, 255, 255, 255))
for filename in os.listdir("src_doc/images"):
    img = Image.open(f"src_doc/images/{filename}").convert('RGBA')
    scale = max(imgw / img.width, imgh / img.height)
    srcw = min(img.width, round(imgw / scale))
    srch = min(img.height, round(imgh / scale))
    corner = (img.width - srcw) / 2, (img.height - srch) / 2
    box = (corner[0], corner[1], corner[0] + srcw, corner[1] + srch)
    img = img.resize((imgw, imgh), box=box)
    img = Image.alpha_composite(bg, img).convert('RGB')

    img.save(f"images/{filename}.jpg", "JPEG", quality=80)
print(" done")

# Remove original zip in order to mark it as consumed
print("removing zip file...", flush=True, end="")
os.remove(sys.argv[1])
print(" done")
