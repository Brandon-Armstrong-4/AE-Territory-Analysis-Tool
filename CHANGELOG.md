# Changelog

All dates are 2026. Versions match the published Studio page.

## Version 4 · November 17

- Replaced the territory header ("Which agencies are in the territory and where is each one") with **Headlines**: a short list of the agencies most worth pursuing, written from scan and deep-scan findings.
- Headlines are state-specific on each state tab; **All Five** shows the top headlines from each state.
- Headline weighting favors software on an agenda and vendor changes, then leadership changes, capital projects and bonds, then budget workshops, grants and accessibility pressure. Friction (PDF or phone registration, no online payment) and an open seed window add to the angle.
- Capitalized "All Five".

## Version 3 · November 17

- **Scanning.** General scan per state (never all five at once), batches of 25, with a state sweep for software bids, park-grant awards and recreation-director openings. Deep scan per agency in six steps: budget, agendas, staff, registration, news, summary.
- **Scan queue.** Buttons write `scanJobs/{id}` and fire the scanner scheduled task; the page follows progress live and can stop a job.
- **Radar.** Active radar widget with a clockwise sweep and real agency blips, a progress bar with percentage and a per-agency log.
- **Ask the Studio.** Chat panel that answers from Studio data and can open agencies, filter lists and queue scans.
- **Charts.** Proportional funnel, Readiness strip with tier lines, registration landscape by state, 12-month seed-window timeline.
- **Theme.** Dark radar theme in red with CivicPlus-style accents; colors are tokens at the top of the stylesheet.
- **Rules.** Competitors are never disqualified (the contract-locked and signed-with-competitor set-asides were removed). Interim-director findings count as an ordinary leadership change. New tier states: Tier 1 needs deep scan, Tier 1 pending check. "Near the line" preset.
- Scanner runbook tightened after the first live run: real data only, `none_found` only when the full recreation page loaded and showed no registration route.

## Version 2 · November 17

- Replaced demo data with the live Salesforce dataset: Recreation ICP accounts in the five states, population 5,000–75,000, deduplicated, non-recreation governments removed.
- Existing REC customers and accounts marked not suitable for outbound are set aside automatically.
- Base records carry customer status and products, contact counts, coordinates, neighbors within 20 miles and the nearest REC customer within 25 miles.
- Import counts per state shown in the funnel and Settings.

## Version 1 · November 17

- First build from the Targeting Studio build prompt, the Targeting Studio brief and the Budget and Season Calendar.
- Readiness score (Fit, Friction, Timing, Access), tiers, relative Priority, population bands, budget windows per state with sources, registration seasons and pilot-ask months.
- Agency drawer with factor-by-factor evidence, set-aside reasons with re-open conditions, rep verification and notes.
- Presets, weights editor with saved weight versions, CSV export, phone layout.
