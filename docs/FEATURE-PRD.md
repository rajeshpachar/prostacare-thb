# ProstaCare India (THB) — Feature PRD

**Product:** ProstaCare India · Clinical Analytics & Patient Management Platform
**Domain:** Uro-oncology / prostate cancer care (India-localized)
**Persona (primary):** Dr. Anand Sharma — Professor & HOD, Urology & Radiation Oncology, AIIMS New Delhi
**Status:** Interactive demo / prototype ("THB Sample Prostate Ca Screens prepared for NVS Team"). All clinical data is illustrative/synthetic.
**Architecture:** Three self-contained HTML pages, no build step, no backend. `index.html` is the shell; it embeds `patient-file.html` and `population-analytics.html` in an iframe and they communicate via `postMessage`. Chart.js 4.4.1 (CDN), DM Sans/Serif/Mono fonts, browser-local persistence (sessionStorage, localStorage, IndexedDB).

---

## 1. Product Overview

ProstaCare India is a clinician command-center for a prostate-cancer service. It unifies three jobs into one cohesive experience:

1. **Home / command-center** (`index.html`) — greets the HOD, surfaces cohort-health KPIs, NCCN-benchmark gaps, care-gap "nudges", flagged patients, and routes into every other view.
2. **Patient File** (`patient-file.html`) — an EMR-style single-patient workspace with demographics, clinical assessment, treatment plan, longitudinal journey, decision-support nudges, team communication, and Rx document management.
3. **Population Analytics** (`population-analytics.html`) — a cohort dashboard of 347 patients with KPIs, ~35 charts across 6 analytic domains, and click-to-drill patient lists.

The product's narrative thesis: India-specific access/cost realities (CGHS/PMJAY turnaround, reliance on CT+bone scan over PSMA PET-CT, under-use of ARSI and bone protection) create **measurable, closeable care gaps** — and the platform makes them visible and actionable.

### 1.1 Goals
- Give an HOD a single glance at cohort protocol-adherence vs NCCN benchmarks.
- Convert population-level gaps into per-patient, actionable nudges.
- Support MDT (multi-disciplinary team) collaboration via notify/discussion flows.
- Demonstrate India-localized clinical workflows (ABHA/Aadhaar/CGHS, EAU+NCCN framing).

### 1.2 Non-Goals (current prototype)
- Real persistence/backend, auth, or PHI handling (all browser-local, demo-only).
- Live data derivation for every displayed KPI (several are presentational literals).
- Production messaging/email (notify flows render demo previews only).

---

## 2. Cross-Cutting Capabilities

These behaviors span all pages and define the platform's UX contract.

| Capability | Description | Where |
|---|---|---|
| **Iframe shell + postMessage bus** | `index.html` hosts child pages in `#viewer-frame`. Children push `demo-nav` (open patient/files/home), `privacy-toggle` (name masking), and `shell-route` (dashboard section/focus) events to the parent. | All pages |
| **Privacy-by-default name masking** | Patient names render blurred; a per-screen eye-toggle reveals them. State syncs bidirectionally across shell↔iframe. | All pages |
| **Deep, resilient routing** | Screen/section/search/filter/drilldown state encoded to URL query params + session/localStorage; restored on reload or deep-link. | Shell + Analytics |
| **Drill-to-patient pattern** | Almost every metric/chart/row drills down to a patient list; selecting a patient opens their Patient File. | All pages |
| **India localization** | ABHA, Aadhaar, UHID, CGHS/PMJAY/ESIC coverage; AIIMS/Tata Memorial/PGIMER referral centres; Hindi/regional languages; EAU+NCCN guideline framing; generic-drug (abiraterone) economics. | All pages |
| **Demo disclaimers** | Diagonal watermark on every page; "illustrative TLGs" notes; "demo preview only / in production…" labels on notify/upload flows. | All pages |
| **Design system** | "Clinical glass" theme — frosted cards, radial-gradient backgrounds, gradient top-accent bars, semantic color palette (teal=ok, amber=warn, red=danger, blue/purple=info/interactive), staggered fade-up entrance animations, hover-lift micro-interactions. | All pages |

---

## 3. Feature Inventory

### F1 — Authentication Gate (Shell)
- **F1.1 Login screen** — branded full-screen overlay; User ID + Password; demo passphrase `1234`; simulated 500ms "Signing in…" then reveals app. Invalid input shows inline error.

