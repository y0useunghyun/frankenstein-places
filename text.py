# source.pdf 글자 전부 → text.html : 나누지 않고 왼쪽 위부터 한 덩어리로
import pymupdf, html
d = pymupdf.open('source.pdf')
parts = []
for n, page in enumerate(d, 1):
    for b in page.get_text('dict')['blocks']:
        for l in b.get('lines', []):
            t = ''.join(s['text'] for s in l['spans'])
            if t.strip() and t.strip() != str(n): parts.append(t)   # 쪽 번호 줄만 뺌
# 줄 끝 공백 = 단어 끝, 문장부호로 끝남 = 문단 끝 → 띄움 / 그 외 = 단어가 잘린 것 → 붙임
text = ''.join(p.strip() + (' ' if p.endswith(' ') or p.strip()[-1] in '.?!”」』)*' else '') for p in parts)
open('text.html', 'w').write(open('text.tpl.html').read().replace('{{BODY}}', html.escape(' '.join(text.split()))))
print(len(text), 'chars')
