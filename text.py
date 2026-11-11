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
out = ''.join(f'<b class="h{lv}">{html.escape(t.strip())}</b> ' if lv else html.escape(join(t)) for t, lv in lines)
open('text-big.html', 'w').write(tpl.replace('<title>프랑켄슈타인 원문</title>', '<title>프랑켄슈타인 원문 · 제목</title>')
                                     .replace('{{BODY}}', re.sub(r'\s+', ' ', out)))
print(len(flat), 'chars /', sum(1 for _, lv in lines if lv), 'headings')
