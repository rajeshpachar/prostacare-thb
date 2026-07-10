# ProstaCare — Canonical Schema & NOVA Edge Build Spec (v1, for internal approval)

**Audience:** ProstaCare product/clinical leads + the NOVA Edge (NOVAGE) platform team, for internal sign-off **before** preset build starts.
**Derived from:** `ProstaCare_Schema_08072026_V2.xlsx` (the "Platform Bible" workbook — product narrative, 110-field dictionary, value lists, 46-widget dashboard inventory, care-gap tracker) + the prior discovery/feasibility docs in this folder (`FLOW-CLARITY-AND-OPEN-QUESTIONS.md`, `NOVA-EDGE-FEASIBILITY.md`, `PRODUCT-PRD.md`, `ProstaCare_Nudge_Logic_Handoff.md`).
**Goal:** define the *canonical data model, tenancy/onboarding model, rules/analytics/intelligence layers, and NOVA Edge mapping* — structured so it is easy to build and manage, with the workbook as one entry surface that maps onto the canonical schema (not the system of record).

---

## 1. Framing — what changed, and the one principle

The workbook is a **platform bible first, data-entry pack second** (its own words). It commits the product to a registry + patient command-centre + care-gap engine + cohort analytics + governed AI ("AI Buddy"), with a **core promise**: *every cohort signal drillable to a patient; every patient gap an explainable next action.*

That promise is only structurally possible if the data model is **longitudinal, computed, and tenant-aware** — which the workbook itself is not (it is a flat, de-identified, single-institution snapshot). So this spec does three things the workbook does not:

1. **Adds the tenancy/identity layer** (institution = tenant; users + roles inside it) so institutions and doctors can be onboarded.
2. **Promotes snapshot columns to longitudinal event tiers** (staging, imaging, treatment lines, nudges) so restaging, sequential therapy, and nudge-trend history become expressible.
3. **Makes every displayed number derived** (Tier 3), never typed — the workbook already flags this need in `Dashboard_Derived`/`Dashboard_Coverage`.

**Guiding principle (carried from PRODUCT-PRD R-X-5):** snapshot storage where the domain is longitudinal is the root cause of the demo's known bugs. The canonical model fixes them structurally (see §5.5).

---

## 2. Terminology — tenancy model (updated): **tenant = institution**

**Decision (confirmed): each onboarded institution is its own NOVA Edge tenant** (one Postgres schema per hospital). Therefore **no `institution_id` column is stored anywhere** — the tenant boundary *is* the institution, and every row already belongs to that institution. Inside a tenant there is **no department** — all clinical users see that institution's patients and access differs by **role** (Clinician · HOD · Admin).

| Reporting need | How it works under tenant-per-institution |
|---|---|
| Cross-**doctor** cohort reporting (within a hospital) | **Native** — one schema per institution |
| Cross-**institution** reporting (sponsor / registry / benchmarking) | A separate **de-identified aggregation layer above the tenants** — pushes de-identified cohort metrics up; matches "sponsor sees de-identified aggregate only" |
| "Each doctor/team isolated" (within a hospital) | **Not required** — all clinicians share access; HOD is the privileged role |
| Per-**doctor** dedicated tenant (internet SaaS, `O-DEP`) | Different again — not chosen; would isolate each doctor and needs the same de-identified layer to report across them |

> Net: cross-reporting splits into two — **within-institution** (native, in-tenant) and **cross-institution** (de-identified aggregation layer). The de-identified layer is also exactly the sponsor/pharma surface (§10), so it does double duty.

---

## 3. Foundational decisions (locked) + the one big open decision

**Locked (from prior discovery):**
- **Tenant = institution** (one schema per hospital); no `institution_id`, **no `department`**.
- Clinical operational visibility = **tenant-wide for clinical roles**; **HOD = privileged** (unlock, notify-all-MDT, audit).
- **Record lock:** edit window → auto-lock → HOD time-bound unlock.
- Non-clinical / ops / quality / **pharma sponsor = de-identified aggregate only** (PHI firewall).
- Care-gap rules = **config-owned, versioned, clinically signed-off**; 8 rules specified.

