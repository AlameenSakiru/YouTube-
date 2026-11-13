"""Read a research source page as plain text, for fact-checking scripts.

Only fetches https pages on the research sites listed in ALLOWED_HOSTS (the sites
approved for this project). Prints the page's readable text to stdout; writes nothing.

    python3 -I tools/research/fetch_source.py URL [URL ...]
    python3 -I tools/research/fetch_source.py --grep WORD URL   # only paragraphs containing WORD
"""
import html, re, subprocess, sys, tempfile, urllib.parse

ALLOWED_HOSTS = {
    # history and archives
    'www.buffalohistorygazette.net', 'maritimehistoryofthegreatlakes.ca', 'archive.org',
    'chroniclingamerica.loc.gov', 'buffaloah.com', 'drloihjournal.blogspot.com',
    'chicagohistorytoday.wordpress.com', 'www.vintagechicagopostcards.com', 'en.wikipedia.org',
    # government and science
    'www.weather.gov', 'www.glerl.noaa.gov', 'oceanservice.noaa.gov', 'mrcc.purdue.edu',
    'www.seagrant.sunysb.edu', 'ijc.org',
    # news
    'toledoblade.com',
}
UA = 'GreatLakesFilesResearch/1.0 (documentary fact-checking)'


def fetch(url):
    u = urllib.parse.urlsplit(url)
    if u.scheme != 'https' or u.hostname not in ALLOWED_HOSTS:
        sys.exit('Not an approved research site: %s' % url)
    r = subprocess.run(['curl', '-sS', '-L', '--proto', '=https', '--proto-redir', '=https', '-m', '60',
                        '--max-filesize', '30000000', '-A', UA, url], capture_output=True)
    if r.returncode:
        sys.exit('Could not fetch %s: %s' % (url, r.stderr.decode(errors='replace').strip()))
    return r.stdout


def to_text(data):
    if data[:5] == b'%PDF-':
        with tempfile.NamedTemporaryFile(suffix='.pdf') as f:
            f.write(data); f.flush()
            return subprocess.run(['pdftotext', '-layout', f.name, '-'], capture_output=True).stdout.decode(errors='replace')
    t = data.decode('utf-8', errors='replace')
    t = re.sub(r'(?is)<(script|style|noscript|svg)\b.*?</\1>', ' ', t)
    t = re.sub(r'(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr|blockquote)>', '\n', t)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    lines = [re.sub(r'[ \t ]+', ' ', l).strip() for l in t.splitlines()]
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(lines)).strip()


def main():
    args = sys.argv[1:]
    word = None
    if args[:1] == ['--grep']:
        word, args = args[1].lower(), args[2:]
    if not args:
        sys.exit(__doc__)
    for url in args:
        text = to_text(fetch(url))
        print('=' * 20, url)
        if word:
            text = '\n\n'.join(p for p in re.split(r'\n\s*\n', text) if word in p.lower())
        print(text)


if __name__ == '__main__':
    main()
