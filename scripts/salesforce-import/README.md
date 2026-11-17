# Salesforce import

Rebuilds the Studio's base dataset from Salesforce. Python 3.9+, standard library only.

Exports and outputs contain CRM data: keep them in `input/` and `out/`, which are git-ignored. Never commit them.

## 1. Export

Run each query (read-only) and save the plain-text result, exactly as the Salesforce connector prints it (`N. Account (Id)` followed by `  Field: value` lines), into `input/`:

| File | Query |
|---|---|
| `icp.txt` | Recreation ICP accounts in range (below) |
| `rec.txt` | REC customer and not-suitable accounts in the five states |
| `contacts.txt` | Contact counts on the parent accounts |
| `products_1.txt`, `products_2.txt`, … | Accounts with any CivicPlus product, paged by `Id` (2,000 rows per page) |
| `counts.json` | Per-state counts for the funnel (below) |

```sql
-- icp.txt
SELECT Id, Name, BillingState, BillingCity, BillingPostalCode, BillingLatitude, BillingLongitude,
       Population__c, Website, Type, Industry, Client_Category__c, Recreation_ICP__c, GEOID__c, ParentId,
       CivicRec__c, CivicRec_ARR__c, CivicClerk__c, CivicEngage__c, CivicHR__c, CivicReady__c, CivicCMS__c,
       CivicOptimize__c, Product_SeeClickFix__c, ArchiveSocial__c, NextRequest__c, Accessibility__c,
       PDF_Accessibility__c, CivicGov__c, Code_and_Supp__c, Asset_Management__c, Utility_Billing__c
FROM Account
WHERE BillingState IN ('Texas','Pennsylvania','Rhode Island','Connecticut','South Dakota')
  AND Recreation_ICP__c IN ('Yes','Yes - Not Suitable for Outbound')
  AND Population__c >= 5000 AND Population__c <= 75000
ORDER BY BillingState, Name

-- rec.txt
SELECT Id, Name, BillingState, BillingCity, BillingLatitude, BillingLongitude, Population__c, Type,
       ParentId, CivicRec_ARR__c, Recreation_ICP__c
FROM Account
WHERE BillingState IN ('Texas','Pennsylvania','Rhode Island','Connecticut','South Dakota')
  AND (CivicRec__c = true OR Recreation_ICP__c = 'Yes - Not Suitable for Outbound')

-- contacts.txt
SELECT AccountId, COUNT(Id) n FROM Contact
WHERE AccountId IN (SELECT ParentId FROM Account
  WHERE BillingState IN ('Texas','Pennsylvania','Rhode Island','Connecticut','South Dakota')
    AND Recreation_ICP__c IN ('Yes','Yes - Not Suitable for Outbound')
    AND Population__c >= 5000 AND Population__c <= 75000)
GROUP BY AccountId

-- products_N.txt (add  AND Id > '<last Id of the previous page>'  for pages 2, 3, ...)
SELECT Id, Name, Type, CivicRec__c, CivicRec_ARR__c, CivicClerk__c, CivicEngage__c, CivicHR__c,
       CivicReady__c, CivicCMS__c, CivicOptimize__c, Product_SeeClickFix__c, ArchiveSocial__c,
       NextRequest__c, Accessibility__c, PDF_Accessibility__c, CivicGov__c, Code_and_Supp__c,
       Asset_Management__c, Utility_Billing__c
FROM Account
WHERE BillingState IN ('Texas','Pennsylvania','Rhode Island','Connecticut','South Dakota')
  AND (CivicRec__c = true OR CivicClerk__c = true OR CivicEngage__c = true OR CivicHR__c = true
    OR CivicReady__c = true OR CivicCMS__c = true OR CivicOptimize__c = true
    OR Product_SeeClickFix__c = true OR ArchiveSocial__c = true OR NextRequest__c = true
    OR Accessibility__c = true OR PDF_Accessibility__c = true OR CivicGov__c = true
    OR Code_and_Supp__c = true OR Asset_Management__c = true OR Utility_Billing__c = true)
ORDER BY Id
```

`counts.json` comes from four aggregate counts per state over the Recreation ICP accounts (all, no population, under 5,000, 5,000–75,000):

```json
{"TX": {"flagged": 0, "noPopulation": 0, "under5k": 0, "inRange": 0}, "PA": {...}, "CT": {...}, "SD": {...}, "RI": {...}}
```

## 2. Build

```bash
python3 build.py --input input --out out --today 2026-11-17
python3 chunk.py --out out --counts input/counts.json --today 2026-11-17
```

`build.py` applies the cleanup and enrichment in [docs/data-import.md](../../docs/data-import.md) and writes `out/agencies.json` and `out/stats.json`. `chunk.py` writes `out/base/{ST}-c{n}.json` and `out/summary-{ST}.json` and checks that the counts reconcile.

## 3. Load

Write each `out/base/{ST}-c{n}.json` to `states/{ST}/base/c{n}` and each `out/summary-{ST}.json` to `summary/{ST}` in the Studio's artifact database (for example, ask Claude to batch-write them with the ArtifactData tool). Delete any leftover higher-numbered chunks from a previous import. Then add a `runs/sf-import-{date}` entry.

## Files

| File | Purpose |
|---|---|
| `parse.py` | Parses the connector's plain-text SOQL output into dicts |
| `build.py` | Cleanup, dedupe, customer status, enrichment, record shape |
| `chunk.py` | Compacts records into database-sized documents and per-state summaries |
