# ProstaCare India — Product PRD (v0.1, draft for build)

**Purpose of this document.** The repo's three HTML screens are a clickable *representation* of the intended product. This PRD translates everything those screens show into **product requirements for the real build** — abstracting away the demo's browser-only shortcuts (hard-coded data, localStorage/IndexedDB, postMessage, simulated sends) and stating what the production system must actually do.

> Reference inventory of the demo (every screen/component/flow as-built) lives in `FEATURE-PRD.md` and `FLOW-PRD.md`. This document supersedes their "demo caveats" framing — items the demo couldn't really do become *requirements* here.

---

## 1. Product Summary

ProstaCare India is a **prostate-cancer care management and population-analytics platform** for an Indian uro-oncology / radiation-oncology service. It does three things in one workflow:

1. **Manages each patient's longitudinal record** (demographics → diagnosis → staging → treatment → journey).
2. **Runs guideline-based decision support** that converts the record into prioritized, actionable care-gap *nudges* (NCCN/EAU, India-adapted).
3. **Aggregates the whole cohort** into population analytics that quantify protocol adherence vs benchmarks and route gaps back down to named patients and the MDT.

**Core value loop:** *population gap → per-patient nudge → MDT action → measured closure.* The platform's thesis is that India-specific access/cost realities (CGHS/PMJAY turnaround, CT/bone-scan reliance over PSMA PET-CT, under-use of ARSI and bone protection) produce **measurable, closeable care gaps** — and making them visible drives better guideline concordance.

---

## 2. Users, Roles & Permissions

The demo shows a single HOD persona; the real product needs a role model.

| Role | Primary jobs | Scope |
|---|---|---|
| **HOD / Lead clinician** (demo persona) | Cohort oversight, protocol adherence, MDT chairing | Whole department cohort |
| **Treating urologist / radiation oncologist** | Own patient panel, treatment decisions, act on nudges | Assigned patients |
| **MDT members** (med-onc, radiation-onc, onco-radiology, nuclear medicine, nurse specialist) | Receive notifications, contribute to discussion, document | Patients shared with them |
| **Data-entry / MRD staff** | Complete records, upload documents (Rx, reports) | Assigned patients |
| **Admin** | User management, role assignment, audit, config | Org-wide |

