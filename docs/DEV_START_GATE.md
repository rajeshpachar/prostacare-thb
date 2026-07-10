# ProstaCare — Open Questions & Confirmations Required Before Development Starts

> **Who this is for:** clinical, business and legal teams. **No technical background needed.**
> Any unfamiliar term (*tenant, derived, one-to-one, aggregate…*) is explained in the glossary at the top of
> **`PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md` §0 — Plain-English glossary**.


**Purpose:** one list of everything we need answered before we start building. **Each question comes with our recommended answer**, so in most cases you only need to say *"confirm"* or *"change it to…"*.

**Three terms used below:** **Tenant** = one hospital's own isolated copy of the system · **De-identified** = no name, ABHA/Aadhaar or phone — only a patient code · **Aggregate** = counts and percentages across many patients, never one person's record.

**Status summary**
- ✅ **13 decisions already settled** (§1) — no need to revisit.
- 🔴 **12 blockers (P0)** — must be answered before dev starts (§2).
- 🟠 **7 items (P1)** — needed within the first sprint (§3).
- 🟡 **4 items (P2)** — needed before go-live, not before dev (§4).
- ⚙️ **6 internal decisions** — ours to make, no client input needed (§5).

> Fastest path: a single **90-minute workshop** covering §2, with clinical + business + legal present. Everything in §2 has a recommended default; most should be a "confirm."

---

## 1. Already decided (for reference — not open)

