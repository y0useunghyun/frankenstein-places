# credits.json + PDF 글자 좌표 → places.json (웹페이지가 읽는 데이터)
import json, pymupdf
from PIL import Image
d = pymupdf.open('source.pdf')
LABEL = {'몰': '몰산', '알프스산': '알프스산맥', '안개와': '안개와 눈의 땅', '아프리카': '아프리카 최남단의 곶', '빙원': '빙원', '첨탑': '잉골슈타트 첨탑',
         '잉골슈타트의': '잉골슈타트의 거리', '플랭팔렌': '플랭팔레', '셴이라는': '셴', '펠리시에': '펠리시에다리', '몽탕베르산': '몽탕베르',
         '얼음': '얼음 바다', '마을에': '어느 마을', '파리라는': '파리', '리옹까지': '리옹', '우리': '우리 호수', '브리튼의': '브리튼의 하얀 절벽',
         '세인트폴': '세인트폴 대성당', '퍼': '퍼스', '아서즈': '아서즈 시트', '묘지를': '가족 묘지', '지중': '지중해', '혹해': '흑해',
         '북극의': '북극의 영원한 얼음', '초라한': '바닷가의 초라한 마을', '최북단': '지구의 최북단', '음뗏목에': '얼음뗏목'}
out = []
for key, c in sorted(json.load(open('credits.json')).items(), key=lambda kv: (kv[1]['page'], int(kv[0].split('-')[1]))):
    p = d[c['page'] - 1]; W, H = p.rect.width, p.rect.height
    exact = [pymupdf.Rect(w[:4]) for w in p.get_text('words') if w[4].strip('.,“”') == c['term']]
    hits = exact or p.search_for(c['term'])
    r = hits[0] if hits else None
    w, h = Image.open(f'photos/{key}.jpg').size
    out.append(dict(c, key=key, w=w, h=h, label=LABEL.get(c['term'], c['term']),
                    box=[round(r.x0 / W, 4), round(r.y0 / H, 4), round(r.x1 / W, 4), round(r.y1 / H, 4)] if r else None))
json.dump(out, open('places.json', 'w'), ensure_ascii=False)
print(len(out), 'places;', sum(1 for o in out if not o['box']), 'without box')
