# source.pdf 글자 데이터 → text.html (책 줄바꿈 풀고 문단으로, 쪽 번호는 왼쪽 여백)
import pymupdf, html
d = pymupdf.open('source.pdf')
out, para, notes = [], [], []
def size(l):   # 줄의 글자 평균 크기 (글자마다 자간용 크기 차이가 있어서)
    sp = [(len(s['text'].strip()), s['size']) for s in l['spans'] if s['text'].strip()]
    return sum(n * z for n, z in sp) / sum(n for n, _ in sp)
def flush():   # 문단 끝 → 그동안 모인 각주를 문단 뒤에
    if para: out.append('<p>' + ''.join(para).strip() + '</p>'); para.clear()
    if notes: out.append('<p class="note">' + ' '.join(notes) + '</p>'); notes.clear()
for n, page in enumerate(d, 1):
    lines = [l for b in page.get_text('dict')['blocks'] for l in b.get('lines', [])
             if ''.join(s['text'] for s in l['spans']).strip()]
    body_x = min((l['bbox'][0] for l in lines if 9 <= size(l) < 12), default=0)
    mark = f'<span class="pg" id="p{n}" data-n="{n}"></span>'
    for l in lines:
        t = ''.join(s['text'] for s in l['spans']); z = size(l)
        if t.strip() == str(n): continue                     # 쪽 번호 줄
        if z < 9: notes.append(html.escape(t.strip())); continue
        if z >= 12: flush(); out.append(f'<h2>{mark}{html.escape(t.strip())}</h2>'); mark = ''; continue
        if l['bbox'][0] > body_x + 4: flush()                # 들여쓰기 = 새 문단
        para.append(mark + html.escape(t)); mark = ''
flush()
open('text.html', 'w').write(open('text.tpl.html').read().replace('{{BODY}}', '\n'.join(out)))
print(len(out), 'blocks')
