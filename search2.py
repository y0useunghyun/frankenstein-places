import csv, json, re, time, urllib.request, urllib.parse
UA = {'User-Agent': 'frankenstein-places-mockup/0.1 (student design project)'}
for key, q in csv.reader(open('redo2.tsv'), delimiter='\t'):
    time.sleep(5)
    api = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({'action': 'query', 'format': 'json', 'list': 'search', 'srnamespace': 6, 'srsearch': q + ' filetype:bitmap', 'srlimit': 8})
    for i in range(4):
        try: r = json.loads(urllib.request.urlopen(urllib.request.Request(api, headers=UA), timeout=30).read()); break
        except Exception: time.sleep(30)
    print('##', key, q)
    for h in r['query']['search']: print('   ', h['title'][5:110])