**🔴 The one decision to settle before build — identity model:**
The V2 workbook is **fully de-identified** (`patient_code` is "the only patient-level identifier permitted"; age-at-diagnosis not DOB; no name/ABHA/Aadhaar). The earlier demo patient-file was **identified** (names, ABHA, Aadhaar, masked-with-reveal). These are two different products. Pick one:

| Option | What it means | Consequence |
|---|---|---|
| **A. De-identified registry (recommended)** | ProstaCare stores **no PHI** — only `patient_code` + clinical data. Identity (name/ABHA) stays in the hospital HIS, linked externally by `patient_code`. | Massively simpler DPDP/consent; pharma firewall becomes near-trivial; matches V2 workbook. Bedside "who is this" needs the HIS. |
| **B. Identified EMR-lite** | ProstaCare stores identifiers, masked-by-default + audited reveal. | Full bedside usability; heavy PHI/consent/audit burden; contradicts the V2 workbook. |
| **C. De-identified core + optional identity module** | De-identified registry by default; an optional, separately-scoped `patient_identity` entity (name/ABHA) available only to in-scope clinical roles at an institution that needs it. | Best of both; slightly more design. **Fallback recommendation if B is wanted anywhere.** |

**Recommendation: A (or C if any site needs bedside identification).** Everything below is written so that identifiers, if kept, live in **one** isolated `patient_identity` entity — the rest of the model stays de-identified regardless.

---

## 4. Canonical data model (three tiers + tenancy + cross-cutting)

Legend for cardinality: **1:1** = one row per patient (current-state) · **1:N dated** = many dated rows per patient (longitudinal) · **derived** = computed, never typed.

### 4.0 Tier 0 — Tenancy & identity (NEW; absent from workbook)
> **Tenant = institution.** The institution is the tenant boundary, so there is **no `institution` entity and no `institution_id`**. **There is also no `department` entity** — access differs by **role**, not department; all clinical users see that institution's patients. The MDT panel is a **notification group, not an access boundary**.

| Entity | Cardinality | Key fields | Notes |
|---|---|---|---|
| `app_user` | — | id, display_name, **email (login identity)**, specialty, role→, status | Clinician / HOD / Coordinator / Ops / Admin |
| **record-lock fields** | on every entered entity | `created_at`, `created_by`, `last_edited_at`, `locked`, `locked_at`, `unlocked_until`, `unlock_reason` | Edit window → auto-lock → HOD time-bound unlock (functional spec §1.8 / W10) |
| `role` | config | **Clinician · HOD (privileged) · Admin** *(+ Ops/Quality only if in-product de-identified dashboards are needed)* | Drives capability matrix (§10) |
| MDT membership | **flag on `app_user`** | `is_mdt_member` (boolean) | Notify-all target. *No `mdt_panel` table* — MDT is a notification group, not an access boundary. |
| Primary clinician | field on `patient` | `primary_clinician_id→` | Attribution, not restriction. *No `care_team_member` table in v1.* |
| `patient_identity` *(only if §3-B/C)* | 1:1, isolated | patient_code→, name, abha, aadhaar_masked, phone | The **only** PHI table; column `read_roles`+`context_mask`; audited reveal |

