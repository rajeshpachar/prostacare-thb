# ProstaCare — Open Questions & Confirmations Required Before Development Starts

**Purpose:** one consolidated list of everything we need from the client (business / clinical / legal) before, and shortly after, development begins. Every item carries a **recommended default** so the client can simply **confirm or amend** rather than design from scratch.

**Status summary**
- ✅ **7 decisions already settled** (§1) — no need to revisit.
- 🔴 **10 blockers (P0)** — must be answered before dev starts (§2).
- 🟠 **7 items (P1)** — needed within the first sprint (§3).
- 🟡 **7 items (P2)** — needed before go-live, not before dev (§4).
- ⚙️ **6 internal decisions** — ours to make, no client input needed (§5).

> Fastest path: a single **90-minute workshop** covering §2, with clinical + business + legal present. Everything in §2 has a recommended default; most should be a "confirm."

---

## 1. Already decided (for reference — not open)

| # | Decision |
|---|---|
| 1 | **Tenant = institution** — one schema per hospital; no `institution_id` |
| 2 | **Clinical access = department/team scoped** (HOD/coordinator may be tenant-wide) |
| 3 | **Ops / quality / pharma sponsor = de-identified aggregate only** (PHI firewall) |
| 4 | Identifiers **masked-by-default + audited reveal** *(applies only if the identified model is chosen — see B1)* |
| 5 | **Notifications = in-app inbox + email via AWS SES**; **login identity = email** |
| 6 | **Cross-tenant aggregation** = in-tenant `sponsor_metric` → Zygo Data Cloud → sponsor (architecture spec'd) |
| 7 | **8 care-gap rules** specified (conditions/severities) — pending clinical sign-off (B8) |

---

## 2. 🔴 BLOCKERS — needed before development starts

| ID | Question | Why it blocks dev | Owner | Our recommended default |
|---|---|---|---|---|
| **B1** | **Identity model:** does ProstaCare store PHI? (A) de-identified registry — `patient_code` only, identity stays in hospital HIS; (B) identified EMR-lite; (C) de-identified core + optional isolated identity module | Determines the entire schema, consent basis, and compliance surface. **The single biggest decision.** | Clinical + Legal | **A** (or **C** if any site needs bedside identification). Matches the V2 workbook, makes the sponsor firewall near-trivial, lightest DPDP burden. |
| **B2** | **Multi-user or single console?** Do clinicians/MDT members log in, have a panel and an inbox — or is "team" just a notify list? | Determines roles, scopes, inbox, and the whole collaboration model | Business | **Multi-user, role-based** (the department-scoped access decision already implies it) |
| **B3** | **Team model:** is a per-patient **care team** distinct from the department **MDT / tumour board**? Who manages membership? | Determines entities (`care_team_member`, `mdt_panel`) and the "notify all" target | Clinical | Both: a **department MDT panel** (notify-all target) **+ a per-patient treating clinician / small care team**. Admin-managed, history retained. |
| **B4** | **Patient source of truth:** created in ProstaCare, or **synced from hospital HIS/registry**? If synced — match key (`patient_code`? UHID? ABHA?) and which fields are read-only | Determines onboarding flow, integration scope, and patient entity ownership | Business + IT | **Created in ProstaCare** for v1 (registry), keyed on `patient_code`; HIS sync as a later phase |
| **B5** | **Disease scope:** prostate only, or the first of several tumour frameworks? | Determines whether we build a shared clinical core + disease overlay, or a single-disease schema | Business | **Prostate first, on a templatable core** (so breast/lung can be added later without rework) |
| **B6** | **Visit / Encounter:** registry organised by clinical event date (recommended) or every entry bound to a visit/encounter? | Determines the event-tier design and data-entry burden | Clinical | **Registry-by-event**, with an **optional** `encounter` (nullable link) for visit grouping / future HIS-appointment sync |
| **B7** | **Sponsor:** confirm **NVS = Novartis**; their role (funder / data consumer / both); and the **independent clinical governance** that owns the rule pack (conflict-of-interest control) | Determines the aggregation contract, governance model, and consent basis | Business + Legal | Sponsor receives **de-identified aggregate only**; rule pack owned by an **independent clinical committee** with versioned sign-off; hard firewall |
| **B8** | **Clinical sign-off on the 8 care-gap rules** — conditions, severities, next-step wording — and the **benchmark targets** (ARSI 60%, PSMA 85%, bone protection 85%, MDT review 95%) | The care-gap engine is the core product; rules cannot be coded unsigned | Clinical | Confirm as specified in `PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md §4`; amend thresholds/wording as needed |
| **B9** | **Aggregation contract:** confirm the `metric_key` catalogue; **small-cell suppression threshold** (default **11**); institution shown as **anonymised code** vs named | Determines what `sponsor_metric` computes and exports | Clinical + Legal | Catalogue as spec'd; threshold **11**; **anonymised `institution_code`** |
| **B10** | **Launch institution + user roster + identity source:** which hospital(s) go first, the doctor/coordinator roster (name, specialty, role, email), and **Azure AD SSO vs email/local accounts** | Cannot provision a tenant or onboard users without it. No roster exists in any document today. | Business + IT | Start with **one department at one institution**; SSO if available, else email/local. Also needs an **SES verified sender domain + SES production access** (see P1-9). |

---

## 3. 🟠 P1 — needed within the first sprint (dev can start without)

| ID | Question | Owner | Recommended default |
|---|---|---|---|
| P1-1 | **Nudge ownership** — who is responsible when a gap fires (treating clinician / relevant specialist / coordinator)? | Clinical | Treating clinician, with coordinator visibility |
| P1-2 | **SLA / escalation / snooze** — do unactioned urgent nudges escalate? After how long, to whom? Is "snooze" allowed? Does dismissal need a reason? | Clinical | Escalate urgent to HOD/coordinator after N days; dismissal requires an audited reason; no snooze in v1 |
| P1-3 | **Notification detail** — digest vs real-time; which triggers email vs in-app only; any patient-facing comms? | Business | Real-time for urgent, **daily digest** otherwise; clinician-only (no patient-facing) in v1 |
| P1-4 | **Edit permissions** — is record editing gated by specialty (e.g. only Radiation Onc edits the RT plan)? Should "notify all MDT" be restricted? | Clinical | No specialty gating in v1; restrict "notify all MDT" to HOD/coordinator |
| P1-5 | **Cardinality confirmations** — `pathology` 1-per-patient (re-biopsy → new row), `outcome` 1-per-patient, **supportive-care dated** | Clinical | As recommended (dated supportive-care gives the bone-protection audit trail) |
| P1-6 | **Data migration** — greenfield, or import an existing registry at the launch site? | Business | Greenfield for v1 |
| P1-7 | **Rule governance mechanism** — clinicians tune severity/wording/thresholds in config; changing rule *logic shape* is a versioned engineering change. Acceptable? | Clinical | Yes (see `NOVAEDGE_ALIGNMENT_REVIEW.md` G2) |

---

## 4. 🟡 P2 — needed before go-live, not before dev

| ID | Question | Owner |
|---|---|---|
| P2-1 | **SES prerequisites** — verified sender domain/address + SES **production access** (out of sandbox) | IT |
| P2-2 | **Export mechanism & cadence** to Zygo Data Cloud — S3 push (recommended) vs pull API; nightly compute, weekly/monthly export | Business + Platform |
| P2-3 | **Consent / legal basis** for aggregate secondary use (DPDP Act; ethics committee if applicable) | Legal |
| P2-4 | **Domain, hosting, data residency, IP ownership** | Business + Legal |
| P2-5 | **Clinical chart renderers** — PSA line, percentile bands, Kaplan-Meier (frontend work) | Platform |
| P2-6 | **Enum localisation** per site (RT facilities, referring centres) | Clinical |
| P2-7 | **Deployment model** — per-doctor SaaS tenant (`O-DEP`) is *not* v1; confirm it stays out of scope | Business |

---

## 5. ⚙️ Internal decisions (ours — no client input needed)

| ID | Item | Resolution |
|---|---|---|
| I-1 | Cross-tenant de-identified aggregation layer (the one net-new component) | Build per `CROSS_TENANT_AGGREGATION_SPEC.md` |
| I-2 | Current-state ("latest dated row") encoding | Materialized view + lateral subquery — **not** a computed column |
| I-3 | Care-gap rule encoding | `guideline_rule` config metadata + one predicate step per rule |
| I-4 | Workbook flag columns → normalized `patient_condition` rows | Import transform |
| I-5 | Partitioning (`psa_reading`, `nudge_event`) | RANGE partition + composite PK |
| I-6 | Audit coverage | Cross-cutting audit subscription on all entities + reveal audit |

---

## 6. What we can start immediately once §2 is answered

| Unblocked by | Work that can start |
|---|---|
| **B1 + B2 + B4 + B6** | **P0 Foundation** — tenancy, roles/scopes, patient hub, Tier-1 current-state entities, onboarding console |
| **B1 + B6** | **P1 Longitudinal** — PSA, staging, imaging, treatment lines, supportive care, journey |
| **B8** | **P2 Care-gap engine** — the 8 rules, nudge lifecycle |
| **B3 + B10 + P2-1** | **MDT notify** (SES) + user onboarding |
| **B7 + B9** | **Aggregation** — `sponsor_metric` + Zygo Data Cloud pipeline |
| **B5** | Schema core shape (single-disease vs templatable overlay) |

**Critical path:** **B1 (identity model)** gates everything. **B8 (rule sign-off)** gates the care-gap engine. **B10 (roster + auth)** gates the first tenant.

---

*Sources consolidated from: `FLOW-CLARITY-AND-OPEN-QUESTIONS.md`, `PROSTACARE_BUILD_SPEC_V1.md §12`, `PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md §7`, `NOVAEDGE_ALIGNMENT_REVIEW.md §4/§6`, `CROSS_TENANT_AGGREGATION_SPEC.md §6`, `TENANT_ONBOARDING_PLAN.md §6`.*