| # | Decision |
|---|---|
| 1 | **Tenant = institution** — one schema per hospital; no `institution_id` |
| 2 | **Clinical access = role-based, tenant-wide** (no department); **HOD = privileged** |
| 3 | **Ops / quality / pharma sponsor = de-identified aggregate only** (PHI firewall) |
| 4 | Identifiers **masked-by-default + audited reveal** *(applies only if the identified model is chosen — see B1)* |
| 5 | **Notifications = email via AWS SES + simple in-app list**; **login identity = email** (no SSE push / auto-task / digest in v1) |
| 6 | **Cross-tenant aggregation** = in-tenant `sponsor_metric` → Zygo Data Cloud → sponsor (architecture spec'd) |
| 7 | **8 care-gap rules** specified (conditions/severities) — pending clinical sign-off (B8) |
| 8 | **Nudge lifecycle** = open → acknowledged → **auto-resolve** (no snooze, no dismiss); engine runs **on-write** (no cron) |
| 9 | **Roles = Clinician · HOD (privileged) · Admin**; MDT = `is_mdt_member` notify flag; **no department** |
| 10 | **Record lock:** edit window → auto-lock → **HOD** time-bound unlock (reason required, audited) |
| 11 | **Deployment model = one tenant per institution, with separation** (per-doctor SaaS tenant `O-DEP` is explicitly **not** the model) |
| 12 | **Hosting & data residency = AWS Mumbai (`ap-south-1`)**; **THB provides domain, hosting, and infrastructure** (DPDP-compliant India residency) |
| 13 | **AWS SES is already in place** — verified sender domain + **production access** (out of sandbox). No SES prerequisite work needed. |

---

## 2. 🔴 BLOCKERS — needed before development starts

| ID | Question | Why it blocks dev | Owner | Our recommended default |
|---|---|---|---|---|
| **B1** | **Identity model:** does ProstaCare store PHI? (A) de-identified registry — `patient_code` only, identity stays in hospital HIS; (B) identified EMR-lite; (C) de-identified core + optional isolated identity module | Determines the entire schema, consent basis, and compliance surface. **The single biggest decision.** | Clinical + Legal | **A** (or **C** if any site needs bedside identification). Matches the V2 workbook, makes the sponsor firewall near-trivial, lightest DPDP burden. |
| **B2** | **Multi-user or single console?** Do clinicians/MDT members log in, have a panel and an inbox — or is "team" just a notify list? | Determines roles, inbox, and the whole collaboration model | Business | **Multi-user, role-based** (the role-based access decision already implies it) |
| **B3** | **Roles & MDT (simplified):** confirm **no `department`** — all clinical roles see the institution's patients, **HOD is the privileged role**, and the MDT panel is only a **notification group** (no access implication). Who manages MDT membership? | Determines roles, access model, and the "notify all" target | Clinical | **Clinician · HOD (privileged) · Admin** (Coordinator folded into Clinician). MDT = `is_mdt_member` flag, admin-managed. Each patient has one **primary clinician** (attribution, not restriction). |
| **B3b** | **Record locking:** confirm **edit window = 48 h**, **HOD unlock window = 24 h**, unlock **restricted to HOD** with a mandatory reason. Should Coordinator also unlock? | Determines the lock/unlock workflow + audit model | Clinical + Business | As stated. Append-only tiers need **no** unlock to continue care — unlock exists only to correct mistakes. |
| **B3c** | **Cardinality confirmation:** every model is either entered on a named screen or derived; **one treatment *plan* (1:1)** vs **many treatment *lines* (1:N)**; duplicates blocked by unique keys | Prevents duplicate/ambiguous rows; confirms no orphan layers | Clinical | Confirm the provenance/cardinality table (`PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md §1.7`) |
| **B4** | **Patient source of truth:** created in ProstaCare, or **synced from hospital HIS/registry**? If synced — match key (`patient_code`? UHID? ABHA?) and which fields are read-only | Determines onboarding flow, integration scope, and patient entity ownership | Business + IT | **Created in ProstaCare** for v1 (registry), keyed on `patient_code`; HIS sync as a later phase |
| **B5** | **Disease scope:** prostate only, or the first of several tumour frameworks? | Determines whether we build a shared clinical core + disease overlay, or a single-disease schema | Business | **Prostate first, on a templatable core** (so breast/lung can be added later without rework) |
| **B6** | **Confirm the v1 scope cuts** (`SIMPLIFICATION_REVIEW.md`): no snooze · no dismiss · **AI Buddy → Phase 2** · no SLA/escalation · no encounter · roles = Clinician·HOD·Admin · comorbidities stay as Yes/No flags | Removes ~7 entities and a whole AI subsystem from v1; nothing in FR/PRD/SCOPE requires them | Clinical + Business | **Confirm all cuts.** Each is unsupported by any stated requirement; each is cheap to add back later. |
| **B11** | **Clinical pathway gaps** (`CLINICAL_PATHWAY_GAP_ANALYSIS.md`): confirm the **11 gaps** — registration fields (religion/marital/education/occupation/tobacco), a **general lab record** (CBC/RFT/LFT/ALP/testosterone), **surgery** as a treatment line, **Pluvicto / Radium-223 radioligand therapy**, **structured adverse events**, **vital status + date of death** (without which Overall Survival cannot be computed), QoL, bone events, resource use, imaging response, support-service referrals | The registry cannot report OS/PFS/QoL or the sponsor's own therapy without these | Clinical | Add all; they are named registry capture points on the agreed pathway |
| **B12** | **Follow-up intervals by disease state** (curative q3–6m · mHSPC q3m · mCRPC q1–3m · Pluvicto q6w · survivors annual) — confirm, so the *"follow-up overdue"* nudge can be built | Introduces the first **time-based** rule; **restores the nightly check** (reverses T9) | Clinical | Confirm the intervals above |
| **B7** | **Sponsor:** confirm **NVS = Novartis**; their role (funder / data consumer / both); and the **independent clinical governance** that owns the rule pack (conflict-of-interest control) | Determines the aggregation contract, governance model, and consent basis | Business + Legal | Sponsor receives **de-identified aggregate only**; rule pack owned by an **independent clinical committee** with versioned sign-off; hard firewall |
| **B8** | **Clinical sign-off on the 8 care-gap rules** — conditions, severities, next-step wording — and the **benchmark targets** (ARSI 60%, PSMA 85%, bone protection 85%, MDT review 95%) | The care-gap engine is the core product; rules cannot be coded unsigned | Clinical | Confirm as specified in `PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md §4`; amend thresholds/wording as needed |
| **B9** | **Aggregation contract:** confirm the `metric_key` catalogue; **small-cell suppression threshold** (default **11**); institution shown as **anonymised code** vs named | Determines what `sponsor_metric` computes and exports | Clinical + Legal | Catalogue as spec'd; threshold **11**; **anonymised `institution_code`** |
| **B10** | **Launch institution + user roster + identity source:** which hospital(s) go first, the doctor/coordinator roster (name, specialty, role, email), and **Azure AD SSO vs email/local accounts** | Cannot provision a tenant or onboard users without it. No roster exists in any document today. | Business + IT | Start with **one institution**; SSO if available, else email/local. *(SES is already provisioned — no prerequisite.)* |

---

## 3. 🟠 P1 — needed within the first sprint (dev can start without)

| ID | Question | Owner | Recommended default |
|---|---|---|---|
| P1-1 | **Nudge ownership** — who is responsible when a gap fires? | Clinical | The patient's **primary clinician**; visible to all clinicians |
| P1-2 | *(cut from v1 — see B6)* SLA / escalation / snooze / dismiss | Clinical | **None in v1.** Nudges auto-resolve when the source field changes. Revisit if clinicians ask. |
| P1-3 | **Notification detail** — which triggers send email vs in-app only; any patient-facing comms? | Business | Send on event (no digest scheduler in v1); clinician-only, no patient-facing comms |
| P1-4 | **Edit permissions** — is editing gated by specialty? Should "notify all MDT" be restricted? | Clinical | **No specialty gating** in v1; restrict "notify all MDT" to **HOD** |
| P1-5 | **Cardinality confirmations** — `pathology` 1-per-patient (re-biopsy → new row), `outcome` 1-per-patient, **supportive-care dated** | Clinical | As recommended (dated supportive-care gives the bone-protection audit trail) |
| P1-6 | **Data migration** — greenfield, or import an existing registry at the launch site? | Business | Greenfield for v1 |
| P1-7 | **Rule governance mechanism** — clinicians tune severity/wording/thresholds in config; changing rule *logic shape* is a versioned engineering change. Acceptable? | Clinical | Yes (see `NOVAEDGE_ALIGNMENT_REVIEW.md` G2) |

---

## 4. 🟡 P2 — needed before go-live, not before dev

| ID | Question | Owner |
|---|---|---|
| ~~P2-1~~ | ~~SES prerequisites~~ — ✅ **ANSWERED:** THB's existing SES has a verified sender domain and production access | — |
| P2-2 | **Export mechanism & cadence** to Zygo Data Cloud — S3 push (recommended) vs pull API; nightly compute, weekly/monthly export | Business + Platform |
| P2-3 | **Consent / legal basis** for aggregate secondary use (DPDP Act; ethics committee if applicable) | Legal |
| ~~P2-4~~ | ~~Domain/hosting/residency/IP~~ — ✅ **ANSWERED:** **AWS Mumbai (`ap-south-1`)**; **THB provides** domain, hosting, infrastructure | — |
| P2-5 | **Clinical chart renderers** — PSA line, percentile bands, Kaplan-Meier (frontend work) | Platform |
| P2-6 | **Enum localisation** per site (RT facilities, referring centres) | Clinical |
| ~~P2-7~~ | ~~Deployment model~~ — ✅ **ANSWERED:** **one tenant per institution, with separation.** Per-doctor SaaS is not the model. | — |

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
| **B1 + B2 + B4 + B6** | **P0 Foundation** — tenancy, 3 roles, patient hub, 1:1 entities, record lock, onboarding console |
| **B1 + B6** | **P1 Longitudinal** — PSA, staging, imaging, treatment lines, supportive care, journey |
| **B8** | **P2 Care-gap engine** — the 8 rules, nudge lifecycle |
| **B3 + B10 + P2-1** | **MDT notify** (SES email) + user onboarding |
| **B7 + B9** | **Aggregation** — `sponsor_metric` + Zygo Data Cloud pipeline |
| **B5** | Schema core shape (single-disease vs templatable overlay) |

**Critical path:** **B1 (identity model)** gates everything. **B8 (rule sign-off)** gates the care-gap engine. **B10 (roster + auth)** gates the first tenant.

---

*Sources consolidated from: `FLOW-CLARITY-AND-OPEN-QUESTIONS.md`, `PROSTACARE_BUILD_SPEC_V1.md §12`, `PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md §7`, `NOVAEDGE_ALIGNMENT_REVIEW.md §4/§6`, `CROSS_TENANT_AGGREGATION_SPEC.md §6`, `TENANT_ONBOARDING_PLAN.md §6`.*