### 4.1 Tier 1 — Patient hub & current-state (1:1 per patient)
| Entity | Source sheet/section | Key fields (from Field_Dictionary) |
|---|---|---|
| `patient` (hub) | Demographics_Entry + `diagnosis_date` moved here | patient_code (PK), primary_clinician_id→, registry_enrolment_date, age_at_diagnosis_years, language_preference, healthcare_coverage, referring_hospital_centre, referral_source, state, travel_distance_km, diagnosis_date *(no institution_id — tenant = institution)* |
| `pathology` | Clinical_Entry · Presenting Complaint + DRE + Biopsy | primary_complaint, duration, ipss_score, bowel_rectal_symptoms, dre_findings, prostate_volume_cc, biopsy_date, biopsy_type, pi_rads_score, gleason_score, isup_grade_group, cores_positive_total, core_involvement_pct, perineural_invasion, ece_extracapsular_extension — **1:1** (re-biopsy → new row + journey event) |
| comorbidity / family history | Clinical_Entry · comorbidity_1..9 + family_history_1..6 | **Kept as 15 boolean flag columns on `pathology`** (exactly as the workbook and the chip-group UI). *No `patient_condition` table* — the list is fixed and the cohort pivots are trivial SQL over booleans. |
| `treatment_plan` | Treatment_Entry · Intent & MDT | treatment_intent, mdt_tumour_board_status, date_of_mdt_review, clinical_trial_eligibility, treatment_start_date — **1:1** header |
| `outcome` | Outcomes_Entry | last_follow_up_date, best_response, psa_nadir_value, psa_nadir_date, psa_doubling_time_months, biochemical_recurrence_status/date, crpc_progression_status/date, rt_outcome_status — **1:1** (milestone dates inline) |

### 4.2 Tier 2 — Longitudinal events/observations (1:N dated)
| Entity | Source | Key fields | Why longitudinal |
|---|---|---|---|
| `psa_reading` | PSA_History (already correct) | psa_date, psa_ng_ml, free_psa_pct, psa_density, context_remarks | Trend/response curves; **partition on `psa_date`** |
| `staging_assessment` **(NEW)** | Clinical_Entry · TNM Staging & Risk | **assessed_on**, clinical_t_stage, n_stage, m_stage, eau_risk_category, ecog_performance_status, castration_status | Restaging + HSPC→CRPC transition as dated facts; "current stage" = latest by `assessed_on` |
| `imaging_study` **(NEW)** | Clinical_Entry · Imaging & Molecular | **study_date**, modality {mpMRI, bone_scan, psma_pet_ct, ct_ap, dexa, germline_somatic}, result | "is PSMA done / is DEXA current" is time-sensitive (feeds care-gap engine) |
| `treatment_line` **(NEW)** | Treatment_Entry · ADT + Chemo + RT | line_type {ADT, anti_androgen, ARSI, chemo, RT}, agent, formulation_dose, start_date, end_date, status; + RT: rt_indication/status/modality, target_volume, dose_fractionation, rt_facility, planned_rt_start_date, rt_completion_date, cghs_preauth_status/request_date/approval_date; + testosterone_level, safety_side_effects | Expresses **sequential therapy** (ADT → progression → ARSI → chemo) the flat sheet can't |
| `supportive_care_event` | Treatment_Entry · Bone Health & Supportive Care | **at**, bone_protection_therapy, calcium_vitamin_d, next_follow_up_psa_date, testosterone_monitoring, psychosocial_screening_phq9, nutritional_assessment | Dated so bone-protection start/stop has an audit trail (largest care gap) |
| `journey_event` | Journey_Events (already correct) | event_type, event_date, event_notes | Human-readable milestone narrative (no longer the system of record for clinical state) |
| `nudge` **(NEW)** | Care_Gap_Tracker (restructured) | nudge_id, patient_code→, rule_id, severity, current_status {open/logged/resolved/dismissed}, guideline_ref, opened_at, resolved_at | A gap is a lifecycle object, not a flag |
| `nudge_event` **(NEW)** | — | nudge_id→, at, action {opened/viewed/acknowledged/routed_to_mdt/resolved}, actor→ | The event log that makes nudge-trend + closure audit computable (workbook flags this as impossible without it) |

### 4.3 Tier 3 — Derived / analytics (computed, never typed)
Materialized, RLS-scoped; refresh on cron. Covers the whole `Home_Dashboard` + `Population_Dashboard` inventory (see §7) plus:
- `current_stage` / `current_line` / `current_castration_status` (latest-row projections for header badges)
- `protocol_score`, `record_completeness`, benchmark deltas (ARSI/PSMA/bone/MDT), gap counts & severity rollups
- `nudge_trend` (opened/viewed/acted/resolved/net-active) from `nudge_event`
- All 22 derived fields enumerated in the workbook's `Dashboard_Derived` tab

