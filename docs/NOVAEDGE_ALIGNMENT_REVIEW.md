# ProstaCare ↔ NOVA Edge — Architecture Alignment & Gap Review

**Purpose:** verify the ProstaCare canonical model + workflows (`PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md`, `PROSTACARE_BUILD_SPEC_V1.md`) map **seamlessly** onto NOVA Edge primitives (schemas, scopes, workflows, subscriptions/cron, materialized views, ADK agents), and to surface every gap before the preset build.

**Verdict:** **Strongly aligned.** Every entity maps to a NOVA Edge schema and every workflow to existing operators/triggers — no new platform primitive is required. There are **two items that need an explicit design decision/component** before it is truly "seamless" (cross-institution aggregation; rule-config encoding) and **three "encode-it-this-way" notes** (down from six after the `SIMPLIFICATION_REVIEW.md` trims closed G5/G6). All are called out below with resolutions. None is a blocker.

---

## 1. Entity → NOVA Edge schema mapping

Field types available: `string/text/integer/number/float/boolean/datetime/date/json/enum(enumValues)/uuid/phone/email/file/tags` + per-field `required/unique/indexed/default/references`. Enums → `enumValues`; FKs → `references`. *(Partitioning available but **not used in v1**.)* (Platform gotcha: use `datetime` not `date`.)

| Canonical entity | NOVA Edge construct | Notes / field-type mapping | Status |
|---|---|---|---|
| `app_user` (+`is_mdt_member`), `role` | entities + `roles.json` | 3 roles: Clinician · HOD · Admin. **No `department`/`care_team`/`mdt_panel`** — role-based access; tenant is the boundary | ✅ aligned |
| `patient` (hub) | canonical `patients` **extension** via PATCH | de-identified; enums for coverage/state/referral; **no `institution_id`** (tenant = institution) | ✅ aligned |
| `pathology` (1:1) | entity, FK→patient | enums (gleason/isup/pi-rads/dre); text for cores | ✅ aligned |
| comorbidity / family history | **15 boolean columns on `pathology`** | as in the workbook + chip-group UI; no separate table, no import transform | ✅ aligned |
| `treatment_plan` (1:1) | entity | enums + dates | ✅ aligned |
| `outcome` (1:1) | entity | enums + milestone dates | ✅ aligned |
| `psa_reading` (dated) | entity, indexed on `(patient_code, psa_date)` | **no partitioning in v1** (unnecessary at this scale) | ✅ aligned |
| `staging_assessment` (dated) | entity | enums (T/N/M/risk/ecog/castration) + `assessed_on` | ✅ aligned |
| `imaging_study` (dated) | entity | `modality` enum + `result` enum + `study_date` | ✅ aligned |
| `treatment_line` (dated) | entity | `line_type` enum; RT + CGHS fields on the RT line | ✅ aligned |
| `supportive_care_event` (dated) | entity | bone/dexa/phq9/follow-up + `at` | ✅ aligned |
| `journey_event` (dated) | entity | `event_type` enum | ✅ aligned |
| `nudge` | entity | `rule_id`, `severity`, `current_status`, dates | ✅ aligned |
| `nudge_event` | entity | lifecycle log (opened · acknowledged · resolved) for trend + audit | ✅ aligned |
| `notification` / `discussion_entry` | entities | recipients (json), delivery status | ✅ aligned |
| `document` | `file` field + attachment entity + object storage | S3/MinIO per `communication.json` | ✅ aligned |
| `guideline_rule` | **config entity** | `version` + `signed_off_by/at` + `active` (G2) | ✅ aligned |
| ~~`evidence_pack` / `guideline_pack`~~ | config entities | **Phase 2** (with AI Buddy) | ⏸ deferred |
| ~~`encounter`~~ | — | **not in v1**; visit timing derives from follow-up dates | ⏸ deferred |
| `audit_event` | platform `activity` + subscriptions | ensure full coverage (G7) | ✅ aligned |
| **record-lock fields** (`locked`, `locked_at`, `unlocked_until`, `unlock_reason`, `created_by`) | columns on every entered entity | drive W10; `unlock` gated on role | ✅ aligned |
| `sponsor_metric` | entity + scheduled `sql_exec` aggregation | de-identified, small-cell suppressed; exported to Zygo Data Cloud (G3) | ✅ aligned |
| `patient_identity` *(only if identified model)* | isolated entity + `read_roles`/`context_mask` | audited reveal | ✅ aligned |