### F2 — Home Command Center (Shell)
- **F2.1 Sticky header & top nav** — brand, doctor identity, Home / Patient List / Dashboard nav with synced active state.
- **F2.2 Welcome hero** — greeting, identity tags, two clickable cohort stat tags ("347 cohort records", "63 active care gap flags") that deep-link to the dashboard.
- **F2.3 Cohort pulse circles** — five live-computed glassmorphic circles: Pending Nudges (emphasized pulsing halo), Critical Gaps, Upcoming MDT Review, Incomplete Data Entry, Critical Patients. Each routes to a drilldown or the dashboard.
- **F2.4 Action cards** — Open Patient File, Go to Dashboard, Review Urgent Attention Patients, Review Care Gaps, Add New Patient.
- **F2.5 Department at a glance** — Last Visit / Upcoming / Overdue / Population Alerts counters.
- **F2.6 Guideline update banner** — "NEW · NCCN 2024" callout (PSMA PET-CT → Category 1; Darolutamide added) with "View Guidelines →" CTA and dismiss.
- **F2.7 Cohort health cards** — Protocol adherence 73/100, Open care gaps 63, Record completeness 68%, New registrations 18; each drills down with sparklines and reason text.
- **F2.8 Cohort vs NCCN benchmarks** — ARSI intensification 29% vs 60%, PSMA PET-CT 46% vs 85%, Bone protection 33% vs 85%, MDT review 77% vs 95%; each drills down.
- **F2.9 Nudge trend analysis** — Chart.js stacked bar (Opened/Viewed/Acted/Resolved) + Net Active line; Weekly/Monthly toggle.
- **F2.10 Cohort attention required** — three flagged-patient cards (R.K. Sharma, S.N. Tiwari, B.S. Rathod), Insight of the Day, and a care-gap breakdown list.
- **F2.11 Recently viewed & Incomplete records** — recent patient rows + data-entry-pending rows with completion bars.
- **F2.12 Home metric drilldown modal** — generic modal showing stat chips + a representative patient table for any metric/benchmark/gap/pulse; rows open the Patient File and return to the table.

### F3 — Patient List / Roster (Shell)
- **F3.1 Department roster** — searchable queue scoped to the HOD's department (8 of 10 seeded patients).
- **F3.2 Status filter chips** — Last Visit / Upcoming / Overdue with live counts.
- **F3.3 Search** — by name or UHID, with live result count.
- **F3.4 Privacy name-mask toggle** — reveals/masks queue names.
- **F3.5 Queue rows** — slot, status, masked name, UHID/age/clinic, flag badges, visit reason, "Open file".

### F4 — Add New Patient & Team Notify (Shell)
- **F4.1 New Patient Onboarding modal** — Full Name, Age, Gender, UHID, Initial Status; simulated registration adds to live queue. *(Note: in-page modal trigger is currently orphaned — see §6.)*
- **F4.2 Team notification on registration** — builds an email to the full MDT directory (5 clinicians), logs to localStorage, and shows an email-style "Team notification sent" preview with patient summary + "Open patient file".
- **F4.3 New-patient via Patient File** — "Add New Patient" home card opens `patient-file.html?new=true` (blank form path; does not trigger the email flow).

### F5 — Patient File: Record Management
- **F5.1 Patient header & banner** — avatar, masked name, IDs (UHID/ABHA), risk/HSPC/CGHS/ADT badges, stat pills (PSA, stage, grade, ECOG), treating doctor.
- **F5.2 Sidebar nav & quick metrics** — 5 sections + PSA/Gleason/ADT-duration/ECOG quick metrics; nudge badge count.
- **F5.3 Demographics section** — personal info, government IDs & coverage (Aadhaar/ABHA/UHID/CGHS), contact & address; India-specific option sets.
- **F5.4 Clinical Assessment section** — presenting complaints, DRE chips, PSA history table + trend chart, biopsy details, TNM staging & risk, imaging/molecular workup, comorbidities & family history.
- **F5.5 Treatment Plan section** — intent & MDT, ADT, chemotherapy, radiotherapy plan, bone health & supportive care, Rx uploads.
- **F5.6 Patient Journey section** — care-pathway stepper (6 stages), detailed event timeline (8 events), add-event form.