### 4.4 Cross-cutting
| Entity | Source | Purpose |
|---|---|---|
| `notification` / `discussion_entry` | Team modal + workflow | MDT notify + per-patient discussion log; sender, recipients, reason, body, delivery status, audit |
| `document` | Rx upload workflow | Prescription/report blobs → secure object storage refs + metadata + audit |
| `audit_event` | cross-cutting | Every view/edit/reveal/nudge-action/notification (R-AUTH-3) |
| `guideline_rule` | config | The 8 care-gap rules as versioned, signed-off config (§6) |
| ~~`evidence_pack` / `guideline_pack`~~ | config | **Deferred to Phase 2 with AI Buddy** (absent from the agreed functional requirements) |

**Notifications & email (AWS SES).** Identity = **email** (users log in with their email ID). The MDT-notify workflow (functional spec W7) sends every configured notification via **AWS SES**: resolve recipients → in-app inbox item (+task) → **SES email** to `recipient.email` → store SES `messageId` + delivery status (sent/bounced/complaint/failed) on `Notification` → append discussion log. NOVA Edge encoding: the workflow `email` step is backed by an **SES integration** (verified sender domain; credentials in `system_integrations`); in-app via `in_app_notification` + `sse_publish`. SMS/WhatsApp are future channels behind the same `Notification` record. Triggers covered: care-gap→MDT, new patient, discuss-with-team, urgent escalation.

---

## 5. Sheet → entity migration map