---

## 2. Workflow → NOVA Edge mechanism mapping

Triggers: API run · entity `subscriptions` (on_create/update) · schema `policies` (cron) · webhook. Step types used: `create/upsert/query/sql_exec/branch/for_each/email/in_app_notification`. *(No `sse_publish`/`llm` in v1.)*

| Workflow | Trigger | Steps used | Status |
|---|---|---|---|
| W1 onboarding | Add-patient API → `on_create` sub | `create` + notify workflow (W7) | ✅ aligned |
| W2 workup/staging | save → `on_create` sub on staging/imaging | `upsert`(pathology) + `create`(dated) + fire W5 | ✅ aligned |
| W3 PSA capture | save → `on_create` sub | `create`; scheduled mat-view refresh | ✅ aligned |
| W4 treatment | save → `on_create` sub | `create`(line/supportive) + fire W5 | ✅ aligned |
| **W5 care-gap engine** | `on_write` subs (staging/imaging/treatment/supportive) — **no cron in v1** (all 8 rules are state-based; W10/W11 *do* use cron) | `sql_exec` `INSERT…SELECT…WHERE <rule> AND NOT EXISTS(open)` + `sql_exec` auto-resolve `UPDATE` | ✅ aligned — see G2 (rule encoding) + G4 (current-state) |
| W6 nudge lifecycle | Acknowledge API | `create`(nudge_event) + open W7 | ✅ aligned |
| W7 MDT notify | from nudge/patient | `query`(users WHERE is_mdt_member) + `for_each` + `email` (SES) + `in_app_notification` + `create`(discussion_entry). *No `sse_publish`, no auto-task, no digest in v1.* | ✅ aligned |
| W8 analytics | on-write + cron refresh | **materialized views** (RLS-scoped) + `reports` | ✅ aligned — see G1 (charts) + G3 (cross-tenant) |
| **W10 record lock / unlock** | `policies` cron (hourly auto-lock + auto re-lock) + `unlock` API | `sql_exec` UPDATE (auto-lock) · `branch` role-gate (HOD) + `create`(audit_event) on unlock | ✅ aligned |
| **W11 sponsor aggregation** | `policies` cron (nightly) | `sql_exec` INSERT…SELECT from de-identified mat-views + suppression `CASE` → `sponsor_metric` | ✅ aligned |
| ~~W9 AI Buddy~~ | user opens | ADK `agent` + read tools + evidence packs | ⏸ **Phase 2** (absent from functional requirements) |

---

## 3. Current-state derivation — the key encoding note (G4)

"Current stage / line / castration = latest dated row" is **cross-row**, which NOVA Edge **computed columns cannot do** (the `compute` DSL is string-composition only — no rollups). So current-state must be encoded as **either**:
- a **materialized view** `current_state` (one row/patient with the latest values), refreshed on write/cron — best for dashboards & header badges; **or**
- an **inline subquery** inside the care-gap engine's `sql_exec` (`… JOIN LATERAL (SELECT … ORDER BY assessed_on DESC LIMIT 1) …`) — best for the rules pass.

**Resolution:** use both — a `current_state` mat-view for UI/analytics, and lateral subqueries inside W5 for evaluation. Do **not** model current-state as a stored/computed column. *(Spec §2/§5 already treat it as derived; this pins the platform encoding.)*

---

## 4. Gaps & resolutions

