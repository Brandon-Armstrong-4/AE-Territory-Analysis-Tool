# Scanning

Scans are split in two so the territory can be covered quickly and the shortlist can be researched properly.

| | General scan | Deep scan |
|---|---|---|
| Scope | One state at a time (never all five) | One agency |
| Batch | 25 agencies (Settings, 5–100) | 6 steps |
| Effort | About 30 seconds per agency: 1 search, up to 2 page reads | Up to about 10 page reads |
| Goal | Surface-level signals to sort the state | Verify the facts behind a Tier 1 or near-the-line agency |
| Sets | `scanLevel: "general"`, `stage: "scanned"` | `scanLevel: "deep"`, `deepScannedOn`, `deepSummary` |

## What each scan captures

### General scan

| Field | Values | Why it qualifies |
|---|---|---|
| `friction.registration` | `online_modern`, `online_legacy`, `pdf_form`, `phone_email`, `none_found`, `unknown` | The core pain REC solves. `none_found` only when the full recreation page loaded and showed no registration route. |
| `friction.platformDetected` | ActiveNet, RecDesk, Rec1, MyRec, CommunityPass, PerfectMind, Amilia, RecTrac, DaySmart, SportsEngine, Sawyer, CivicRec | Read from the registration link's domain. CivicRec marks the agency as an existing REC customer. |
| `friction.competitor` | true / false | Information only. **Never a set-aside reason.** |
| `friction.incumbentQuality` | `legacy`, `unsupported`, `fragmented`, `adequate`, `none`, `unknown` | Fragmented includes generic form tools (Jotform, Google Forms, Wufoo). |
| `friction.payment` | `online`, `partial`, `none`, `unknown` | Cash or check only is a strong friction signal. |
| `friction.booking` | `online`, `form`, `phone`, `none_found`, `unknown` | Facility and pavilion rentals. |
| `friction.accessibility` | `suspected` when registration depends on a PDF, `none` with a modern platform | Upgraded to `evidenced` only by a deep scan. |
| `friction.programBreadth` | camps, aquatics, leagues, classes, rentals, senior, special events | Only programs seen on pages read. |
| `contacts` | role, name, level (`director`, `rec_staff`, `generic`), source URL | Only recreation staff named on the pages read. |

**State sweep.** Before the first agency, if the state has not been swept in 7 days, up to 6 searches over the last 12 months for recreation software RFPs and bids, park and recreation grant awards, and recreation director job openings. Findings are matched to agencies by exact government name and stored in `sweeps/{ST}`.

**Batch order.** Unscanned, not set aside, largest population band first, then existing customers, then agencies in the seed window, then population.

### Deep scan

| Step | Looks for | Writes |
|---|---|---|
| 1 Budget | Adopted budget or budget calendar | `budget` with `basis: "verified"`, parks and recreation operating budget, software line items |
| 2 Agendas | Council and park board agendas and minutes, last 12 months | `agenda_mention`, `vendor_change`, `budget_workshop` signals; `incumbent` contract approval (information only) |
| 3 Staff | Staff directory | `contacts` with levels; `recFunction.capacity` |
| 4 Registration | Confirms registration, payment and booking | `friction.accessibility = "evidenced"` for image-only or non-fillable PDF forms |
| 5 News | Last 12 months | `capital_project`, `bond_or_levy`, `grant`, `leadership_change` (interim included, no extra weight), `accessibility_pressure` |
| 6 Summary | | `deepSummary`: 2–3 sentences on why now and any blockers |

## Job lifecycle

```js
scanJobs/{id} = {
  id: "general-ri-m3k9x2",          // or "deep-pa-..."
  kind: "general" | "deep",
  state: "RI",
  agencyIds: [...],
  total, done,                       // drives the progress bar
  sweep: true,                       // general only, adds one step
  progress: { _sweep: "done", "<agencyId>": "done" | "blocked" },
  steps: [{ key: "budget", label: "Budget", status: "pending" | "done" }],   // deep only
  current: { id, name, step },
  status: "queued" | "running" | "done" | "stopped",
  requestedOn, startedAt, finishedAt, stopRequested, note
}
```

1. The page writes the job as `queued` and calls `fire_trigger` on the scanner task.
2. The task claims it with a version-pinned update (`running`); a second run that loses the race skips it.
3. After each agency or step it writes results to `states/{ST}/agencies/{id}` and updates `done`, `current` and `progress`. The page's radar, progress bar and log follow along live.
4. Stop sets `stopRequested`; the task checks before each agency or step and ends as `stopped`.
5. On finish the task writes `runs/{id}` and updates `summary/{ST}.lastRunOn`.

## Real data only

- Every value comes from a public page read during that run, with its URL in `evidence`.
- Anything not seen, blocked or only rendered by scripts is `unknown`, with the agency marked `blocked` in progress.
- Excerpts are 12 words or fewer; everything else is paraphrased. No LinkedIn.
- Signals are only events from the last 18 months, de-duplicated by source URL, and stay `verified: false` until the rep checks them.

The full instructions the task follows are in [scanner/runbook.md](../scanner/runbook.md).
