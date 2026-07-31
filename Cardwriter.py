#!/usr/bin/env python3

import json
import os
import textwrap
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

# -----------------------------
# Configuration
# -----------------------------

JSON_FILE = "translatedCards.json"
OUTPUT_DIR = "translated_proxies"
CACHE_DIR = "image_cache"

# Use a TTF that supports your language
FONT_FILE = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"

TITLE_SIZE = 13
TAG_SIZE =11
BODY_SIZE = 10

BORDER = 22
OVERLAY_ALPHA = 200        # 0-255
TEXT_COLOUR = (0, 0, 0)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

title_font = ImageFont.truetype(FONT_FILE, TITLE_SIZE)
tag_font = ImageFont.truetype(FONT_FILE, TAG_SIZE)
body_font = ImageFont.truetype(FONT_FILE, BODY_SIZE)


def download_image(url):
    filename = os.path.join(CACHE_DIR, os.path.basename(url))

    if not os.path.exists(filename):
        print("Downloading", url)
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        with open(filename, "wb") as f:
            f.write(r.content)

    return Image.open(filename).convert("RGBA")


def wrap(draw, text, font, width):
    words = text.split()

    if not words:
        return ""

    lines = []
    line = words[0]

    for word in words[1:]:
        test = line + " " + word
        if draw.textlength(test, font=font) <= width:
            line = test
        else:
            lines.append(line)
            line = word

    lines.append(line)
    return "\n".join(lines)


with open(JSON_FILE, encoding="utf-8") as f:
    cards = json.load(f)

for card in cards:

    try:
        img = download_image(card["imageUrl"])

        width, height = img.size

        overlay_top = height * 19 // 32

        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        odraw = ImageDraw.Draw(overlay)

        odraw.rounded_rectangle(
            (
                BORDER,
                overlay_top + BORDER,
                width - BORDER,
                height - BORDER,
            ),
            radius=BORDER,
            fill=(255, 255, 255, OVERLAY_ALPHA),
        )

        img = Image.alpha_composite(img, overlay)

        draw = ImageDraw.Draw(img)

        x = BORDER * 2
        y = overlay_top + BORDER * 2
        text_width = width - x * 2
        
        
        # Card name
        draw.text(
            (x, y),
            card.get("cardName", ""),
            fill=TEXT_COLOUR,
            font=title_font,
        )

        y += TITLE_SIZE + 10

        # Tags
        tags = ", ".join(tag["value"] for tag in card.get("tags", []))

        draw.text(
            (x, y),
            tags,
            fill=TEXT_COLOUR,
            font=tag_font,
        )

        y += TAG_SIZE + 15

        # Rules text
        rules = wrap(
            draw,
            card.get("text", "").replace("\r", ""),
            body_font,
            text_width,
        )

        draw.multiline_text(
            (x, y),
            rules,
            fill=TEXT_COLOUR,
            font=body_font,
            spacing=6,
        )

        outname = f'{card["cardNumber"]}.png'
        img.convert("RGB").save(os.path.join(OUTPUT_DIR, outname), quality=95)

        print("Created", outname)

    except Exception as e:
        print(card.get("cardNumber"), e)
