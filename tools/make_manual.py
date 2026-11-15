#!/usr/bin/env python3
"""Builds the PDF manual of Synth Cook Book from docs/manual.txt (sections start with '# ', bullets with '- ').
Usage: python3 tools/make_manual.py <ignored> <docs/manual.txt> <out.pdf>      Needs: pip install reportlab pillow
If docs/tour/tour.json exists (made by tools/shoot_tour.py from the recipe book page) the PDF gets an Interface tour after the Quick start:
a picture of each synth panel with numbered badges and a table of every control with range or positions and its info bubble text."""
import sys, re
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
import io, json, os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, PageBreak, KeepTogether, CondPageBreak, Table, TableStyle, Image as RLImage

_, txt, out = sys.argv[1:4]
h1 = ParagraphStyle('h1', fontName='Helvetica-Bold', fontSize=22, textColor=colors.HexColor('#1B0264'), spaceAfter=6)
h2 = ParagraphStyle('h2', fontName='Helvetica-Bold', fontSize=13, textColor=colors.HexColor('#7900E3'), spaceBefore=12, spaceAfter=4)
body = ParagraphStyle('b', fontName='Helvetica', fontSize=10, leading=13.5, spaceAfter=4)
esc = lambda s: s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
story = [Paragraph('Synth Cook Book', h1), Paragraph('Studio 87. Free and open source (AGPL-3.0-or-later; patches CC0 or CC-BY, see each file).', body)]

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOUR = os.path.join(root, "docs", "tour", "tour.json")
tcell = ParagraphStyle('tc', fontName='Helvetica', fontSize=8, leading=10)
tcellb = ParagraphStyle('tcb', fontName='Helvetica-Bold', fontSize=8, leading=10, textColor=colors.HexColor('#C2185B'))
def add_tour(story):
    if not os.path.exists(TOUR): return
    from PIL import Image
    T = json.load(open(TOUR))
    story.append(PageBreak()); story.append(Paragraph('Interface tour', h1))
    story.append(Paragraph('Pink numbers on each panel match the tables. The pictures are the recipe book page itself, with the Pro-1 recipe "Fat Dirty Bass" or the first recipe of each synth loaded; the knob positions are just that recipe. Ranges and info bubble texts were read from the page by tools/shoot_tour.py.', body))
    hd = T['synths'][0]['head']
    rows = [[Paragraph(esc(h['label'] or h['id']), tcellb), Paragraph(esc(h['tip']), tcell)] for h in hd if h['tip']]
    story.append(Paragraph('Header, recipe list and panel size', h2))
    t = Table(rows, colWidths=[40*mm, 134*mm]); t.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),0.4,colors.HexColor('#cccccc'))])); story.append(t)
    for d in T['synths']:
        im = Image.open(os.path.join(root, 'docs', 'tour', 'window_%s.png' % d['key'])).convert('RGB')
        story.append(PageBreak()); story.append(Paragraph(esc(d['name']), h2))
        b = io.BytesIO(); im.save(b, 'PNG'); b.seek(0); w, h = im.size
        story.append(RLImage(b, width=174*mm, height=174*mm*h/w))
        for gi, bx in enumerate(d['boxes']):
            items = [c for c in d['ctls'] if c['group'] == gi]
            if not items: continue
            x, y, bw, bh = bx['r']; cr = im.crop((max(0, int(x) - 6), max(0, int(y) - 6), min(w, int(x + bw) + 6), min(h, int(y + bh) + 6)))
            cb = io.BytesIO(); cr.save(cb, 'PNG'); cb.seek(0); s = min(120*mm / cr.size[0], 42*mm / cr.size[1])
            rws = []
            for c in items:
                rg = ('%s to %s' % (c['min'], c['max'])) if c['kind'] == 'knob' and c.get('min') is not None else (' / '.join(c.get('positions') or []) if c['kind'] == 'switch' else '')
                tip = c['tip'] if c['tip'].strip().lower() != c['label'].strip().lower() else '(the info bubble only repeats the name)'
                rws.append([Paragraph(str(c['n']), tcellb), Paragraph(esc(c['label']), tcellb), Paragraph(esc(rg), tcell), Paragraph(esc(tip), tcell)])
            tb = Table(rws, colWidths=[8*mm, 28*mm, 34*mm, 104*mm]); tb.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,-1),0.4,colors.HexColor('#cccccc')),('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#f7f3ec'))]))
            story.append(CondPageBreak(70*mm)); story.append(KeepTogether([Paragraph(esc(bx['title'] or 'Panel'), ParagraphStyle('gt', fontName='Helvetica-Bold', fontSize=11, textColor=colors.HexColor('#7900E3'), spaceBefore=8, spaceAfter=3)), RLImage(cb, width=cr.size[0]*s, height=cr.size[1]*s), Spacer(1, 3), tb]))
        loose = [c for c in d['ctls'] if c['group'] is None]
        if loose:
            story.append(Paragraph('Other controls', h2))
            story.append(Table([[Paragraph(str(c['n']), tcellb), Paragraph(esc(c['label']), tcellb), Paragraph(esc(c['tip']), tcell)] for c in loose], colWidths=[8*mm, 40*mm, 126*mm]))

sections, cur = [], None
for line in open(txt, encoding='utf-8').read().splitlines():
    if line.startswith('# '): cur = (line[2:].strip(), []); sections.append(cur)
    elif cur is not None: cur[1].append(line)
for title, lines in sections:
    story.append(Paragraph(esc(title), h2)); items = []; para = []
    def flush_para():
        global para
        if para: story.append(Paragraph(esc(' '.join(para)), body)); para = []
    def flush_items():
        global items
        if items: story.append(ListFlowable([ListItem(Paragraph(esc(i), body)) for i in items], bulletType='bullet', leftIndent=14)); items = []
    for l in lines:
        if l.startswith('- '): flush_para(); items.append(l[2:])
        elif not l.strip(): flush_para(); flush_items()
        else: flush_items(); para.append(l.strip())
    flush_para(); flush_items()
    if title == 'Quick start': add_tour(story)
SimpleDocTemplate(out, pagesize=A4, leftMargin=18*mm, rightMargin=18*mm, topMargin=16*mm, bottomMargin=16*mm, title='Synth Cook Book manual').build(story)
