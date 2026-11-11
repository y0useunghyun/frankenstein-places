import pymupdf, html, re
d = pymupdf.open('source.pdf')
lines = []   # (텍스트, 등급)  0 본문 / 1 장·편지·서문 / 2 권 / 3 책 제목
for n, page in enumerate(d, 1):
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            t = ''.join(s['text'] for s in l['spans'])
            if not t.strip() or t.strip() == str(n): continue   # 쪽 번호 줄만 뺌
            k = sum(len(s['text']) for s in l['spans']) or 1
            size = sum(s['size'] * len(s['text']) for s in l['spans']) / k
            lv = 3 if size > 15 else 2 if size > 12.5 and re.match(r'제\d권', t.strip()) else 1 if size > 12.5 else 0
            lines.append((t, lv))

def join(p):   # 줄 끝 공백 = 단어 끝, 문장부호로 끝남 = 띄움 / 그 외 = 단어가 잘린 것 → 붙임
    return p.strip() + (' ' if p.endswith(' ') or p.strip()[-1] in '.?!”」』)*' else '')

tpl = open('text.tpl.html').read()
flat = ' '.join(''.join(join(t) for t, _ in lines).split())
open('text.html', 'w').write(tpl.replace('{{BODY}}', html.escape(flat)))

# 제목 크게 버전: 같은 흐름 안에서 제목만 튀어나옴
# 본문은 평탄 그대로, 제목은 제자리에서 크게 떠서 겹침 (줄 높이 안 바뀜)
out = ''.join(f'<span class="h h{lv}" data-t="{html.escape(t.strip())}">{html.escape(join(t))}</span>' if lv else html.escape(join(t)) for t, lv in lines)
open('text-big.html', 'w').write(tpl.replace('<title>프랑켄슈타인 원문</title>', '<title>프랑켄슈타인 원문 · 제목</title>')
                                     .replace('{{BODY}}', re.sub(r'\s+', ' ', out)))
print(len(flat), 'chars /', sum(1 for _, lv in lines if lv), 'headings')

# ── 3D 버전: 장소 이름 = 링크, 그 자리에 사진이 섬 ──────────────────────────
import json
MARK = ''   # 쪽 시작 표시 → 펼친 뒤 위치만 기록하고 지움
pages, raw = [], ''
for n, page in enumerate(d, 1):
    raw += MARK; pages.append(n)
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            t = ''.join(s['text'] for s in l['spans'])
            if t.strip() and t.strip() != str(n): raw += join(t)
squashed, start = ' '.join(raw.split()), {}
for n in pages:
    i = squashed.index(MARK); start[n] = i; squashed = squashed[:i] + squashed[i + 1:]
assert squashed == flat, '3D 본문이 평탄 본문과 다름'

places = [dict(p, terms=[p['term']], img=f'thumbs/p{p["key"]}.jpg') for p in json.load(open('places.json'))]
for k, c in json.load(open('collect.json')).items():
    words = sorted(c['label'].split(), key=len, reverse=True)
    places.append(dict(c, terms=[c['label'], *words], img=f'thumbs/{"p" + c["reuse"] if c.get("reuse") else k}.jpg'))

spans = []   # (시작, 끝, 장소) — 그 쪽 앞뒤 한 쪽 안에서 처음 나오는 곳
for p in places:
    pg = int(re.match(r'\d+', str(p['page']))[0]); lo, hi = start.get(pg - 1, 0), start.get(pg + 2, len(flat))
    for t in p['terms']:
        i = flat.find(t, lo, hi)
        if len(t) > 1 and i >= 0: spans.append((i, i + len(t), p)); break
spans.sort(key=lambda s: s[0])
body, at, used = '', 0, 0
for i, j, p in spans:
    if i < at: continue   # 겹치면 앞의 것만
    tip = ' · '.join(str(v) for v in (p['label'], p['en'], p.get('year')) if v)
    body += html.escape(flat[at:i]) + (f'<a class="pl" href="{html.escape(p["url"])}" target="_blank" rel="noopener" '
             f'data-img="{p["img"]}" title="{html.escape(tip)}">{html.escape(flat[i:j])}</a>')
    at, used = j, used + 1
body += html.escape(flat[at:])
open('text-3d.html', 'w').write(tpl.replace('<title>프랑켄슈타인 원문</title>', '<title>프랑켄슈타인 원문 · 3D</title>')
    .replace('{{BODY}}', body).replace('</body>', '<script src="text-3d.js"></script>\n</body>'))
print(used, '/', len(places), 'places linked')
