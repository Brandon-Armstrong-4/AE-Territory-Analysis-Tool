# Data import

Salesforce is the source of truth for **which agencies have a parks and recreation function**. The Studio does not re-check that on the web; to change the list, refresh the import.

## Selection rule

```
Account where
  Recreation_ICP__c in ('Yes', 'Yes - Not Suitable for Outbound')
  and BillingState in ('Texas', 'Pennsylvania', 'Rhode Island', 'Connecticut', 'South Dakota')
  and Population__c between 5,000 and 75,000
```

Billing states are stored as full names in Salesforce. Accounts with no population are left out (the population range in Settings can still be widened later, but only for agencies that are in the import).

## Cleanup

1. **Not a recreation government, removed.** State government accounts, Rhode Island county accounts (Rhode Island has no county government), and special districts that are not recreation agencies (soil and water conservation, parking, water, lake associations).
2. **Duplicates, merged.** Accounts sharing a `ParentId`, or in the same state with the same base name and population within 2%. The government account is kept over "- Parks and Recreation" or "- Rec" accounts, and the merged Salesforce ids are kept on the record.
3. **Existing REC customers, set aside.** `CivicRec__c` on the account, its parent, a related "- Rec" account, or a REC account with the same name and population.
4. **Not suitable for outbound, set aside.** "Yes - Not Suitable for Outbound" without REC evidence is set aside under its own reason, not counted as a customer.
5. **Customer status.** Any CivicPlus product flag on the account or its parent makes it an existing customer (most products sit on the parent; the child's `Type` is often "Non-Customer"). Products are listed by name.

## Enrichment

- `contactCount` from contacts on the parent account (`contactKnown` when there is at least one).
- Coordinates from the billing latitude and longitude.
- `neighbors`: up to 6 dataset agencies within 20 miles.
- `nearby.recCustomer`: the nearest REC customer within 25 miles (feeds the Nearby reference factor).
- Two evidence entries per record pointing at the Salesforce source.

## Outputs

| Document | Contents |
|---|---|
| `states/{ST}/base/c{n}` | `{state, source: "salesforce", importedOn, chunk, rows[]}`, chunks under 180 KB |
| `summary/{ST}` | `import` counts: flagged, no population, under 5k, over 75k, in range, not government, duplicates removed, dataset, REC customers, not suitable for outbound, candidates, cross-sell, new logo |
| `runs/sf-import-{date}` | Run log |

The chunk script asserts `inRange − notGovernment − duplicatesRemoved = dataset` for every state before writing.

## Refreshing

Run the queries and scripts in [scripts/salesforce-import](../scripts/salesforce-import/README.md), then replace the `states/{ST}/base/*` and `summary/{ST}` documents. Scan results in `states/{ST}/agencies/*` and rep decisions are keyed by agency id and survive a refresh, as long as the agency's name and type are unchanged (ids are `{state}-{type}-{slug of name}`).

A refresh is worth doing when the Recreation ICP flag is updated in bulk, or once a quarter to pick up new customers.
