# pick.tsv 의 지정 제목으로 사진 교체/추가 (제목 앞 ? = 검색 1순위)
import csv, json, re, io, time, urllib.request, urllib.parse
from PIL import Image, ImageOps
UA = {'User-Agent': 'frankenstein-places-mockup/0.1 (student design project)'}
def get(url):
    for i in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=40).read()
        except Exception as e: err = e; time.sleep(30 * (i + 1))
    raise err
rows = list(csv.reader(open('places.tsv'), delimiter='\t'))
out = json.load(open('credits.json'))
for key, title in csv.reader(open('pick.tsv'), delimiter='\t'):
    time.sleep(5)
    q = {'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'iiprop': 'url|extmetadata', 'iiurlwidth': 960}
    if title.startswith('?'): q.update(generator='search', gsrnamespace=6, gsrsearch=title[1:], gsrlimit=1)
    else: q['titles'] = 'File:' + title
    p = next(iter(json.loads(get('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q)))['query']['pages'].values()))
    if 'imageinfo' not in p: print('MISSING', key, title); continue
    ii = p['imageinfo'][0]; meta = ii.get('extmetadata', {})
    strip = lambda k: re.sub('<[^>]+>', '', meta.get(k, {}).get('value', '')).strip()[:80]
    y = re.search(r'1[5-9]\d\d', strip('DateTimeOriginal'))
    ImageOps.grayscale(Image.open(io.BytesIO(get(ii['thumburl']))).convert('RGB')).save(f'photos/{key}.jpg', quality=78)
    page, term, en, _ = rows[int(key.split('-')[1])]
    out[key] = dict(page=int(page), term=term, en=en, title=p['title'], url=ii['descriptionurl'],
                    year=int(y.group()) if y else None, artist=strip('Artist'), license=strip('LicenseShortName'))
    print(key, term, '→', p['title'][5:70], out[key]['year'])
    json.dump(out, open('credits.json', 'w'), ensure_ascii=False, indent=1)
