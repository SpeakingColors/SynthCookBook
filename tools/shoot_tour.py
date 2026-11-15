#!/usr/bin/env python3
"""Reads the tour data of the Synth Cook Book from the page itself (docs/recipe-book.html) and draws the manual pictures.
Run: python3 tools/shoot_tour.py        (needs: pip install playwright pillow; playwright install chromium)
For every synth in the Synth menu it opens the panel, reads each control from the DOM (knobs: aria-label, aria-valuemin,
aria-valuemax; switches: the position labels; every control: its info bubble text from data-tip), groups them by the panel
boxes, and writes docs/tour/tour.json plus docs/tour/window_<synth>.png with numbered pink badges on the controls.
Nothing is typed in by hand."""
import json, os
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(root, "docs", "tour"); os.makedirs(OUT, exist_ok=True)
PAGE = "file://" + os.path.join(root, "docs", "recipe-book.html")

READ = """
() => {
  const rect = e => { const r = e.getBoundingClientRect(); return [r.x + scrollX, r.y + scrollY, r.width, r.height]; };
  const cv = document.getElementById('canvas');
  const boxes = [...cv.querySelectorAll('.box')].map(b => ({ title: (b.querySelector('h3') || {}).textContent || '', r: rect(b) }));
  const ctls = [];
  cv.querySelectorAll('.ctl, .sw').forEach(e => {
    const r = rect(e); if (r[2] < 2) return;
    const o = { r, tip: e.getAttribute('data-tip') || '' };
    if (e.classList.contains('ctl')) {
      const k = e.querySelector('svg[role=slider]');
      if (k) { o.kind = 'knob'; o.label = k.getAttribute('aria-label'); o.min = k.getAttribute('aria-valuemin'); o.max = k.getAttribute('aria-valuemax'); }
      else { o.kind = 'control'; o.label = (e.textContent || '').trim().slice(0, 30); }
    } else {
      o.kind = 'switch';
      const lbl = e.querySelector('.lbl'), slot = e.querySelector('button.slot');
      o.label = (lbl && lbl.textContent.trim()) || (slot && slot.getAttribute('aria-label')) || '';
      o.positions = [...e.querySelectorAll('.tag')].map(t => t.textContent.trim());
    }
    ctls.push(o);
  });
  const head = [...document.querySelectorAll('button[data-tip], .infodot')].filter(b => b.getBoundingClientRect().width > 0 && !cv.contains(b)).map(b => ({ label: (b.textContent || '').trim().replace(/\\s+/g, ' ') || b.id, tip: b.getAttribute('data-tip') || b.getAttribute('title') || '', id: b.id }));
  const banner = [...document.querySelectorAll('.warn, .note, .banner')].map(e => e.textContent.trim()).filter(t => t.length > 20).slice(0, 3);
  return { boxes, ctls, head, banner, W: document.documentElement.scrollWidth, H: document.documentElement.scrollHeight };
}
"""

def main():
    res = {"synths": []}
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1500, "height": 1000})
        pg.goto(PAGE); pg.wait_for_timeout(1500)
        keys = pg.evaluate("[...document.getElementById('synthSel').options].map(o => [o.value, o.textContent])")
        for key, name in keys:
            pg.select_option("#synthSel", key); pg.wait_for_timeout(900)
            pg.evaluate("document.querySelector('#fitBtn') && document.querySelector('#fitBtn').click()"); pg.wait_for_timeout(500)
            d = pg.evaluate(READ); d["key"] = key; d["name"] = name
            pg.screenshot(path=os.path.join(OUT, "_raw_%s.png" % key), full_page=True)
            res["synths"].append(d)
        pg2 = b.new_page(viewport={"width": 1500, "height": 900}, device_scale_factor=1.5)   # README / web page screenshot, no badges
        pg2.goto(PAGE); pg2.wait_for_timeout(1500)
        pg2.evaluate("document.querySelector('#fitBtn') && document.querySelector('#fitBtn').click()"); pg2.wait_for_timeout(500)
        pg2.screenshot(path=os.path.join(root, "docs", "screenshot.png"), full_page=True)
        b.close()
    for d in res["synths"]:
        ctl = d["ctls"]
        def grp(c):
            cx, cy = c["r"][0] + c["r"][2] / 2, c["r"][1] + c["r"][3] / 2
            best = None
            for i, bx in enumerate(d["boxes"]):
                x, y, w, h = bx["r"]
                if x <= cx <= x + w and y <= cy <= y + h and (best is None or w * h < d["boxes"][best]["r"][2] * d["boxes"][best]["r"][3]): best = i
            return best
        for c in ctl: c["group"] = grp(c)
        gorder = sorted(range(len(d["boxes"])), key=lambda i: (round(d["boxes"][i]["r"][1] / 40), d["boxes"][i]["r"][0]))
        rank = {g: n for n, g in enumerate(gorder)}
        ctl.sort(key=lambda c: (rank.get(c["group"], 999), round(c["r"][1] / 30), c["r"][0]))
        for n, c in enumerate(ctl, 1): c["n"] = n
        im = Image.open(os.path.join(OUT, "_raw_%s.png" % d["key"])).convert("RGB"); dr = ImageDraw.Draw(im)
        try: f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
        except Exception: f = ImageFont.load_default()
        for c in ctl:
            x, y = c["r"][0] + 6, c["r"][1] + 6
            dr.ellipse([x - 10, y - 10, x + 10, y + 10], fill=(255, 123, 177), outline=(22, 22, 56))
            t = str(c["n"]); w = dr.textlength(t, font=f); dr.text((x - w / 2, y - 8), t, fill=(22, 22, 56), font=f)
        im.save(os.path.join(OUT, "window_%s.png" % d["key"]), optimize=True); os.remove(os.path.join(OUT, "_raw_%s.png" % d["key"]))
        print(d["key"], len(ctl), "controls", len(d["boxes"]), "boxes")
    json.dump(res, open(os.path.join(OUT, "tour.json"), "w"), indent=1)

main()