| # | Gap | Why it matters | Resolution |
|---|---|---|---|
| **G1** | Chart renderers for **PSA line / percentile bands / Kaplan-Meier** | NOVA Edge chart subtype is a free string, but the concrete renderer lives in the frontend repo (`metadata-auto-ui`), unaudited | Confirm line/area exist; build KM as a custom renderer. Data/aggregation side is fully supported. **Frontend task, not a data-model gap.** |
| **G2** | `guideline_rule` as **data-driven config** vs one `sql_exec` per rule | Clinical team wants to edit rules without code | Recommended: `guideline_rule` config holds **metadata** (rule_id, severity, next_step, inputs, version, sign-off, active); the engine workflow holds **one predicate step per rule (8)**, gated by `active`. Clinicians tune severity/wording/thresholds in config; changing the *logic shape* is a versioned workflow edit. (Fully dynamic predicate-from-config is possible via stored SQL fragments + `tables` allowlist, but adds risk — defer.) |
| **G3** | **Cross-institution** de-identified reporting is **not native** (tenants are isolated schemas) | Sponsor/registry benchmarking spans hospitals | **Net-new component:** a cross-tenant **de-identified aggregation layer** (scheduled export of each tenant's de-identified cohort metrics → a registry store the sponsor reads). This is the one piece that isn't in-tenant config. Owner + cadence = open decision (`O-REP`). |
| **G4** | Current-state = latest row (cross-row) | Header badges + rule inputs | Mat-view + lateral subquery (see §3). Not a computed column. |
| ~~**G5**~~ | ~~Partitioning composite PK + lookback~~ | — | ✅ **CLOSED** — partitioning dropped from v1 (unnecessary at this scale). Gap was self-inflicted. |
| ~~**G6**~~ | ~~flag columns → normalized rows import transform~~ | — | ✅ **CLOSED** — comorbidity/family stay as boolean columns. Transform no longer exists. |
| **G7** | **Audit coverage** must be complete | R-AUTH-3; identity reveal | Cross-cutting `audit_event` subscription on all entities + explicit reveal audit on `patient_identity`. |

**None blocks the build.** G3 is the only genuinely net-new *component*; the rest are encode-it-this-way notes or a frontend task.

---

## 5. Alignment checklist

| Dimension | Status |
|---|---|
| Every entity → a NOVA Edge schema | 🟢 |
| Field types / enums / FKs / partitioning expressible | 🟢 |
| Tenancy = institution = one tenant schema | 🟢 |
| Department/role scopes (`row_policies` + `$user.department`) | 🟢 |
| De-identified analytics via RLS-scoped mat-views | 🟢 |
| Care-gap engine via `sql_exec` + on-write subs (no cron) | 🟢 (encode per G2/G4) |
| Nudge lifecycle + trend from `nudge_event` | 🟢 |
| MDT notify via comms steps | 🟢 |
| AI Buddy via bounded ADK agent | ⏸ Phase 2 |
| Onboarding = provision tenant per institution + seed preset | 🟢 |
| Record lock / HOD unlock (W10) | 🟢 |
| In-tenant `sponsor_metric` aggregation (W11) | 🟢 |
| Cross-institution de-identified rollup | 🟡 net-new component (G3) |
| Clinical chart renderers (line/KM) | 🟡 frontend confirm (G1) |

---

## 6. What must exist before/around the preset build

1. **Decide G2 encoding** (config metadata + per-rule predicate steps — recommended) so the clinical team's rule-governance need is met.
2. **Scope G3** (cross-tenant de-identified aggregation layer) — owner, store, cadence; it is the sponsor surface too.
3. **Confirm G1** (frontend line/KM renderers).
4. Pin **G4** current-state as mat-view + lateral subquery in the schema/workflow design.
5. Include **G7** audit subscription in the preset from day one. *(G5 and G6 are closed — see `SIMPLIFICATION_REVIEW.md`.)*

Everything else is standard NOVA Edge configuration: fork `novahub_v2`, add the entities (§1), the workflows (§2), the mat-views (§5/W8), the ADK agent (W9), scopes + roles, and the theme.

---

*Reviewed against: `NOVA-EDGE-FEASIBILITY.md` (platform capability findings), the `novahub_v2`/`sakra` presets, and platform docs (workflow-reference, materialized-views, column-compute-derivations, partitioning, rbac). Companion: `PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md`, `PROSTACARE_BUILD_SPEC_V1.md`.*