**Requirements**
- R-AUTH-1: Authenticated login with org SSO and/or username/password; session management, lockout, audit. *(Demo uses passphrase `1234` — placeholder only.)*
- R-AUTH-2: Role-based access control; data scope enforced server-side (department vs panel vs shared).
- R-AUTH-3: Full audit trail for record views, edits, nudge actions, and notifications (who/what/when).
- R-PRIV-1: **Privacy-by-default name masking** is a product feature (the demo's eye-toggle): names/contact masked until explicitly revealed; reveal events are audited.

---

## 3. Functional Requirements by Domain

### 3.1 Home / Command Center
- R-HOME-1: Role-aware landing showing cohort KPIs: total records, high/very-high risk count, open care-gap count, protocol-adherence score, new registrations, record completeness.
- R-HOME-2: **Cohort pulse indicators** — at-a-glance live counts for Pending Nudges, Critical Gaps, Upcoming MDT Reviews, Incomplete Data Entry, Critical Patients; each links to its work queue. All values **computed live** from cohort data (not static).
- R-HOME-3: **Guideline-update banner** — surfaces newly published guideline changes (e.g. NCCN PSMA PET-CT category change, new ARSI options) with a link to the reference.
- R-HOME-4: **Cohort-vs-benchmark cards** — current cohort % vs NCCN benchmark for ARSI intensification, PSMA PET-CT, bone protection on ADT, MDT review rate; each drillable to the affected patients.
- R-HOME-5: **Attention queue** — patients with active critical flags, with reason and one-click open.
- R-HOME-6: **Nudge-trend analytics** — opened/viewed/acted/resolved over time + net-active backlog; weekly/monthly views.
- R-HOME-7: **Quick navigation** to Patient List, Population Dashboard, Add Patient, and metric drilldowns.

### 3.2 Patient List / Roster
- R-LIST-1: Searchable, filterable roster scoped to the user's role; search by name and identifiers (UHID/ABHA).
- R-LIST-2: Status filters (e.g. arrived / upcoming / overdue) with live counts.
- R-LIST-3: Clinical flag badges per patient; visit reason and appointment context.
- R-LIST-4: Open patient → Patient File.

### 3.3 Patient File — Record
- R-REC-1: **Demographics** — personal info; **government IDs & coverage** (Aadhaar, ABHA, UHID, CGHS/PMJAY/ESIC/State/Private/Self-pay + card numbers); contact & address with Indian state/district/PIN; language & referral centre. India-specific option sets required.
- R-REC-2: **Clinical assessment** — presenting complaints/IPSS, DRE findings, **PSA history** (longitudinal, editable, feeds the trend chart — chart must be data-driven), biopsy details (PI-RADS, Gleason/ISUP, cores, PNI, ECE), **TNM staging & risk** (EAU risk tier, ECOG, castration status), imaging & molecular workup (mpMRI, bone scan, PSMA PET-CT, CT, DEXA, germline/somatic), comorbidities & family history.
- R-REC-3: **Treatment plan** — intent & MDT status/date, ADT (agent/formulation/dates, anti-androgen, ARSI intensification, testosterone), chemotherapy, radiotherapy (modality/target/dose/fractionation/facility/dates/approval status), bone health & supportive care (bone-protection agent, Ca/Vit D, DEXA, follow-up PSA, PHQ-9, nutrition).
- R-REC-4: **Patient journey** — care-pathway stepper (diagnosis → staging → MDT → treatment → response → long-term F/U) and an editable longitudinal event timeline (add-event must persist).
- R-REC-5: All record sections persist server-side with validation, versioning, and audit. (Demo "Save" buttons become real persistence.)

### 3.4 Decision Support — Nudges Engine
- R-NUDGE-1: A **rules engine** evaluates the patient record against guideline logic and emits typed nudges (urgent / recommendation / reminder) with title, rationale, and cited guideline.
- R-NUDGE-2: Rule set (from the demo, to be clinically validated and versioned): bone scan for high-risk staging; PSMA PET-CT for high/very-high risk; bone protection on long-term ADT; DEXA on ADT; germline/genetic testing on indication (family history/BRCA); ARSI intensification for high-risk HSPC; follow-up PSA scheduling; psychosocial/sexual-health screening.
- R-NUDGE-3: Nudges recompute on record change and on guideline-version update.
- R-NUDGE-4: Each nudge supports **Acknowledge & log** and **route to MDT** (→ team flow), with status (open / logged / resolved) and audit.
- R-NUDGE-5: Acknowledged/completed nudges retained as a care-decision history.
- R-NUDGE-6: Cohort nudge metrics roll up to Home and Population Analytics.
- R-NUDGE-7: Guideline content is **versioned and configurable** (NCCN/EAU + India adaptations), not hard-coded; updates propagate to rules and reference.

### 3.5 MDT Collaboration — Notify & Discussion
- R-MDT-1: From any nudge or patient, compose a notification to a **specific MDT member or the whole MDT directory** (typeahead against a managed directory).
- R-MDT-2: Structured message: reason, subject, note, optional secure patient-summary link.
- R-MDT-3: **Preview** the rendered notification before sending.
- R-MDT-4: **Send via real channels** (email/in-app/secure messaging) — production replaces the demo's simulated send; delivery status tracked.
- R-MDT-5: Per-patient **discussion log** with full history and re-view of sent items; contributes to audit.
- R-MDT-6: Secure patient-summary links must be access-controlled and expiring (no PHI in plain URLs).

### 3.6 Document Management (Rx & Reports)
- R-DOC-1: Upload prescriptions/reports (PDF/images, multiple) attached to the patient; production stores in secure object storage (demo uses IndexedDB).
- R-DOC-2: List, open/view, and remove documents with metadata (name, type, size, uploader, timestamp); all actions audited.
- R-DOC-3: Access governed by patient scope; downloads/views logged.

### 3.7 New Patient Onboarding & Team Notify
- R-ONB-1: Register a new patient (name, age/DOB, gender, identifiers, initial status); validation and duplicate detection.
- R-ONB-2: On registration, **notify the MDT** with a structured new-patient summary and an "open file" link; delivery tracked. *(This is the demo's intended flow — must be fully reachable and wired in production.)*
- R-ONB-3: New patient appears in the appropriate roster/queue immediately.

### 3.8 Population Analytics
- R-ANL-1: Cohort dashboard across domains: **Overview, Clinical Profile, Treatment, Outcomes, Quality & Gaps, Demographics**.
- R-ANL-2: KPI cards and a **live snapshot** (risk mix, active ADT, ARSI intensified, open care gaps, median PSA, protocol score) — **computed from real cohort data**.
- R-ANL-3: Visualizations (from the demo set, all data-bound): registrations trend, risk/coverage/ECOG/referral donuts, age/stage/Gleason/PSA-density/free-PSA/comorbidity bars, PSA percentile-band trend, PSA×Gleason heatmap, treatment funnel, ADT/ARSI/RT-fractionation breakdowns, ADT-duration, PSA-response-by-arm, **Kaplan-Meier survival**, time-to-nadir, PSA-doubling-time, RT-outcome-by-fractionation, time-to-treatment, ARSI PSA response, nudge-trend, **protocol-adherence radar (cohort vs NCCN)**, CGHS-delay, bone-gap, data-completeness-by-field-group, MDT-review-rate, coverage/comorbidity/state/language demographics.
- R-ANL-4: **Functional time-range filtering** (e.g. 3M / 1Y / All) that actually re-queries data. (Demo chips are cosmetic.)
- R-ANL-5: **Universal drill-down** — clicking any chart element filters to the underlying patient list with summary stats; selecting a patient opens their file (with breadcrumb back to the dashboard).
- R-ANL-6: Specialized drills: data-completeness by field group, protocol-axis adherence, heatmap cell (stage×grade), geographic (state).
- R-ANL-7: **Export/report** generation (PDF/printable) for cohort and quality views.
- R-ANL-8: Care-gap leaderboard (top gaps with counts and % of eligible) drillable to patients and to bulk MDT action.

### 3.9 Guidelines Reference
- R-GL-1: In-context guideline reference (India practice / NCCN / comparison / staging / references) accessible from patient and home contexts.
- R-GL-2: Versioned content tied to the nudge rules; "what changed" callouts on update.

---

## 4. Cross-Cutting Requirements

- R-X-1: **Single integrated navigation** — Home ↔ Patient List ↔ Patient File ↔ Population Analytics, with deep-linkable, restorable state. (Demo's iframe+postMessage is an artifact; production should be one app with proper routing.)
- R-X-2: **Drill-to-patient everywhere** — any aggregate metric resolves to named patients and into the patient file.
- R-X-3: **Privacy masking** consistent across all views, persisted per user, reveal events audited.
- R-X-4: **India localization** as a first-class concern — identifiers (ABHA/Aadhaar/UHID), coverage schemes, referral network, languages, and India-adapted guideline economics (generic drug availability).
- R-X-5: **Live computation** — every displayed count/percentage derives from the data layer; no static literals that can drift.

---

## 5. Data Model (entities to support the above)

- **Patient** — demographics, identifiers (UHID/ABHA/Aadhaar), coverage, contact/address, referral centre, status.
- **PSA reading** — value, free-PSA %, density, date (longitudinal series).
- **Diagnosis/Pathology** — biopsy, Gleason/ISUP, PI-RADS, cores, PNI/ECE, prostate volume, DRE.
- **Staging/Risk** — cTNM, EAU risk tier, ECOG, castration status.
- **Imaging/Molecular** — mpMRI, bone scan, PSMA PET-CT, CT, DEXA, germline/somatic results.
- **Treatment** — intent, MDT status, ADT, anti-androgen, ARSI, chemo, RT plan, bone-health/supportive care.
- **Nudge** — type, rule id, guideline ref, status, timestamps, links to patient & actions.
- **Notification / Discussion entry** — sender, recipients, reason, subject, body, summary-link, delivery status, timestamps.
- **Document** — type, storage ref, metadata, uploader, audit.
- **Journey event** — type, date, notes, stage.
- **User / Role / Org** — identity, role, scope, MDT membership.
- **Guideline version** — content, rules, effective dates.
- **Audit event** — actor, action, target, timestamp.
- **Cohort/aggregate** — derived metrics for analytics (materialized or computed).

---

## 6. Integrations (production)

- **ABHA / ABDM** (Ayushman Bharat Digital Mission) for health IDs and record linkage.
- **HIS/EMR & LIS/RIS** for demographics, labs (PSA), pathology, imaging status.
- **Coverage/TPA** systems (CGHS/PMJAY/ESIC) for approval-status tracking (e.g. CGHS pre-auth delay metric).
- **Messaging** — email + secure in-app/clinical messaging for MDT notifications.
- **Object storage** for documents.
- **Guideline content source** (curated/versioned).

---

## 7. Non-Functional Requirements

- **Security & compliance** — PHI protection, encryption in transit/at rest, India data-residency, consent, role-based access, comprehensive audit. (Replaces the demo's browser-local, unauthenticated storage.)
- **Reliability/availability** — clinical-grade uptime; no data loss on the record.
- **Performance** — cohort analytics responsive at 100s–1000s of patients; drill-downs near-instant.
- **Accessibility** — keyboard navigation, ARIA roles, screen-reader labels (demo already models this).
- **Usability** — "glass" clinical design system, semantic color coding (ok/warn/danger/info), micro-interactions; consistent across screens.
- **Scalability** — multi-department / multi-site capable; cohort sizes well beyond the demo's 347.
- **Auditability & data quality** — completeness scoring per field group, validation, versioned edits.

---

## 8. Open Questions / Decisions for Real Build

1. **Patient scope per role** — exact data-access boundaries (department vs panel vs explicitly shared)?
2. **Guideline governance** — who curates/version-approves the India-adapted rule set, and how often?
3. **Notification channels** — email only, or in-app + secure clinical messaging? Delivery/read receipts required?
4. **Source of truth** — does ProstaCare own the record, or sync from an existing HIS/EMR (and which fields are read-only)?
5. **Outcome data** — how are survival/recurrence outcomes captured (manual vs derived)?
6. **Analytics freshness** — real-time vs batch aggregation for population metrics?
7. **Consent & sharing** — model for secure patient-summary links and external sharing.
8. **Deployment** — single-site pilot (AIIMS) vs multi-site from day one.

---

### Appendix — source artifacts
- `FEATURE-PRD.md` — full as-built feature inventory of the demo (13 feature groups, data seed, persistence map).
- `FLOW-PRD.md` — 13 step-by-step user flows and the navigation/state map.
- Demo screens: `index.html` (home shell), `patient-file.html` (patient record), `population-analytics.html` (cohort dashboard).
