# all.tsv → collect/ (흑백 jpg) + collect.json.  쿼리가 "=키"면 photos/ 의 기존 사진 재사용
import csv, json, re, io, time, shutil, urllib.request, urllib.parse
from PIL import Image, ImageOps
UA = {'User-Agent': 'frankenstein-places-mockup/0.1 (student design project)'}
def get(url):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except Exception as e: err = e; time.sleep(30 * (i + 1))
    raise err
def year(meta):
    m = re.search(r'1[5-9]\d\d', re.sub('<[^>]+>', '', meta.get('DateTimeOriginal', {}).get('value', '')))
    return int(m.group()) if m else None
def search(q):
    api = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({
        'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6,
        'gsrsearch': q + ' filetype:bitmap', 'gsrlimit': 15, 'prop': 'imageinfo',
        'iiprop': 'url|size|extmetadata', 'iiurlwidth': 960})
    return sorted(json.loads(get(api)).get('query', {}).get('pages', {}).values(), key=lambda p: p['index'])
credits = json.load(open('credits.json'))
try: out = json.load(open('collect.json'))
except FileNotFoundError: out = {}
for i, (page, label, en, q) in enumerate(csv.reader(open('all.tsv'), delimiter='\t')):
    key = f'a{i:03d}'
    if key in out: continue
    base = dict(page=page, label=label, en=en)
    if q.startswith('='):
        shutil.copy(f'photos/{q[1:]}.jpg', f'collect/{key}.jpg')
        c = credits[q[1:]]
        out[key] = dict(base, **{k: c[k] for k in ('title', 'url', 'year', 'artist', 'license')}, reuse=q[1:])
    else:
        time.sleep(5)
        pages = search(q) or search(' '.join(q.split()[:2]) + ' 19th century')
        cands = [p for p in pages if p['imageinfo'][0]['width'] >= 500 and p['title'].lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff'))]
        old = [p for p in cands if (year(p['imageinfo'][0].get('extmetadata', {})) or 9999) <= 1930]
        pick = (old or cands or [None])[0]
        if not pick: print('NONE', key, label, q); continue
        ii = pick['imageinfo'][0]; meta = ii.get('extmetadata', {})
        ImageOps.grayscale(Image.open(io.BytesIO(get(ii['thumburl']))).convert('RGB')).save(f'collect/{key}.jpg', quality=78)
        strip = lambda k: re.sub('<[^>]+>', '', meta.get(k, {}).get('value', '')).strip()[:80]
        out[key] = dict(base, title=pick['title'], url=ii['descriptionurl'], year=year(meta), artist=strip('Artist'), license=strip('LicenseShortName'))
    print(key, label, '→', out[key]['title'][5:70], out[key]['year'])
    json.dump(out, open('collect.json', 'w'), ensure_ascii=False, indent=1)
