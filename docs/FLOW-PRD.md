# ProstaCare India (THB) — Flow PRD

Companion to `FEATURE-PRD.md`. This document describes the **user journeys and step-by-step interaction flows** across the three-page app (`index.html` shell, `patient-file.html`, `population-analytics.html`). Flows are written as: **trigger → steps → state changes → end state**.

Legend: `[shell]` = index.html, `[file]` = patient-file.html, `[analytics]` = population-analytics.html. ⤳ = postMessage across the iframe boundary.

---

## 0. Navigation Map

```
                         ┌─────────────────────────────────────────┐
                         │            LOGIN (passphrase 1234)        │
                         └───────────────────┬─────────────────────┘
                                             ▼
                ┌──────────────────────  HOME [shell]  ──────────────────────┐
                │  hero · pulse circles · action cards · cohort health ·      │
                │  NCCN benchmarks · nudge trends · attention · recent        │
                └───┬───────────────┬────────────────────┬───────────────┬───┘
                    │               │                    │               │
         Patient List [shell]   Home Drilldown        Dashboard      Add Patient
                    │            modal [shell]        [analytics]      modal [shell]
                    │               │                    │               │
                    └──────┬────────┴─────────┬──────────┘               │
                           ▼                  ▼                          ▼
                    Patient File [file]  (drill → patient ⤳)     Team Notify preview
                    nudges · treatment · team · Rx · guidelines
```

All child pages render inside `#viewer-frame` in the shell. Children drive the shell via `demo-nav`, `privacy-toggle`, and `shell-route` messages; the shell restores deep state from URL params on reload.

---

## FLOW 1 — Login / App Entry  `[shell]`

**Trigger:** App loads unauthenticated.

1. Full-screen `#screen-login` overlay shown; header and main hidden.
2. User enters User ID + Password and clicks **Sign In** (or presses Enter).
3. **Decision:** Password `=== "1234"`?
   - **Yes →** button shows "Signing in…"; after ~500ms `body.authenticated` is set → CSS reveals header + `#shell-main`, hides login.
   - **No →** inline red error: "Invalid User ID or Password. Please try 1234."

**End state:** Home dashboard (`#screen-home`) visible; route restored from URL if deep-linked.

---

## FLOW 2 — Home Orientation & Routing  `[shell]`

**Trigger:** Authenticated; Home visible.

1. On load, `renderHomeScripts()` builds the drill registry, renders pulse circles (live counts), draws the nudge-trend chart.
2. User scans: hero greeting → pulse circles → action cards → cohort-health → NCCN benchmarks → attention patients → recent/incomplete.
3. **Branch points** (each persists to URL + session/localStorage):
   - Top nav **Home / Patient List / Dashboard** → Flow 2 / Flow 3 / Flow 7.
   - Hero stat tags "347 cohort records" / "63 active care gap flags" → Dashboard (Flow 7), deep-linked to overview / quality.
   - Pulse circles → Pending Nudges→quality view; others→home drilldown modal (Flow 6).
   - Action cards → Patient List / Dashboard / scroll-to-attention / quality view / Add-New-Patient-via-file.
   - Guideline banner "View Guidelines →" → Flow 5.

**End state:** User lands on a deeper view; back navigation reconstructs prior state.

---

## FLOW 3 — Patient List / Roster  `[shell]`

**Trigger:** "Open Patient File" card, "Patient List" nav, or viewer toolbar button.

1. `#screen-files` shown; `renderPatientQueue()` lists the HOD's department roster (8 visible).
2. **Filter:** click a status chip (Last Visit / Upcoming / Overdue) → non-active chips dim to 0.4; list filters; counts update.
3. **Search:** type name/UHID → live filter + "N results for …" copy.
4. **Privacy:** eye-toggle reveals/masks names (state persists as `queueNames=1`).
5. **Select:** click **Open file** on a row → Flow 4 (opens Patient File in viewer).

**End state:** Either a filtered roster or a patient file open in the viewer.

---

## FLOW 4 — Open a Patient File (Shell → File)  `[shell]`⤳`[file]`

**Trigger:** Any "Open file" / patient-name / flagged-card / drilldown-row / recent-row click.

1. Shell `openPatientFile(id, source)` builds `patient-file.html?patient={encoded JSON}` (or `?new=true` for onboarding).
2. `#screen-viewer` shown; `#viewer-frame` loads the URL; toolbar set (kicker/title, masked for privacy; Back target derived from source).
3. `[file]` hydrates: `?patient=` token-replaces name/UHID/ABHA/phone/DOB/age throughout; `?new=true` resets to a blank form.
4. `[file]` lands on **Nudges & Alerts** section; `computeNudges()` runs; urgent banner + sidebar badge populate.
5. Privacy state syncs: `[file]` ⤳ `privacy-toggle` keeps shell title masking consistent.

