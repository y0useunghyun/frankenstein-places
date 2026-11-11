# pick2.tsv: collect/ 사진 교체 (제목 / ?검색 / =photos키 재사용) + 엉뚱한 것 삭제
import csv, json, re, io, os, time, shutil, urllib.request, urllib.parse
from PIL import Image, ImageOps
UA = {'User-Agent': 'frankenstein-places-mockup/0.1 (student design project)'}
def get(url):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except Exception as e: err = e; time.sleep(30 * (i + 1))
    raise err
C = json.load(open('collect.json')); credits = json.load(open('credits.json'))
rows = list(csv.reader(open('all.tsv'), delimiter='\t'))
for key, title in csv.reader(open('pick2.tsv'), delimiter='\t'):
    page, label, en, _ = rows[int(key[1:])]
    base = dict(page=page, label=label, en=en)
    if title.startswith('='):
        shutil.copy(f'photos/{title[1:]}.jpg', f'collect/{key}.jpg'); c = credits[title[1:]]
        C[key] = dict(base, **{k: c[k] for k in ('title', 'url', 'year', 'artist', 'license')}, reuse=title[1:])
    else:
        time.sleep(5)
        q = {'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'iiprop': 'url|extmetadata', 'iiurlwidth': 960}
        if title.startswith('?'): q.update(generator='search', gsrnamespace=6, gsrsearch=title[1:], gsrlimit=1)
        else: q['titles'] = 'File:' + title
        p = next(iter(json.loads(get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q)))['query']['pages'].values()))
        if 'imageinfo' not in p: print('MISSING', key, title); continue
        ii = p['imageinfo'][0]; meta = ii.get('extmetadata', {})
        strip = lambda k: re.sub('<[^>]+>', '', meta.get(k, {}).get('value', '')).strip()[:80]
        y = re.search(r'1[5-9]\d\d', strip('DateTimeOriginal'))
        ImageOps.grayscale(Image.open(io.BytesIO(get(ii['thumburl']))).convert('RGB')).save(f'collect/{key}.jpg', quality=78)
        C[key] = dict(base, title=p['title'], url=ii['descriptionurl'], year=int(y.group()) if y else None, artist=strip('Artist'), license=strip('LicenseShortName'))
    print(key, label, '→', C[key]['title'][5:60])
# 마땅한 사진 없음 → 비워 둠
for k in ['a008', 'a021', 'a033', 'a040', 'a054', 'a093', 'a119', 'a123', 'a136', 'a147', 'a152']:
    if C.pop(k, None) and os.path.exists(f'collect/{k}.jpg'): os.remove(f'collect/{k}.jpg')
json.dump(C, open('collect.json', 'w'), ensure_ascii=False, indent=1)
print(len(C), 'in collect')