### F6 — Patient File: Decision Support (Nudges)
- **F6.1 Nudges engine** — `computeNudges()` reads 9 clinical controls and generates up to ~8 typed nudges (urgent/warning/info) per evidence rules: bone scan, PSMA PET-CT, bone protection, DEXA, germline testing, ARSI intensification, follow-up date, psychosocial screening.
- **F6.2 Urgent alert banner** — dynamic count of urgent clinical actions, with "View all nudges →".
- **F6.3 Acknowledge & log** — each nudge can be acknowledged and routed into the team-discussion flow; logged state persists.
- **F6.4 Acknowledged nudges log** — completed-actions history.

### F7 — Patient File: Team Collaboration
- **F7.1 Discuss with Team modal** — recipient mode (specific member vs all MDT), typeahead directory search, reason/subject/note, "include secure patient summary link", demo recipient email.
- **F7.2 Notification email preview** — styled email render (sender, patient summary grid, flag source, CTA, disclaimer).
- **F7.3 Send to Team** — validates, persists per-patient to localStorage, refreshes Team Discussion Log, recomputes nudges, shows toast.
- **F7.4 Team Discussion Log** — per-patient history with "Preview email" re-render.

### F8 — Patient File: Rx / Document Management
- **F8.1 Upload Rx** — hidden file input (PDF/images, multiple); files stored as blobs in IndexedDB keyed by UHID.
- **F8.2 Rx list** — name/time/MIME/size; **Open** (object URL in new tab) and **Remove**.
- **F8.3 Triggers** — accessible from header and Treatment section.

### F9 — Patient File: Guidelines Reference
- **F9.1 Guidelines dropdown** (header) — opens the guidelines modal at a chosen tab.
- **F9.2 Guidelines modal** — 5 tabs (India / NCCN / Compare / Staging / References) with collapsible accordions; covers high-risk workup, ADT monitoring, PSMA/ARSI framing, India-vs-NCCN access gaps, staging tiers, references (EAU, NCCN, STAMPEDE/ENZAMET/TITAN/ARASENS).

### F10 — Patient File: Utilities
- **F10.1 Print Summary** — `window.print()`.
- **F10.2 Patient hydration** — `?patient={json}` token-replaces identity across the DOM; `?new=true` resets to a blank new-patient form.

### F11 — Population Analytics: Navigation & Snapshot
- **F11.1 Six analytic sections** — Overview, Clinical Profile, Treatment, Outcomes, Quality & Gaps, Demographics.
- **F11.2 Sidebar snapshot** — live cohort stats (High/VH Risk, Active ADT, ARSI Intensified, Care Gaps, Median PSA, Protocol Score).
- **F11.3 Time-range chips** — 3M / 1Y / All time *(cosmetic in prototype — see §6)*.
- **F11.4 Export** — `window.print()`.

### F12 — Population Analytics: Visualizations (~35 charts)
- **F12.1 Overview** — registrations combo, risk donut, age bar, coverage donut, stage bar.
- **F12.2 Clinical** — PSA-at-dx histogram, PSA percentile-band trend, Gleason bar, PSA density, free-PSA, comorbidities, PSA×Gleason heatmap.
- **F12.3 Treatment** — treatment funnel, ADT agents, RT fractionation donut, ARSI agents, ADT duration.
- **F12.4 Outcomes** — PSA-response multi-line by arm, Kaplan-Meier BCR-free survival, time-to-nadir, PSA doubling time, RT outcome by fractionation, time-to-treatment, ARSI PSA response.
- **F12.5 Quality** — nudge trend stacked combo, protocol-adherence radar (cohort vs NCCN), CGHS delay, bone-gap donut, data-completeness bar, MDT review-rate line.
- **F12.6 Demographics** — patients by state, coverage-by-state stacked bar, referral donut, travel distance, language, comorbidity pairs, ECOG donut.

### F13 — Population Analytics: Drill-Down
- **F13.1 Universal chart drill** — clicking any bar/slice/point/vertex filters the cohort and slides in a right-hand panel.
- **F13.2 Drill panel** — dynamic title/subtitle/stat chips + patient table (ID, Name, Age, Risk, PSA, Gleason, Stage, Coverage, Care Gaps).
- **F13.3 Specialized drills** — completeness drill, protocol-axis drill, heatmap-cell drill, state-row drill.
- **F13.4 Drill-to-patient** — selecting a row posts `demo-nav` to the shell, which opens that patient's file (with "back to dashboard").
- **F13.5 Nudge trend toggle** — Weekly / Monthly.

