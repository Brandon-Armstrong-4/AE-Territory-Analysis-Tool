"""Build the Targeting Studio agency dataset from Salesforce exports.

Reads saved SOQL results (see README.md for the queries) from --input and writes
agencies.json and stats.json to --out. CRM exports and outputs never belong in git.

    python3 build.py --input input --out out --today 2026-11-17
"""
import argparse, glob, json, math, os, re, collections
from parse import parse

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument('--input', default='input', help='folder with icp.txt, rec.txt, contacts.txt and products_*.txt')
ap.add_argument('--out', default='out', help='output folder')
ap.add_argument('--today', required=True, help='capture date written on evidence, YYYY-MM-DD')
args = ap.parse_args()
os.makedirs(args.out, exist_ok=True)
TODAY = args.today
ST = {'Texas':'TX','Pennsylvania':'PA','Rhode Island':'RI','Connecticut':'CT','South Dakota':'SD'}
icp = parse(os.path.join(args.input, 'icp.txt'))
rec = parse(os.path.join(args.input, 'rec.txt'))
con = parse(os.path.join(args.input, 'contacts.txt'))
prod = []
for f in sorted(glob.glob(os.path.join(args.input, 'products_*.txt'))):
    prod += parse(f)
P = {p['Id']: p for p in prod}
print('flagged in range', len(icp), '| REC accounts', len(rec), '| contact groups', len(con), '| product accounts', len(P))
contacts = {c['AccountId']: int(c['n']) for c in con}
PROD = [('CivicClerk__c','CivicClerk (AMM)'),('CivicEngage__c','Websites'),('CivicHR__c','CivicHR'),('CivicReady__c','CivicReady'),('CivicCMS__c','CivicCMS'),
        ('CivicOptimize__c','CivicOptimize'),('Product_SeeClickFix__c','SeeClickFix'),('ArchiveSocial__c','ArchiveSocial'),('NextRequest__c','NextRequest'),
        ('Accessibility__c','Web Accessibility'),('PDF_Accessibility__c','PDF Accessibility'),('CivicGov__c','CivicGov'),('Code_and_Supp__c','Municode Code'),
        ('Asset_Management__c','Asset Management'),('Utility_Billing__c','Utility Billing')]
def num(v):
    try: return float(v)
    except: return None
