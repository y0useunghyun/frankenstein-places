# 위키미디어 공용에서 지명마다 옛 사진 1장 → 흑백 jpg + credits.json
import csv, json, re, io, sys, time, urllib.request, urllib.parse
from PIL import Image, ImageOps
UA = {'User-Agent': 'frankenstein-places-mockup/0.1 (student design project)'}
def get(url):
    for i in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30).read()
        except Exception as e: err = e; time.sleep(30 * (i + 1))
    raise err
def year(meta):
    m = re.search(r'1[5-9]\d\d', re.sub('<[^>]+>', '', meta.get('DateTimeOriginal', {}).get('value', '')))
    return int(m.group()) if m else None
out = {}
try: out = json.load(open('credits.json'))
except FileNotFoundError: pass
for i, (page, term, en, q) in enumerate(csv.reader(open('places.tsv'), delimiter='\t')):
    key = f'{page}-{i}'
    if key in out: continue
    time.sleep(2)
    def search(q):
      api = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({
        'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6,
        'gsrsearch': q + ' filetype:bitmap', 'gsrlimit': 15, 'prop': 'imageinfo',
        'iiprop': 'url|size|extmetadata', 'iiurlwidth': 900})
      return sorted(json.loads(get(api)).get('query', {}).get('pages', {}).values(), key=lambda p: p['index'])
    pages = search(q) or search(' '.join(q.split()[:2]) + ' 19th century')
    cands = [p for p in pages if p['imageinfo'][0]['width'] >= 500 and p['title'].lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff'))]
    old = [p for p in cands if (year(p['imageinfo'][0].get('extmetadata', {})) or 9999) <= 1930]
    pick = (old or cands or [None])[0]
    if not pick: print('NONE', page, term, q); continue
    ii = pick['imageinfo'][0]; meta = ii.get('extmetadata', {})
    img = ImageOps.grayscale(Image.open(io.BytesIO(get(ii['thumburl']))).convert('RGB'))
    img.save(f'photos/{key}.jpg', quality=78)
    strip = lambda k: re.sub('<[^>]+>', '', meta.get(k, {}).get('value', '')).strip()[:80]
    out[key] = dict(page=int(page), term=term, en=en, title=pick['title'], url=ii['descriptionurl'],
                    year=year(meta), artist=strip('Artist'), license=strip('LicenseShortName'))
    print(key, term, '→', pick['title'][:70], out[key]['year'])
    json.dump(out, open('credits.json', 'w'), ensure_ascii=False, indent=1)
