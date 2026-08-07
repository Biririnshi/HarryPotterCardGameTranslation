#!/usr/bin/env python3

import base64
import html
import json
import os
import re
import sys
from pathlib import Path

import requests
from playwright.sync_api import sync_playwright

# -----------------------------
# Configuration
# -----------------------------

JSON_FILE = "translatedCards.json"
OUTPUT_DIR = "translated_proxies"
CACHE_DIR = "image_cache"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)


def download_image(url: str) -> str:
    filename = os.path.join(CACHE_DIR, os.path.basename(url))

    if not os.path.exists(filename):
        print("Downloading", url)
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        with open(filename, "wb") as handle:
            handle.write(response.content)

    return filename


def slugify(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-") or "card"


def escape_text(value: str) -> str:
    return html.escape(value or "", quote=False)


def format_effect_text(value: str) -> str:
    highlighted = re.sub(r"\(([^)]*)\)", r'<span class="keyword">\1</span>', value or "")
    return highlighted.replace("\r", "").replace("\n", "<br>")


def build_card_html(card: dict, image_path: str) -> str:
    title = escape_text(card.get("cardName", ""))
    tags = [escape_text(tag.get("value", "")) for tag in card.get("tags", []) if tag.get("value")]
    effect_text = format_effect_text(card.get("text", ""))
    card_type = card.get("cardType", {}).get("value", "")
    mp_value = card.get("mp")

    with open(image_path, "rb") as handle:
        encoded_image = base64.b64encode(handle.read()).decode("ascii")

    mp_badge = ""
    if mp_value is not None:
        mp_badge = f"""
            <div class=\"mp-badge\">{escape_text(str(mp_value))}</div>
        """

    tags_markup = "".join(
        f"<span class=\"tag-chip\">{tag}</span>" for tag in tags
    ) or ' '

    return f"""<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <style>
    :root {{
      color-scheme: dark;
      font-family: 'Hiragino Sans', 'Yu Gothic', 'Arial Unicode MS', 'Noto Sans CJK JP', sans-serif;
    }}
    html, body {{
      margin: 0;
      padding: 0;
      background: transparent;
      width: 744px;
      height: 1040px;
    }}
    body {{
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    .card {{
      width: 744px;
      height: 1040px;
      position: relative;
      overflow: hidden;
      border-radius: 34px;
      background: linear-gradient(145deg, #1a1425, #2d2238 60%, #17111f);
      box-shadow: 0 24px 60px rgba(255,255,255,0.45);
      color: black;
    }}
    .card-image {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}
    .overlay {{
      position: absolute;
      inset: 0;
      background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 65%, rgba(0,0,0,0.8) 100%);
      display: flex;
      flex-direction: column;
      justify-content: flex-end;
      padding: 36px 30px 28px;
      box-sizing: border-box;
    }}
    .content {{
      background: rgba(255,255,255,0.35);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(255,255,255,0.22);
      border-radius: 24px;
      padding: 18px 18px 16px;
      height: 30%;
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.22);
    }}
    .header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .title {{
      font-size: 36px;
      font-weight: 800;
      line-height: 1.15;
      margin: 0;
      text-shadow: 0 2px 10px rgba(255,255,255,0.3);
      word-break: break-word;
    }}
    .keyword {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 18px;
      font-weight: 650;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      background: rgba(227, 189, 0,0.8);
      white-space: nowrap;
    }}
    .meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 10px;
    }}
    .tag-chip {{
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 16px;
      font-weight: 650;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      background: rgba(255, 255, 255,0.6);
      white-space: nowrap;
    }}
    .effect {{
      font-size: 18px;
      font-weight: 600;
      line-height: 1.65;
      margin: 0;
      white-space: pre-wrap;
      color: black;
      text-shadow: 0 1px 8px rgba(255,255,255,0.25);
      overflow: hidden;
    }}
    .mp-badge {{
      position: absolute;
      right: 32px;
      bottom: 18px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: linear-gradient(135deg, #7b2cbf, #4c1d95);
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: 800;
      border: 4px solid rgba(255,255,255,0.9);
      box-shadow: 0 12px 24px rgba(0,0,0,0.3);
    }}
    .footer {{
      position:absolute;
      bottom:0;
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 12px;
      font-size: 20px;
      color: black;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
  </style>
</head>
<body>
  <div class=\"card\">
    <img class=\"card-image\" src=\"data:image/png;base64,{encoded_image}\" alt=\"{title}\" />
    <div class=\"overlay\">
      <div class=\"content\">
        <div class=\"header\">
          <h1 class=\"title\">{title}</h1>
          <span>{escape_text(card_type)}</span>
        </div>
        <div class=\"meta\">
          {tags_markup}
        </div>
        <p class=\"effect\">{effect_text}</p>
        <div class=\"footer\">
          <span>{escape_text(str(card.get('cardNumber', '')))}</span>
        </div>
      </div>
    </div>
    {mp_badge}
  </div>
</body>
</html>
"""


def render_html_to_png(html_string: str, output_path: str) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 372, "height": 520})
        page.set_content(html_string, wait_until="load")
        page.evaluate("document.body.style.zoom = '0.5';")
        page.screenshot(path=output_path, type="png")
        browser.close()


def main() -> None:
    with open(JSON_FILE, encoding="utf-8") as handle:
        cards = json.load(handle)

    for card in cards:
        try:
            image_path = download_image(card["imageUrl"])
            card_number = card.get("cardNumber", "")
            output_path = os.path.join(OUTPUT_DIR, f"{card_number}.png")
            html_string = build_card_html(card, image_path)
            render_html_to_png(html_string, output_path)
            print(f"Created {card_number}.png")
        except Exception as exc:
            print(card.get("cardNumber"), exc)


if __name__ == "__main__":
    main()