---

## 4. Clinical Data Model (Demo Seed)

### 4.1 Cohort (Population Analytics)
- **347 synthetic patients** (7 seeded + 340 deterministic RNG). Risk weights: Low .18, Int-Fav .16, Int-Unfav .16, High .30, Very High .11, M1 .09.
- Per-patient dimensions: risk tier, clinical stage, Gleason/ISUP, coverage, ADT agent, RT fractionation, ARSI agent, ADT duration, PSA density, free-PSA, ECOG, comorbidity bitmask, state, referral, travel, language, nadir, PSA doubling time, time-to-treatment, CGHS delay, bone-gap category, response group, MDT-reviewed flag, completeness group, per-axis protocol status.

### 4.2 Roster (Shell)
- 10 seeded visiting patients (p1–p10) with full Indian demographics, appointment slots, statuses, visit reasons, and clinical flags; department filter shows 8.

### 4.3 Index Patient (Patient File) — Ramesh Kumar Sharma
- 68y male; UHID DL-2024-08742; ABHA 78-5432-1234-9876; CGHS; AIIMS New Delhi.
- Prostate adenocarcinoma, **cT3bN1M0, EAU High risk, HSPC**, Gleason 4+4=8 / ISUP 4.
- PSA trend: Oct'23 18.2 → Feb'24 31.4 → Aug'24 42.6 ng/mL.
- Biopsy MRI-fusion, PI-RADS 4, 10/12 cores (83%), PNI+, ECE+.
- ADT (Leuprolide depot, ~4mo) + Bicalutamide; **ARSI not initiated; bone protection not started; PSMA PET-CT / bone scan / DEXA / genomics not done**; RT planned (IMRT/VMAT 78Gy/39fx) awaiting CGHS approval.

### 4.3 Benchmark Targets (NCCN)
ARSI intensification 60%, PSMA PET-CT 85%, Bone protection 85%, MDT review 95%, plus a 10-axis protocol-adherence radar benchmark.

---

## 5. Persistence & Integration

| Mechanism | Used for |
|---|---|
| **sessionStorage / localStorage** | Shell route state; team notifications (per-UHID); notify preferences; new-patient email log |
| **IndexedDB** (`prostacare-demo` / `rxDocs`) | Rx document blobs, keyed by UHID |
| **URL query params** | Shell screen/search/filter/drilldown; dashboard section/focus; patient payload |
| **postMessage** | Shell ↔ iframe navigation, privacy state, route sync |
| **External link** | THB corporate site (logo) |

---

## 6. Known Gaps / Issues (carry into backlog)

1. **Orphaned Add-Patient trigger** — the Patient List "Add Patient" button has no opening `<button>`/onclick; `openAddPatientModal()` is never called, so the in-page Add-Patient modal **and its team-notify email flow (F4.1/F4.2) are unreachable** from the UI.
2. **Analytics drill ReferenceError** — `RT_OUTCOME_LABELS` is referenced but never defined; clicking the RT-outcome chart throws and the drill won't open.
3. **Cosmetic time-range chips** — `setT()` only toggles styling; 3M/1Y/All time don't re-filter data.
4. **No-op buttons** — "Download report" (Overview) and "Add to Timeline" (Patient Journey) have no handlers.
5. **Static vs computed drift** — several hero/glance/snapshot KPIs are hard-coded literals and can diverge from the live-computed roster/cohort.
6. **Decoupled PSA chart** — the Patient File PSA chart points are hardcoded and don't read the editable PSA table.
7. **Save buttons** — Demographics / Treatment "Save" buttons have no persistence beyond "Save & Refresh Nudges".
8. **Font mismatch** — CSS variables name IBM Plex but DM Sans/Serif/Mono are what load.

---

## 7. Success Signals (demo context)

- HOD can move Home → gap → drilldown → patient file → notify team in under a minute.
- Every population metric is "explainable" down to named patients.
- India-localized content reads as authentic to a clinical audience.
- Care-gap narrative (ARSI / PSMA / bone protection under-use) lands as the platform's value proposition.