def base_name(n):
    s = n.lower()
    s = re.sub(r',\s*(tx|pa|ri|ct|sd|texas|pennsylvania|rhode island|connecticut|south dakota)\s*$', '', s)
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'\s*[-–]\s*(parks?\s*(and|&)\s*rec(reation)?|rec(reation)?|parks?)(\s+(department|dept\.?))?\s*$', '', s)
    s = re.sub(r'\b(parks?\s*(and|&)\s*rec(reation)?\s*(department|dept\.?)?)\b', '', s)
    s = re.sub(r'^(the\s+)?(city|town|township|borough|village|municipality)\s+of\s+', '', s)
    s = re.sub(r'\s+(city|town|township|borough|village)$', '', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()
def gtype(r):
    n = r['Name']
    m = re.match(r'^(the\s+)?(city|town|township|borough|village)\s+of\b', n, re.I)
    if m: return m.group(2).lower()
    if re.match(r'^municipality of\b', n, re.I): return 'city'
    if re.search(r'school district', n, re.I): return 'school_district'
    if r.get('Industry') == 'Special District' or re.search(r'\b(district|authority|commission|association)\b', n, re.I): return 'special_district'
    if re.search(r'\bcounty\b', n, re.I): return 'county'
    for t in ['township','borough','village','town','city']:
        if re.search(r'\b'+t+r'\b', n, re.I): return t
    return 'other'
def rec_district(n): return bool(re.search(r'park|recreation|open space', n, re.I))
def is_rec_named(n): return bool(re.search(r'(parks?\s*(and|&)\s*rec|\brec(reation)?\b)', n, re.I))
def miles(a, b):
    la1, lo1, la2, lo2 = map(math.radians, [a[0], a[1], b[0], b[1]])
    h = math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin((lo2-lo1)/2)**2
    return 3958.8 * 2 * math.asin(math.sqrt(h))

stats = collections.defaultdict(lambda: collections.Counter())
# 1. drop non-governments
rows = []
for r in icp:
    st = ST[r['BillingState']]
    t = gtype(r)
    r['_st'] = st; r['_type'] = t; r['_base'] = base_name(r['Name']); r['_pop'] = num(r.get('Population__c'))
    if st in ('RI','CT') and t == 'county':
        stats[st]['no_county_government'] += 1; continue
    if r.get('Industry') == 'State Government':
        stats[st]['state_agency'] += 1; continue
    if t == 'special_district' and not rec_district(r['Name']) and not re.match(r'^(city|town|township|borough|village)\s+of\b', r['Name'], re.I):
        stats[st]['not_recreation_district'] += 1; continue
    rows.append(r)
# 2. dedupe: union-find on shared parent, or same state+base name with population within 2%
par = {r['Id']: r['Id'] for r in rows}
def find(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
def union(a, b): par[find(a)] = find(b)
byparent = collections.defaultdict(list)
for r in rows: byparent[r['ParentId']].append(r)
for g in byparent.values():
    for r in g[1:]: union(r['Id'], g[0]['Id'])
byname = collections.defaultdict(list)
for r in rows: byname[(r['_st'], r['_base'])].append(r)
for g in byname.values():
    for i in range(len(g)):
        for j in range(i+1, len(g)):
            a, b = g[i], g[j]
            if a['_pop'] and b['_pop'] and abs(a['_pop'] - b['_pop']) <= 0.02 * max(a['_pop'], b['_pop']): union(a['Id'], b['Id'])
groups = collections.defaultdict(list)
for r in rows: groups[find(r['Id'])].append(r)
# REC signals
recByParent = collections.defaultdict(list); recById = {}; recByName = collections.defaultdict(list)
for x in rec:
    st = ST.get(x.get('BillingState'))
    if not st: continue
    x['_st'] = st; x['_base'] = base_name(x['Name']); x['_pop'] = num(x.get('Population__c'))
    recById[x['Id']] = x
    if x.get('ParentId'): recByParent[x['ParentId']].append(x)
    recByName[(st, x['_base'])].append(x)

agencies = []; used_ids = set()
for gid, g in groups.items():
    st = g[0]['_st']
    if len(g) > 1: stats[st]['duplicates_removed'] += len(g) - 1
    g.sort(key=lambda r: (is_rec_named(r['Name']), r.get('Type') != 'Customer', not r.get('Website'), r['Name']))
    p = g[0]
    ids = {r['Id'] for r in g}; pids = {r['ParentId'] for r in g if r.get('ParentId')}
    # products from self, group, parents
    prods = set(); rec_evidence = []
    for acc in [*g, *[P[x] for x in pids if x in P], *[P[r['Id']] for r in g if r['Id'] in P]]:
        for f, lab in PROD:
            if acc.get(f) is True: prods.add(lab)
        if acc.get('CivicRec__c') is True: rec_evidence.append(f"Rec product on {acc.get('Name')}")
    for r in g:
        if r.get('Recreation_ICP__c') == 'Yes - Not Suitable for Outbound': rec_evidence.append('Recreation ICP: Yes - Not Suitable for Outbound')
    for x in [*[y for pid in pids for y in recByParent.get(pid, [])], *[recById[x] for x in pids if x in recById]]:
        if x['Id'] not in ids: rec_evidence.append(f"Related REC account: {x['Name']}")
    for x in recByName.get((st, p['_base']), []):
        if x['Id'] not in ids and x['_pop'] and p['_pop'] and abs(x['_pop'] - p['_pop']) <= 0.02 * p['_pop']: rec_evidence.append(f"Matching REC account: {x['Name']}")
    nso_only = bool(rec_evidence) and all(e.startswith('Recreation ICP') for e in rec_evidence)
    owns = bool(rec_evidence) and not nso_only
    typ = p.get('Type')
    existing = typ == 'Customer' or bool(prods)
    if owns: prods.add('REC')
    ccount = sum(contacts.get(x, 0) for x in pids | ids)
    rel = {'status': 'existing' if existing else 'new_logo', 'products': sorted(prods), 'ownsREC': owns, 'source': 'salesforce',
           'contactKnown': ccount > 0, 'contactCount': ccount, 'sfType': typ}
    if typ == 'Ex-Customer': rel['exCustomer'] = True; rel['priorConversation'] = True
    if owns: rel['recEvidence'] = sorted(set(e for e in rec_evidence if not e.startswith('Recreation ICP')))[:4]
    if nso_only: rel['notSuitableOutbound'] = True
    t = p['_type']
    name = re.sub(r',\s*(TX|PA|RI|CT|SD)\s*$', '', p['Name']).strip()
    if t != 'special_district': name = re.sub(r'\s*[-–]\s*(parks?\s*(and|&)\s*rec(reation)?|recreation)(\s+(department|dept\.?))?\s*$', '', name, flags=re.I).strip()
    slug = re.sub(r'[^a-z0-9]+', '-', p['_base']).strip('-') or p['Id'].lower()
    aid = f"{st.lower()}-{t.replace('_','-')}-{slug}"
    if aid in used_ids: aid += '-' + p['Id'][-6:].lower()
    used_ids.add(aid)
    core = t == 'special_district' and bool(re.search(r'park|recreation', p['Name'], re.I))
    lat, lon = num(p.get('BillingLatitude')), num(p.get('BillingLongitude'))
    a = {'id': aid, 'name': name, 'state': st, 'type': t, 'population': int(p['_pop']) if p['_pop'] else None,
         'populationSource': 'Salesforce Account.Population__c', 'censusGovId': p.get('GEOID__c'),
         'website': p.get('Website'), 'recPageUrls': [], 'city': p.get('BillingCity'),
         'recFunction': {'status': 'yes', 'basis': 'Salesforce Recreation ICP', 'core': core},
         'relationship': rel, 'stage': 'swept', 'lastScannedOn': None,
         'salesforce': {'accountId': p['Id'], 'parentId': p.get('ParentId'), 'recreationICP': p.get('Recreation_ICP__c'), 'mergedAccounts': [r['Name'] for r in g[1:]]},
         'evidence': [{'field': 'recFunction', 'url': None, 'source': 'Salesforce', 'capturedOn': TODAY, 'excerpt': f"Recreation ICP = {p.get('Recreation_ICP__c')} on {p['Name']}", 'confidence': 'medium', 'verified': False},
                      {'field': 'population', 'url': None, 'source': 'Salesforce', 'capturedOn': TODAY, 'excerpt': f"Population__c = {int(p['_pop']) if p['_pop'] else 'blank'}", 'confidence': 'medium', 'verified': False}],
         'signals': [], 'contacts': [], 'friction': {}, 'budget': None, 'importedOn': TODAY}
    if lat is not None and lon is not None: a['geo'] = [round(lat, 5), round(lon, 5)]
    agencies.append(a)
    stats[st]['dataset'] += 1
    if owns: stats[st]['rec_customers'] += 1
    elif nso_only: stats[st]['not_suitable_outbound'] += 1
    else:
        stats[st]['candidates'] += 1
        stats[st]['candidate_existing' if existing else 'candidate_new_logo'] += 1

# neighbors (same state, within 20 miles, nearest 6) and nearest REC customer (any population) within 25 miles
recpts = [(x, (num(x.get('BillingLatitude')), num(x.get('BillingLongitude')))) for x in rec if num(x.get('BillingLatitude')) is not None]
for a in agencies:
    if 'geo' not in a: a['neighbors'] = []; continue
    ds = sorted(((miles(a['geo'], b['geo']), b['id']) for b in agencies if b is not a and 'geo' in b and b['state'] == a['state']), key=lambda x: x[0])
    a['neighbors'] = [i for d, i in ds[:6] if d <= 20]
    best = None
    own = set([a['salesforce']['accountId'], a['salesforce']['parentId']])
    for x, pt in recpts:
        if x['Id'] in own or x.get('ParentId') in own: continue
        d = miles(a['geo'], pt)
        if d <= 25 and (best is None or d < best[0]): best = (d, x)
    if best:
        nm = re.sub(r'\s*[-–]\s*Rec\s*$', '', best[1]['Name']); nm = re.sub(r'\s*\(.*?\)', '', nm)
        a['nearby'] = {'recCustomer': {'name': nm.title() if nm.isupper() else nm, 'miles': round(best[0], 1)}}
json.dump(agencies, open(os.path.join(args.out, 'agencies.json'), 'w'))
json.dump({k: dict(v) for k, v in stats.items()}, open(os.path.join(args.out, 'stats.json'), 'w'), indent=1)
for st in ['TX','PA','CT','SD','RI']: print(st, dict(stats[st]))
print('total', len(agencies), 'types', collections.Counter(a['type'] for a in agencies).most_common())
