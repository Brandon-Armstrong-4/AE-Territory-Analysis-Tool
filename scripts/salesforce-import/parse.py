"""Parse the plain-text SOQL result format saved by the Salesforce connector.

Each record starts with a line like "12. Account (001...)" and continues with
"  Field: value" lines. Returns a list of dicts with true/false/null converted.
"""
import re


def parse(path):
    recs, cur = [], None
    with open(path, encoding='utf-8') as fh:
        for line in fh:
            line = line.rstrip('\n')
            if re.match(r'^\d+\. (Account|AggregateResult) ', line):
                cur = {}
                recs.append(cur)
                continue
            m = re.match(r'^  ([A-Za-z_][\w.]*): ?(.*)$', line)
            if m and cur is not None:
                k, v = m.group(1), m.group(2)
                v = None if v == 'null' else True if v == 'true' else False if v == 'false' else v
                cur[k] = v
    return recs
