#!/usr/bin/env python3

import math
import re
from dataclasses import dataclass
import html
import json
import os
from PIL import Image

# First, extract games from the htmlified Google Docs document

with open("src_doc/Bitacora.html", "r") as file:
    src = file.read()

flags = re.MULTILINE | re.DOTALL

re_img = re.compile(r'src="([^"]+)"', flags)
re_txt = re.compile(r'<span class="c\d">([^<]+)</span>', flags)


def clean_text(txt: str) -> str:
    return html.unescape(txt.strip())


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


games = []
for img_i, img in enumerate(images):
    end: int = len(src) if img_i + 1 == len(images) else images[img_i+1]['at']

    i = img['at']

    title_match = re_txt.search(src[i:end])
    if not title_match:
        break
    i += title_match.end()

    desc = []
    while True:
        desc_match = re_txt.search(src[i:end])
        if not desc_match:
            break
        desc.append(desc_match[1])
        i += desc_match.end()

    game = {
        "image": f"{img['src']}.jpg",
        "title": clean_text(title_match[1]),
        "desc": clean_text(" ".join(desc)),
    }
    games.append(game)

    print("got game:")
    print(f"  image: \"{game['image']}\"")
    print(f"  title: {game['title']}")
    print(f"  description: {game['desc']}")

with open("games.js", "w") as file:
    file.write("rawGameData=")
    json.dump(games, file)

# Now, resize all images
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