| Workbook sheet | Target entity(ies) | What moves / changes |
|---|---|---|
| `Demographics_Entry` | `patient` (hub) | Keep 1:1. Make `patient_code` a real PK with FK integrity. Move `diagnosis_date` here. Add `primary_clinician_id` FK. *(No institution/department FKs — tenant = institution.)* |
| `Clinical_Entry` | **splits into** `pathology` (1:1, incl. comorbidity/family flags) + `staging_assessment` (1:N dated, **NEW**) + `imaging_study` (1:N dated, **NEW**) | The single sheet holding several lifecycles is decomposed by lifecycle. Staging & imaging become dated events. |
| `PSA_History` | `psa_reading` | Structurally correct already; partition on date; **the Patient-File chart binds to this table** (closes the decoupled-chart bug). |
| `Treatment_Entry` | `treatment_line` (1:N dated, **NEW**) + `treatment_plan` (1:1 header) + `supportive_care_event` (1:N dated) | One mashed row → dated therapy lines + a small current-state header + dated supportive care. |
| `Outcomes_Entry` | `outcome` (1:1, milestone dates inline) | Keep 1:1; milestone dates already present. |
| `Journey_Events` | `journey_event` | Keep. Role narrows to milestone narrative (staging/treatment now have their own history). Wire the "Add to Timeline" action. |
| `Care_Gap_Tracker` | `nudge` + `nudge_event` (**NEW**) + derived read-model | Flag sheet → lifecycle. All counts/severity become **derived** over `nudge`. |
| `Home_/Population_Dashboard`, `Dashboard_Derived`, `Dashboard_Coverage` | Tier-3 materialized views | Inventory → mat-view specs (§7). |
| *(none)* | `app_user` (+`is_mdt_member`), `role`, `notification`/`discussion_entry`, `document`, `audit_event`, `guideline_rule`, `sponsor_metric` | Net-new — the workbook has no home for these (the signal it's an entry surface, not the system of record). *(No `institution`, `department`, `care_team`, `mdt_panel`, `patient_condition`, or `encounter` entities — see `SIMPLIFICATION_REVIEW.md`.)* |

### 5.5 Bugs that close as a consequence of the migration
| Demo bug (PRODUCT-PRD §6) | Root cause | Closes because |
|---|---|---|
| Decoupled PSA chart (§6.6) | chart read hardcoded points | chart binds to `psa_reading` |
| Static-vs-computed KPI drift (§6.5) | hand-typed metrics | Tier-3 is derived-only (R-X-5) |
| Nudge-trend needs history | one-row snapshot | `nudge_event` exists |
| Restaging / HSPC→CRPC not expressible | staging overwrites | `staging_assessment` is dated |
| Sequential therapy not expressible | one mashed treatment row | `treatment_line` is dated |

---

## 6. Care-gap rules engine (config-owned, 8 rules)

The 8 rules are fully specified (workbook `Care_Gap_Tracker` + `ProstaCare_Nudge_Logic_Handoff.md`). Each becomes one `guideline_rule` config row + a condition in a parameterized evaluation workflow. Inputs read from **current-state projections** of Tier-2 (latest staging/imaging/treatment/supportive-care).

| rule_id | Condition (against current state) | Severity |
|---|---|---|
| bone_scan_missing | `bone_scan=Not done` AND risk ∈ {High, Very High, M1} | Urgent |
| psma_missing | `psma_pet_ct=Not done` AND risk ∈ {High, Very High} | Urgent |
| bone_protection_missing | `bone_protection_therapy=Not started` | Urgent |
| dexa_missing | `dexa=Not done` | Warning |
| genomics_missing | `germline_somatic=Not done` | Warning |
| arsi_readiness | `castration=HSPC` AND risk ⊇ High AND `arsi=Not initiated` | Warning |
| followup_psa_missing | `next_follow_up_psa_date` empty | Info |
| psychosocial_prompt | `phq9` blank or Not done | Info |

**Evaluation:** workflow `sql_exec` scan `INSERT…SELECT…WHERE <rule> AND NOT EXISTS(open nudge)` (idempotent) bound to (a) `on-write` subscriptions of staging/imaging/treatment/supportive entities and (b) a daily `policies` cron. **Auto-resolve** when the source condition clears (matches the demo semantic: acknowledge ≠ resolve). Rules are **versioned + clinically signed-off**; the sponsor never edits them (governance §8/§10).

---

## 7. Analytics & derived layer (dashboard inventory → mat-views)

The workbook's `Population_Dashboard` (36 widgets across Overview/Clinical/Treatment/Outcomes/Quality/Demographics) + `Home_Dashboard` (23 widgets) map to RLS-scoped materialized views. `Dashboard_Derived` (22 derived fields) and `Dashboard_Coverage` (covered/partial/not) are the authoritative derivation list. Highlights:

- **Covered by the canonical model:** registration trends, age histogram, referral donut, travel bands, risk/coverage/stage mixes, Gleason/ISUP, comorbidity pivot, ADT/RT/ARSI landscapes, CGHS delay, time-to-treatment, outcome cards, KM survival, bone-health donut, completeness, MDT rate.
- **Previously "not representable" — now solved by Tier-2:** **nudge-trend lifecycle** (via `nudge_event`), and per-user **recently-viewed** (via `audit_event`). The workbook explicitly listed these as impossible on snapshot rows.
- **Drill-to-patient everywhere:** every widget resolves to the underlying `patient_code` set (the core product promise). For non-clinical/sponsor roles the drill lands on **de-identified/masked** rows (§10).
- **Chart types:** NOVA Edge chart subtype is a free-form string (line/percentile-band/KM not precluded); confirm/extend the frontend renderers for the PSA line, percentile bands, and Kaplan-Meier (the one custom viz). See NOVA-EDGE-FEASIBILITY §7.1/G1.

---

## 8. Governed Intelligence — AI Buddy (⏸ **DEFERRED TO PHASE 2**)

> **Scope decision:** AI Buddy appears **zero times** in `FUNCTIONAL_REQUIREMENTS.md`, `PRD.md`, or `SCOPE.md` — it exists only in the newer workbook. It is the single largest subsystem in this spec and is **not required for v1**. Ship registry + care-gap engine + dashboards first. The design below stands for Phase 2. *(`SIMPLIFICATION_REVIEW.md` T12.)*

The workbook's `Governed_Intelligence` tab defines a strict boundary: AI Buddy is **stepwise, evidence-anchored, and must not free-generate, invent gaps, claim autonomous decisions, or imply drug access the config denies.** Mapping to NOVA Edge:

- **AI Buddy** → an ADK `agent` in `chat`/stepwise mode, tools limited to **read** entities + report tools + the care-gap engine; **no unbounded generation**.
- **Brain = configured packs only:** `evidence_pack` / `guideline_pack` / access-rule config / retrospective aggregates — no external free-text.
- **Four lenses** (pathway review, progression branch, access/affordability, trial/new-drug) → distinct tool-scoped prompts, each grounded in config + patient state.
- **Guardrails:** `require_human_approval` on any write; `sanitize` on inputs; PII kept out of prompts via `context_mask` (moot under the de-identified model §3-A). Every AI step is audited.
- **Governance/COI:** because a pharma sponsor may have commercial interest in flagged therapies, the evidence/guideline packs and the 8 rules are owned by an **independent clinical committee** with versioned sign-off; AI Buddy can only surface what those packs contain.

---

## 9. Multi-institution onboarding & provisioning

Since the workbook has no tenancy layer, onboarding is net-new. Because **tenant = institution**, onboarding a hospital = provisioning its tenant, then setting up its users:

```
Platform admin → PROVISION institution tenant (new schema, seed preset, theme)
Institution admin (in-tenant) → onboard app_users (clinicians / HOD / admin)
      → assign role (Clinician · HOD · Admin) + set is_mdt_member
      → (per patient) set primary_clinician
Patient registry entry (Add New Patient) → appears in that institution's cohort
```
Cross-institution rollup (sponsor/registry) reads the **de-identified aggregation layer** above tenants, never the tenants directly.

- **Identity source (`O-ONB4`, open):** hospital SSO (Azure AD — NOVA Edge supports it) or platform-local accounts; confirm per institution.
- **Onboarding roster (`O-ONB`, open):** no predefined doctor-team list exists in any doc — must be supplied per launch institution.
- **Provisioning mechanism:** admin console (NOVA Edge `pages.json` + entity CRUD) for v1; bulk import / HIS-directory sync later.
- **Patient onboarding:** created in ProstaCare (registry) OR synced from HIS (`O-S1`, open) — under the de-identified model, sync carries `patient_code` + clinical data only.

---

## 10. Access, privacy & the pharma firewall (NOVA Edge encoding)

| Layer | Decision | NOVA Edge mechanism |
|---|---|---|
| Operational visibility | **Tenant-wide for clinical roles** (no department scoping); HOD is the privileged role | role grants only; the tenant *is* the boundary — no row-level scopes needed |
| Record immutability | Edit window → auto-lock → **HOD-only, time-bound unlock** (reason required, audited) | lock fields + scheduled `auto_lock` workflow + `unlock` workflow gated on role |
| Non-clinical / ops / sponsor | De-identified aggregate only | Exposed **only** to RLS-scoped, **de-identified** materialized views; no entity-row access |
| Identifiers (if §3-B/C) | Masked-by-default + audited reveal | isolated `patient_identity`; column `read_roles` + `context_mask`; reveal → `audit_event` |
| Rules/AI governance | Independent clinical sign-off; sponsor can't edit | `guideline_rule`/`evidence_pack` write-restricted to Admin+clinical-committee role |
| Data residency / consent | India (DPDP) | India-region hosting; consent basis per §3 decision (de-identified ⇒ lightest) |

Capability × role matrix is in `FLOW-CLARITY-AND-OPEN-QUESTIONS.md §5` (straw-man, pending confirmation).

---

## 11. NOVA Edge build mapping & phasing

**Preset deliverable** (`presets/prostate_cancer/`): `schemas.json` (all Tier-0/1/2 entities + partitioning on `psa_reading`), `workflows.json` (nudge evaluation + MDT notify + onboarding + outcome derivations), `tools.json`/`agents.json`/`agent-tools.json` (AI Buddy + evidence packs), `pages.json` + `ui/schema_ui.json` (Home, Patient List, Patient File detail, Population Dashboard, admin console), `mat_views.json` (Tier-3 + dashboard inventory), `reports.json`, `roles.json`, `config.json`, `app_theme.json` (Visual Language palette), `sample-data.json` (the workbook's de-identified sample rows).

**Reuse:** fork `novahub_v2` (care-gap/clinical) for the entity+care-gap spine; `b2b_account` detail-page pattern for the Patient File; canonical `patients` extension for the hub.

**Phasing:**
| Phase | Scope | NOVA Edge |
|---|---|---|
| **P0 Foundation** | Tenancy + patient hub + Tier-1 current-state + de-identified access | schemas + scopes + roles + onboarding console |
| **P1 Longitudinal** | PSA, staging, imaging, treatment-line, journey, supportive-care | Tier-2 entities + partitioning + current-state projections |
| **P2 Care-gap engine** | 8 rules (**on-write only, no cron**) + nudge/nudge_event lifecycle + MDT notify (SES) | `guideline_rule` + evaluation workflow + notify workflow |
| **P3 Analytics** | Home + Population dashboards, benchmarks, protocol score | mat-views + `pages.json`; confirm line/KM renderers (G1) |
| **P4 Governed AI** *(Phase 2)* | AI Buddy bounded agent + evidence packs | ADK agent + packs + guardrails |
| **P5 Integrations** | HIS/registry sync, FHIR read, (later) ABHA/ABDM | adapters/remote entities (net-new, see feasibility §4) |

---

## 12. Open decisions for NOVA Edge sign-off (the gate)

**P0 — settle before P0 build:**
1. **Identity model (§3):** de-identified registry (A) / identified (B) / de-identified + optional identity module (C). *Recommend A or C.*
2. **`O-A1` multi-user vs single console** — the role-based access model implies multi-user; confirm.
3. **`O-T*` roles & MDT (simplified)** — confirm roles = Clinician · HOD · Admin, MDT = `is_mdt_member` notify flag, no department, no care-team table.
4. **`O-S1` patient source of truth** — created in ProstaCare vs synced from HIS (key = `patient_code`?).
5. **`O-PH1/2/3` pharma** — confirm sponsor (NVS = Novartis?), data model (de-identified aggregate), and independent rule-governance/COI.
6. **`O-TMPL1` disease scope** — prostate-only vs templatable core (recommend: prostate on a shared oncology core).

**P1 — needed during build:**
7. `O-ONB` onboarding roster + `O-ONB4` identity source (SSO vs local) per launch institution.
8. `O-N*`/`O-CH*` nudge ownership, SLA/escalation, snooze; notification channels (in-app/email/…).
9. Supportive-care & pathology cardinality: keep `pathology` 1:1 (re-biopsy rare) ✅ recommended; make `supportive_care` **dated** ✅ recommended (bone-protection audit).

**P2 — refinement:**
10. `O-REP*` reporting grain/destination + de-identified export cadence for the sponsor.
11. `O-DOM*` domain/hosting/IP; chart-renderer scope (G1); FHIR/ABHA/ABDM connector timing (feasibility §4).

---

## 13. Why this is easier to build and manage

- **One canonical schema, three tiers** — snapshot for current-state, dated events for history, derived for everything shown. No hand-typed metrics, no snapshot/longitudinal contradictions.
- **The workbook stays useful** — as a de-identified *entry/seed surface* and the authoritative *field dictionary + value lists*, mapping cleanly onto the canonical entities (§5).
- **Tenancy is explicit** — institutions/doctors onboard into org-units + scopes; cross-reporting native; PHI firewall structural.
- **Rules & intelligence are config** — versioned, signed-off, sponsor-safe; the engine is data, not code.
- **Everything traces to `patient_code`** — so the core promise (drill any signal to a patient, explain any gap) holds structurally.

---

*Authoritative sources: `ProstaCare_Schema_08072026_V2.xlsx` (Field_Dictionary, Value_Lists, dashboard inventory, Care_Gap_Tracker). Companion specs in this folder: `NOVA-EDGE-FEASIBILITY.md`, `FLOW-CLARITY-AND-OPEN-QUESTIONS.md`, `PRODUCT-PRD.md`, `ProstaCare_Nudge_Logic_Handoff.md`. This document is the consolidated build spec for NOVA Edge internal approval; the preset build begins once §12 P0 items are signed off.*
