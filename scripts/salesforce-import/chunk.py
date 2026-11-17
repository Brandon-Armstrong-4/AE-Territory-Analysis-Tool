"""Split agencies.json into Studio database documents and per-state summaries.

    python3 chunk.py --out out --counts input/counts.json --today 2026-11-17

Writes out/base/{ST}-c{n}.json (states/{ST}/base/c{n}, about 180 KB each, under
the database's 256 KB document limit) and out/summary-{ST}.json (summary/{ST}).
counts.json holds the aggregate query results per state:
{"TX": {"flagged": 0, "noPopulation": 0, "under5k": 0, "inRange": 0}, ...}
"""
import argparse, json, os

ap = argparse.ArgumentParser()
ap.add_argument('--out', default='out')
ap.add_argument('--counts', required=True)
ap.add_argument('--today', required=True)
ap.add_argument('--max-bytes', type=int, default=180_000)
args = ap.parse_args()

agencies = json.load(open(os.path.join(args.out, 'agencies.json')))
stats = json.load(open(os.path.join(args.out, 'stats.json')))
counts = json.load(open(args.counts))
os.makedirs(os.path.join(args.out, 'base'), exist_ok=True)


def compact(o):
    if isinstance(o, dict):
        return {k: compact(v) for k, v in o.items() if v not in (None, [], {}, '')}
    if isinstance(o, list):
        return [compact(x) for x in o]
    return o


for st in ['TX', 'PA', 'CT', 'SD', 'RI']:
    rows = sorted((compact(a) for a in agencies if a['state'] == st), key=lambda a: a['id'])
    for r in rows:
        r.pop('state', None)
    chunks, cur, size = [], [], 0
    for r in rows:
        n = len(json.dumps(r, separators=(',', ':')))
        if cur and size + n > args.max_bytes:
            chunks.append(cur); cur, size = [], 0
        cur.append(r); size += n
    if cur:
        chunks.append(cur)
    for i, c in enumerate(chunks):
        doc = {'state': st, 'source': 'salesforce', 'importedOn': args.today, 'chunk': i, 'rows': c}
        with open(os.path.join(args.out, 'base', f'{st}-c{i}.json'), 'w') as fh:
            json.dump(doc, fh, separators=(',', ':'))
    s, c = stats.get(st, {}), counts[st]
    imp = {'flagged': c['flagged'], 'noPopulation': c['noPopulation'], 'under5k': c['under5k'],
           'over75k': c['flagged'] - c['noPopulation'] - c['under5k'] - c['inRange'], 'inRange': c['inRange'],
           'notGovernment': s.get('no_county_government', 0) + s.get('not_recreation_district', 0) + s.get('state_agency', 0),
           'duplicatesRemoved': s.get('duplicates_removed', 0), 'dataset': s.get('dataset', 0),
           'recCustomers': s.get('rec_customers', 0), 'notSuitableOutbound': s.get('not_suitable_outbound', 0),
           'candidates': s.get('candidates', 0), 'crossSell': s.get('candidate_existing', 0), 'newLogo': s.get('candidate_new_logo', 0)}
    assert imp['inRange'] - imp['notGovernment'] - imp['duplicatesRemoved'] == imp['dataset'], (st, imp)
    with open(os.path.join(args.out, f'summary-{st}.json'), 'w') as fh:
        json.dump({'state': st, 'source': 'Salesforce Recreation ICP', 'censusCount': None, 'lastRunOn': args.today, 'import': imp}, fh)
    print(st, len(rows), 'agencies in', len(chunks), 'documents')