**Back paths (viewer toolbar):** Back (to Data Table / Dashboard / Home / Patient List, per source), Patient List, Home.

**End state:** Patient File open and hydrated inside the shell viewer.

---

## FLOW 5 — Guidelines Reference  `[shell]` and `[file]`

**Trigger A (shell):** Guideline banner "View Guidelines →" → `glOpen('nccn')` → home drilldown modal renders a 3-card guideline reference (NCCN 2024 changes / India practice realities / demo talking points) with stat chips.

**Trigger B (file):** Header **Guidelines ▾** dropdown → opens the Guidelines modal at a chosen tab.
1. Modal shows 5 tabs: **India / NCCN / Compare / Staging / References**.
2. User switches tabs (`glTab`) and expands collapsible accordions (`glToggle`).
3. Close via ✕ / overlay / Escape.

**End state:** User returns to prior context with no state loss.

---

## FLOW 6 — Home Metric Drilldown  `[shell]`

**Trigger:** Any `[data-home-drill]` element — cohort-health card, NCCN benchmark card, nudge-trend card, care-gap row, or pulse circle (keyboard-accessible: Enter/Space).

1. `openHomeDrill(key)` opens `#home-drill-overlay`; `renderHomeDrill()` pulls the matching config from the drill registry (~15 datasets).
2. Modal shows: title, subtitle, stat chips, and a representative patient table (per-metric columns: stage, PSA, ADT duration, bone Rx, DEXA, MDT status, completion %, next step…).
3. **Drill to patient:** click a patient name or "Open file" → modal closes (state retained) → Flow 4 opens that patient's file with Back target "Back to Data Table".
4. **Return:** Back re-opens the same drilldown (`restoreHomeDrill`).
5. Close via ✕ / overlay / Escape.

**End state:** Either back at Home or inside a patient file reachable back to the drill table.

---

## FLOW 7 — Population Analytics Exploration  `[shell]`⤳`[analytics]`

**Trigger:** Dashboard nav, hero stat tags, action cards, or section "view …" links.

1. Shell `openPopulationDashboard(section, focus)` loads `population-analytics.html?section=…&focus=…` in the viewer.
2. `[analytics]` `applyInitialRoute()` activates the section and smooth-scrolls to the focus element.
3. User navigates the **6 sections** (Overview / Clinical / Treatment / Outcomes / Quality / Demographics) via sidebar; `nav()` updates URL params and ⤳ `shell-route` so the shell stays in sync.
4. **Snapshot** sidebar shows live cohort stats; **time-range chips** toggle visually (cosmetic).
5. **Quality nudge trend:** Weekly / Monthly chips swap datasets.

**End state:** A chosen analytic section, deep-linkable and shell-synced.

---

## FLOW 8 — Chart Drill-Down to Patient  `[analytics]`⤳`[shell]`⤳`[file]`

**Trigger:** Click any chart element (bar/slice/line point/radar vertex/heatmap cell/state row).

1. `wire(chart, filterFn, …)` resolves the clicked selection (`getChartSelection` robust hit detection) and filters the 347-patient `PTS` array.
2. `dpOpen()` slides in the right-hand drill panel: dynamic title/subtitle, stat chips (count, avg age, median PSA, on-ADT, high+ risk), and a patient table (ID/Name/Age/Risk/PSA/Gleason/Stage/Coverage/Care Gaps).
   - Specialized variants: completeness drill, protocol-axis drill (cohort dataset only), heatmap-cell drill.
3. **Select patient:** click a row → `[analytics]` ⤳ `demo-nav {target:'patient', backTarget:'dashboard', record}` → shell opens that patient's file (Flow 4) with Back → Dashboard.
4. Close panel via ✕ / overlay / Escape.

