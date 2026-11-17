"""Read-only public Website evidence and exact static artifact diff, no SFTP."""
import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import zipfile

PRODUCTION = 'https://competencehub.donner-partner.de'
PREVIEW = 'https://dp-manuel.github.io/CompetenceHub'
BASELINE_SHA = 'd80bd25977dfabf5d3ecf9892ed1747ff18b69a485d6b631ea0a0a459226dd5f'


def sha(raw): return hashlib.sha256(raw).hexdigest()


def archive(path, expected=None):
    raw = path.read_bytes()
    if expected is not None and sha(raw) != expected: raise ValueError('Bound archive changed')
    with zipfile.ZipFile(path) as source:
        result = {}
        for item in source.infolist():
            name = PurePosixPath(item.filename)
            if name.is_absolute() or '..' in name.parts or item.is_dir(): raise ValueError('Invalid release entry')
            if item.filename in result: raise ValueError('Duplicate release entry')
            result[item.filename] = source.read(item)
        return result


class Metadata(HTMLParser):
    def __init__(self):
        super().__init__(); self.meta = {}; self.canonical = []; self.links = []; self.text = []

    def handle_starttag(self, tag, values):
        attrs = dict(values)
        if tag == 'meta': self.meta[attrs.get('name') or attrs.get('property')] = attrs.get('content')
        if tag == 'link' and attrs.get('rel') == 'canonical': self.canonical.append(attrs.get('href'))
        if tag == 'a' and attrs.get('href'): self.links.append(attrs['href'])

    def handle_data(self, data): self.text.append(data)


def fetch(url):
    request = Request(url, headers={'Cache-Control': 'no-cache', 'User-Agent': 'CompetenceHub-Release-Audit/20261117'})
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read(12 * 1024 * 1024 + 1)
            if len(raw) > 12 * 1024 * 1024: raise ValueError('Public resource exceeds bound')
            return {'status': response.status, 'url': response.url, 'sha256': sha(raw)}, raw
    except HTTPError as error: return {'status': error.code, 'url': url}, b''
    except (URLError, TimeoutError) as error: return {'status': 'UNAVAILABLE', 'error': type(error).__name__, 'url': url}, b''


def audit(baseline):
    live = {}
    for name, expected in baseline.items():
        if name == '.htaccess':
            live[name] = {'status': 'NOT_HTTP_PUBLIC', 'fresh_sftp_verification_required': True}; continue
        record, raw = fetch(PRODUCTION + '/' + name)
        record['baseline_match'] = record.get('status') == 200 and raw == expected
        live[name] = record
    preview = {}
    for name in ('index.html', 'coaches/index.html', 'coaches/guelcan-elmas-brandes/index.html',
                 'coaches/susanne-klemm/index.html', 'leistungen/index.html', 'kontakt/index.html',
                 'kalender/index.html', 'datenschutz/index.html', 'impressum/index.html', 'robots.txt', 'sitemap.xml'):
        record, raw = fetch(PREVIEW + '/' + name)
        if name.endswith('.html') and record['status'] == 200:
            parsed = Metadata(); parsed.feed(raw.decode('utf8'))
            record.update(robots=parsed.meta.get('robots'), canonicals=parsed.canonical,
                          has_coach_filter='id="finder-coach"' in raw.decode('utf8'),
                          mailto=sum(h.startswith('mailto:') for h in parsed.links),
                          telephone=sum(h.startswith('tel:') for h in parsed.links))
        preview[name] = record
    return {'checked_at_utc': datetime.now(timezone.utc).isoformat(),
            'production': live, 'preview': preview, 'production_writes': False}


def difference(baseline, candidate):
    groups = {key: [] for key in ('added', 'changed', 'removed', 'unchanged')}
    for name in sorted(baseline.keys() | candidate.keys()):
        old, new = baseline.get(name), candidate.get(name)
        state = 'added' if old is None else 'removed' if new is None else 'unchanged' if old == new else 'changed'
        groups[state].append({'path': name, 'before_sha256': sha(old) if old is not None else None,
                              'after_sha256': sha(new) if new is not None else None})
    return groups


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--candidate', type=Path); parser.add_argument('--candidate-sha256')
    parser.add_argument('--live', action='store_true'); parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); original = archive(args.baseline, BASELINE_SHA)
    result = {'baseline_sha256': BASELINE_SHA, 'baseline_files': len(original)}
    if args.live: result.update(audit(original))
    if args.candidate:
        if not args.candidate_sha256: parser.error('--candidate requires --candidate-sha256')
        result['candidate_sha256'] = args.candidate_sha256
        result['difference'] = difference(original, archive(args.candidate, args.candidate_sha256))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf8') as stream: json.dump(result, stream, ensure_ascii=True, indent=2)
    print('PUBLIC_RELEASE_EVIDENCE=' + str(args.output))
