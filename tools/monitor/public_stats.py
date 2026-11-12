"""Log the channel's public numbers: subscribers and each video's views.

Reads only the public channel page (what anyone sees at youtube.com/@GreatLakesFiles/videos)
and appends one row per video to tracker/public-stats.csv. Watch time, click rate and
retention are private and only visible in YouTube Studio.

    python3 tools/monitor/public_stats.py            # log a row and print the change since last time
    python3 tools/monitor/public_stats.py --dry-run  # print only
"""
import csv, datetime, json, os, re, subprocess, sys

HANDLE = os.environ.get('HANDLE', '@GreatLakesFiles')
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOG = os.path.join(ROOT, 'tracker', 'public-stats.csv')
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
FIELDS = ['time_utc', 'subscribers', 'video_id', 'title', 'views', 'age']


def fetch(url):
    r = subprocess.run(['curl', '-sS', '-L', '-m', '40', '-H', 'Accept-Language: en-US,en;q=0.9',
                        '-H', 'Cookie: SOCS=CAI; PREF=hl=en&gl=US', '-A', UA, url], capture_output=True)
    return r.stdout.decode('utf8', 'replace')


def initial(html):
    m = re.search(r'var ytInitialData = (\{.*?\});</script>', html, re.S)
    return json.loads(m.group(1)) if m else None


def walk(o, key, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key: out.append(v)
            walk(v, key, out)
    elif isinstance(o, list):
        for v in o: walk(v, key, out)


def txt(o):
    if not o: return ''
    if 'simpleText' in o: return o['simpleText']
    if 'runs' in o: return ''.join(r.get('text', '') for r in o['runs'])
    return o.get('content', '')


def number(s):
    """'1.2K views' -> 1200, 'No views' -> 0, '15 views' -> 15."""
    s = s.replace(',', '').replace('\xa0', ' ')
    m = re.search(r'([\d.]+)\s*([KMB]?)', s)
    if not m: return 0
    return int(round(float(m.group(1)) * {'': 1, 'K': 1e3, 'M': 1e6, 'B': 1e9}[m.group(2)]))


def read():
    d = initial(fetch('https://www.youtube.com/%s/videos' % HANDLE))
    if not d: sys.exit('Could not read the channel page.')
    head = []
    for h in ('pageHeaderViewModel', 'c4TabbedHeaderRenderer'): walk(d, h, head)
    parts = []
    for h in head[:1]:
        mp = []; walk(h, 'metadataParts', mp)
        parts += [txt(p.get('text', {})) for m in mp for p in m]
    subs = next((p for p in parts if 'subscriber' in p), '')
    videos = []
    lk = []; walk(d, 'lockupViewModel', lk)
    for l in lk:
        ti = []; walk(l, 'lockupMetadataViewModel', ti)
        mp = []; walk(l, 'metadataParts', mp)
        ps = [txt(p.get('text', {})).replace('\xa0', ' ') for m in mp for p in m]
        views = next((p for p in ps if 'view' in p), next((p for p in ps if p and 'ago' not in p), ''))
        age = next((p for p in ps if 'ago' in p), '')
        videos.append(dict(video_id=l.get('contentId'), title=txt(ti[0].get('title', {})) if ti else '',
                           views=number(views), age=age))
    return number(subs) if subs and 'No subscriber' not in subs else 0, videos


def last_rows():
    if not os.path.exists(LOG): return {}
    out = {}
    for r in csv.DictReader(open(LOG)): out[r['video_id']] = r
    return out


def main():
    now = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0)
    subs, videos = read()
    prev = last_rows()
    print('%s  subscribers: %d' % (now.strftime('%Y-%m-%d %H:%M UTC'), subs))
    rows = []
    for v in videos:
        line = '  %-72s %7d views  (%s)' % (v['title'][:72], v['views'], v['age'])
        p = prev.get(v['video_id'])
        if p:
            hours = (now - datetime.datetime.fromisoformat(p['time_utc'])).total_seconds() / 3600
            gained = v['views'] - int(p['views'])
            if hours > 0: line += '  +%d in %.1f h = %.0f per hour' % (gained, hours, gained / hours)
        print(line)
        rows.append(dict(time_utc=now.isoformat(), subscribers=subs, **v))
    if '--dry-run' in sys.argv: return
    new = not os.path.exists(LOG)
    with open(LOG, 'a', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new: w.writeheader()
        w.writerows(rows)


if __name__ == '__main__':
    main()