**Known issue:** RT-outcome chart drill references undefined `RT_OUTCOME_LABELS` and throws (panel won't open) — see Feature PRD §6.

**End state:** A filtered patient list, or a patient file opened with a path back to the dashboard.

---

## FLOW 9 — Care-Gap → Nudge → Team Notify (the core clinical loop)

This is the platform's signature end-to-end story, spanning all three pages.

**9a. Discover the gap (population):** `[analytics]` Quality & Gaps → "Top care gaps" (e.g. "No bone protection on ADT >3m — 42 pts") → click → drill panel lists the 42 patients → select R.K. Sharma → ⤳ opens his file.

**9b. See the nudge (patient):** `[file]` Nudges section — `computeNudges()` has already flagged: bone protection not started (urgent), PSMA PET-CT not done (urgent), ARSI not intensified (warning), DEXA not done, germline not ordered, no follow-up date. Urgent banner shows the count.

**9c. Acknowledge & route to team:** Click **"Acknowledge & log →"** on a nudge → `openTeamModalFromNudge()` pre-fills the Discuss-with-Team modal (source title/body, reason, recipient mode = all MDT).

**9d. Compose & preview:**
1. Choose recipient mode: **specific member** (typeahead against the 5-clinician MDT directory, auto-fills email) or **all MDT members**.
2. Fill reason (Urgent review / Care gap / Treatment decision / MDT discussion / FYI), subject, note; optionally "include secure patient summary link"; set demo recipient email.
3. **Preview received email** → opens a styled email render (sender, patient summary grid, flag source, CTA, demo disclaimer).

**9e. Send:** **Send to Team** validates → persists per-patient to localStorage → refreshes the **Team Discussion Log** → recomputes nudges → toast "Notification sent to …". Logged entries offer "Preview email" to re-render.

**End state:** Gap is documented and routed to the MDT; nudge shows "Logged with team →"; an audit trail exists in the Team Discussion Log and acknowledged-nudges history.

---

## FLOW 10 — Rx / Prescription Upload  `[file]`

**Trigger:** Header **Upload Rx** or Treatment-section upload toolbar.

1. `triggerRxUpload()` clicks a hidden `<input type=file accept=".pdf,image/*" multiple>`.
2. User selects file(s) → `handleRxUpload()` stores each as a blob in IndexedDB (`prostacare-demo`/`rxDocs`, keyed by UHID); status messages update.
3. `#rx-list` renders each doc (name/time/MIME/size) with **Open** (object URL in new tab) and **Remove** (deletes from IndexedDB).

**End state:** Uploaded prescriptions persist across reloads (browser-local) and are openable/removable.

---

## FLOW 11 — Add New Patient & Team Notify  `[shell]`

> **Status:** intended flow is fully coded but its in-page modal trigger is currently orphaned (Feature PRD §6.1). The reachable path today is the "Add New Patient" home card, which opens the blank Patient File (`?new=true`) and does **not** fire the email flow. Both documented below.

**11a. Intended modal flow (currently unreachable):**
1. Open **New Patient Onboarding** modal (`openAddPatientModal`).
2. Fill Full Name, Age, Gender, UHID, Initial Status (Upcoming/Arrived/Urgent) → **Register**.
3. Button shows "Registering…"; after ~1s the patient is added to the live queue.
4. System builds an email to the full MDT directory, logs it to localStorage, refreshes doctor context + queue, closes the form.
5. **Team notification sent** preview overlay renders (subject "New patient registered — {name} ({UHID})", From/To/Sent/Scope, patient KV grid, "Open patient file", demo disclaimer).

**11b. Reachable path today:** Home "Add New Patient" card → `openPatientFile('new')` → `patient-file.html?new=true` → blank form (`resetFormForNewPatient`) for fresh data entry.

**End state:** New patient in the roster (11a) or a blank patient file ready for entry (11b).

---

## FLOW 12 — Patient Journey & Timeline  `[file]`

**Trigger:** Patient File → Patient Journey section.

1. **Care Pathway stepper** shows 6 stages (Diagnosis ✓, Staging ✓, MDT Review ✓, Treatment ●now, Response Assessment ○, Long-term F/U ○).
2. **Detailed Event Timeline** lists 8 chronological events (color-coded done/now/upcoming dots).
3. **Add New Journey Event** form: event type + date + notes → "+ Add to Timeline". *(Button present but not yet wired — backlog.)*

**End state:** User reviews the longitudinal care pathway.

---

## FLOW 13 — Privacy Masking (cross-page)  `[shell]`⤳`[file]`/`[analytics]`

**Trigger:** Any eye-toggle (header, banner, sidebar, queue).

1. Toggling on a page blurs/reveals all `[data-sensitive-name]` / `[data-sensitive-phone]` nodes via CSS.
2. A child page ⤳ `privacy-toggle {visible}` to the shell; the shell updates its viewer title masking and queue state, and persists `queueNames` in the route.
3. On reload, masking state is restored from the route.

**End state:** Consistent name-visibility across shell and embedded views, persisted.

---

## State Persistence Summary

| State | Store | Survives reload? | Cross-page? |
|---|---|---|---|
| Auth | in-memory (`body.authenticated`) | No | Shell only |
| Active screen / search / filter / drilldown | URL params + session/localStorage | Yes | Shell |
| Dashboard section / focus | URL params + ⤳ shell-route | Yes | Shell↔Analytics |
| Privacy masking | route param + ⤳ privacy-toggle | Yes | All |
| Patient identity (into file) | URL `?patient=` / `?new=true` | Yes (link) | Shell→File |
| Team notifications + prefs | localStorage (per-UHID) | Yes | File |
| Rx documents | IndexedDB (per-UHID) | Yes | File |
| New-patient email log | localStorage | Yes | Shell |
