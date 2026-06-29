# ProstaCare India on nova-edge-pg — Feasibility & Mapping

**Question:** Can the `nova-edge-pg` platform power the ProstaCare India product (per `PRODUCT-PRD.md`)?

**Verdict: Yes — strong fit (high feasibility).** Standing up ProstaCare as a tenant/preset is **pure JSON configuration, zero Go**. ~80% of the product (records, dashboards, RBAC, PII masking, notifications, document handling, care-gap lifecycle, audit, search) is configuration on top of canonical entities and existing presets. The net-new engineering concentrates in three areas: an **MDT/tumour-board** concept (doesn't exist on the platform), the **guideline rule evaluation** (you build it — as in-platform workflows or upstream), and **India health-system connectors** (ABHA/ABDM are absent; FHIR is data-model-aligned but has no wire connector).

> **This revision is grounded in a deep read of the platform's own requirement docs and source**, not just the presets. It corrects three claims in the first draft (see §0). Sources: `docs/guides/{feature-development-guide, tenant-and-preset-setup, column-compute-derivations, materialized-views, workspaces-pages-frontend, reporting-complete-guide, his-integration-playbook}.md`, `docs/ingestion/{care-gap-prd, pg-ingestion-prd}.md`, `docs/integrations/bayanaty-care-gap-{frontend-prd,handshake}.md`, `docs/facades/his-v1.md`, `docs/ai/partitioning_brd.md`, `docs/remote-integration/remote-entity-integration.md`, and `internal/types/schema.go`.

---

## 0. Corrections from the deep doc review (vs first draft)

| First-draft claim | Verdict after reading platform docs | Corrected position |
|---|---|---|
| "No column-level computed/derived fields" | **Wrong** | Shipped `compute` DSL (PR #526/#527) — stored, Go-evaluated at write, authored as JSON on **canonical** schemas. Limited to string composition (`concat_ws`, `coalesce`, `template`, transforms), **no arithmetic/rollups/cross-entity lookups**. So `display_id = "P-"+last6(uhid)` is config; `adt_months = now()-start_date` still needs a workflow/materialized view. |
| "Charts limited to bar/pie/donut; no line/time-series" | **Unsubstantiated** | No such enum exists in the platform. Widget types are `chart / table / metrics / recent_records`; chart **subtype is a free-form string** with `xAxis`/`yAxis[]`. Line/area/time-series are **not precluded** — the actual renderer set lives in the separate frontend repo (`metadata-auto-ui`), which wasn't audited. **Re-scope G1 as "confirm/extend the frontend chart renderers," not "the platform can't do line charts."** |
| "The care-gap rules engine already ships" | **Half-right — important nuance** | The shipped care-gap product is an **ingestion + lifecycle + execution** system; it consumes **pre-computed** gap decisions from an upstream DataLake "ledger" and is explicitly *"NOT a rules engine"*. **However**, the workflow engine *is* capable of computing rules in-platform (the `b2b_aplus_neglect_alert` `sql_exec` scan pattern). So ProstaCare has two valid options for nudges (§2 F-Nudges). |

Net effect of the corrections: feasibility went **up**, not down — computed fields and richer charts are available, and the build is pure config. The real gaps narrowed to MDT, the guideline logic itself, and India connectors.

---

## 1. Why it fits

nova-edge-pg is a **multi-tenant, config-driven entity + workflow + AI platform** (Go + PostgreSQL): one tenant = one Postgres schema + one preset (a folder of JSON files seeded over REST). Every concern ProstaCare needs is authored as JSON:

| nova-edge concern | Preset file / mechanism | ProstaCare use |
|---|---|---|
| Data model (entities, fields, FKs, indexes, RLS, audit, search, **computed cols**, partitioning) | `schemas.json` + canonical entities | Patient record, PSA series, staging, treatment, nudges, documents |
| Business logic / rules | `workflows.json` (24 operators) | **Nudge / care-gap engine** (workflow `sql_exec` scan) |
| Care-gap ingestion + lifecycle | shipped care-gap subsystem | open→closed gap tracking, dedup, audit (if decisions come from upstream) |
| AI agents (ADK) + tools | `agents.json`, `tools.json`, `agent-tools.json` | Clinical AI assist on a record |
| Notifications (email/SMS/in-app/realtime) | workflow steps + `communication.json` | **MDT notify** (the routing; MDT *concept* is net-new) |
| Dashboards (KPIs, charts, filters) | `pages.json` widgets | Population analytics |
| Per-entity screens (detail/tabs/forms/lists) | `ui/schema_ui.json` | Patient File (multi-section detail page) |
| Analytics aggregation (RLS-scoped) | `reports.json`, `mat_views.json` | Cohort metrics, benchmarks, completeness |
| RBAC + row-level + field-level + PII masking | `roles.json`, schema `scopes`/`row_policies`, column `read_roles`/`context_mask` | Department vs own-panel scope, privacy masking |
| External integration (HIS adapter, virtual entities) | `integrations.json`, `his.Adapter`, `remote_config` | Hospital HIS, labs, FHIR (read) |
| Tenant identity & theming | `config.json`, `settings.json`, `app_theme.json` | ProstaCare branding/theme |
| Scheduling | schema `policies` (cron), subscriptions, supervisor jobs | Daily care-gap re-scan, overdue follow-ups |

**Start from a clinical preset.** Closest forks: `novahub_v2` (care-gap/population-health: patients, open/closed care-gaps, orders, clinical profiles, `patient_trend` lab time-series, ingestion workflows) and/or `hospital_crm` + `diagnostic_lab`. Canonical `patients`/`appointments`/`doctors` entities (FHIR-aligned) arrive automatically on bootstrap; ProstaCare only adds oncology extensions (PSA, Gleason, staging) via PATCH.

---

## 2. ProstaCare feature → nova-edge mechanism (the mapping)

### F-Record (Patient File) → entities + `ui/schema_ui.json` detail page
- **Entities:** extend canonical `patient` (ABHA/UHID/Aadhaar/CGHS) + child entities FK'd to patient: `psa_result`, `biopsy`, `staging` (TNM/Gleason/ISUP via `enumValues`, one row per assessment), `imaging_workup`, `treatment`, `journey_event`, `attachment`.
- **PSA / lab time-series:** model as a row-per-observation entity, **RANGE-partitioned** on the observation date (partitioning is shipped in code: `PartitionConfig{Type,Column,Interval,Retention}`). Composite PK `(id, observed_at)` required; watch the `LookupLookback` caveat (old rows pruned from plain ID lookups — fine for time-series queries).
- **Computed fields:** string-composition derivations (e.g. `display_id = "P-"+last6(uhid)`, `full_name`) via the `compute` DSL on canonical schemas — no code. Numeric derivations (ADT months, PSA doubling time) → materialized views or workflow steps.
- **UI:** model the Patient File on the proven `b2b_account` 360° detail page — header (name/status + role-gated + `type:workflow` action buttons like "Flag for MDT review") + `tab_container` (Demographics / Clinical / Treatment / Journey / Documents) + `associated_entity_list_view` child lists + `timeline`.

### F-Nudges (Decision Support) → **two valid options**
The platform's shipped care-gap product is *ingestion/execution*, not clinical rule evaluation. ProstaCare can go either way:

- **Option A — compute nudges in-platform (recommended for self-contained product).** Author one workflow per guideline using the proven `sql_exec` scan idiom (`b2b_aplus_neglect_alert`):
  ```sql
  INSERT INTO nudge (id, patient_id, type, rule_id, severity, status, ...)
  SELECT gen_random_uuid(), p.id, 'bone_protection', 'NCCN_BONE', 'urgent', 'open', ...
  FROM patient p
  WHERE p.risk_tier IN ('high','very_high') AND p.adt_months >= 3 AND p.bone_protection IS NULL
    AND NOT EXISTS (SELECT 1 FROM nudge n WHERE n.patient_id=p.id
                    AND n.rule_id='NCCN_BONE' AND n.status NOT IN ('resolved','dismissed'))
  ```
  `NOT EXISTS` = idempotent dedup; bind to a schema `policies` cron (daily re-scan) and/or record `on_update` subscription with a `branch` for real-time. Conditional grammar supports `eq/ne/gt/gte/lt/lte/contains/in/and/or` — every demo nudge rule is expressible. Encapsulate as one parameterized rules workflow + a `guideline_rule` config entity so clinicians edit data, not SQL.
- **Option B — ingest pre-computed gaps** via the shipped care-gap pipeline (`ingestion_staging` → `gap_ingestion_batch_processor` → `care_gap_tasks`, with dedup/audit/auto-close). Choose this only if the guideline evaluation lives in an upstream DataLake/ETL.
- ⚠️ Either way the **clinical guideline logic is yours to author/own** — the platform does not ship NCCN/EAU prostate rules.

### F-MDT (Notify & Discussion) → notification workflows **+ a net-new MDT model**
- **Notification routing is config:** nudge `on_create` (with `fire_subscriptions:true`) → workflow that resolves recipients (`sql_exec`/`dispatch`/`assign_user` over `users`/team config) → `for_each` → `email` + `in_app_notification` + optional `sse_publish` (live inbox). Comms templated inline in workflow JSON.
- ⚠️ **There is no MDT / tumour-board / multi-clinician-review concept anywhere on the platform** — entity, workflow, or screen. This is **net-new**: model `mdt_review` + `mdt_participant` + `discussion_entry` entities, a review-status lifecycle, and the discussion-log UI (a `related_list` on the patient page). The notification plumbing exists; the collaborative review object does not.

### F-Analytics (Population dashboard) → `pages.json` + `mat_views.json` + `reports.json`
- KPI cards = `metric` widgets; breakdowns = `chart` widgets; cohort tables = `reports.json` joins (INNER/LEFT/RIGHT, group_by, count/sum/avg/min/max).
- Cohort math (risk mix, ARSI %, completeness %, benchmark deltas, CGHS delay) lives in **materialized views** (SQL with CTEs/FILTER/percentages), cron-refreshed, **RLS-scoped (deny-by-default for non-admins as of 2026-06)**.
- **Chart types:** `chartType` is a free-form string with `xAxis`/`yAxis[]` — PSA-over-time line, percentile bands, etc. are not precluded by the platform; confirm/extend the renderer in the frontend repo (`metadata-auto-ui`). Kaplan-Meier survival is the one genuinely custom viz.
- **Drill-to-patient:** widget/CTA `action:'navigate'` + list `link_to_detail` → patient detail page.

### F-Auth/RBAC/Privacy → roles + scopes + field security + PII masking (all config)
- **Roles** (`roles.json`) with inheritance gating CRUD, features, routes.
- **Department vs own-panel:** schema `scopes`/`row_policies` with server-populated `$user.id`/`$user.teams` (e.g. `MY_PATIENTS = doctor_id eq $user.id`). Fail-closed on unresolved placeholders (PHI-safe; note known issue #668 on `$user.attributes.*` literal leak).
- **Field-level PII:** column `read_roles`/`update_roles` (exact-match, no inheritance) excludes sensitive columns from the response.
- **Privacy name-masking** (the demo's eye-toggle) and **AI-context masking:** column `context_hidden`/`context_mask:"phone|email|partial|hash"` keeps PHI out of LLM prompts.
- ⚠️ **Hard single-patient session caging** (externally-launched, one-patient view) must live in **handler code, not entity scopes** — the entity-scope approach was tried and reverted (broke other roles). Role-scoped "own patients" is config-only and sufficient for the main app.

### F-Onboarding (Add patient + notify) → create workflow + notification subscription
- Add-patient form (entity create) → `on_create` subscription → MDT new-patient notification workflow. Webhook ingestion (`webhooks.json`) handles HIS-pushed registrations with `idempotency_config` dedup.

### F-Documents (Rx/reports) → file fields + attachment system
- Column `ui_type:"file"` (`accept:".pdf,image/*"`) → binary upload + `attachment` entity; S3/MinIO via `communication.json.file_storage`; viewer widget on the detail page; extraction tooling exists in presets.

### F-AI Assist → ADK agent + tools
- A `standard` agent (clinical system prompt) with linked read tools + gated write/workflow tools, deployed in `chat` against the record. Stateless inline AI via the workflow `llm` op (+`sanitize` guard). Default model `google:gemini-2.5-flash` (note: the shipped presets standardize on Gemini; confirm provider creds if another LLM is desired).

---

## 3. Build process (how ProstaCare gets stood up)

**Standing up the tenant/preset is 100% config — zero Go.**

1. **Bootstrap:** `POST /api/v1/{tenant}/bootstrap/system` → creates `tenant_{id}` schema, system roles, canonical entities (FHIR-aligned `patients`/`appointments`/`doctors`), AI-CMS skeleton.
2. **Seed preset:** `python3 scripts/agent_e2e/seed-preset.py prostate_cancer` → entity DDL + PATCH canonical extensions, tools, agents, agent↔tool links, sample data, Typesense reindex. Idempotent (`ON CONFLICT DO UPDATE`).
3. **Admin/SSO:** register first admin; optional Azure AD IdP.

**Preset deliverable** = a folder `presets/prostate_cancer/` with `schemas.json`, `workflows.json`, `tools.json`, `agents.json`, `agent-tools.json`, `pages.json`, `ui/schema_ui.json`, `mat_views.json`, `reports.json`, `roles.json`, `sample-data.json`, `config.json`, `app_theme.json`, `utterances.json`, `scenarios.json`. A generator (`scripts/agent_e2e/claude-create-preset.sh "<description>"`) scaffolds preset JSON from prose.

**Config vs code line:** JSON covers entities + full REST surface, RLS/RBAC, workflows (24 operators), triggers (manual/event/cron), webhooks, outbound integrations, agents/tools, caching, search, audit, partitioning, mat-views. You cross into **Go** only for: a new workflow operator, a new channel/messaging adapter, a new HIS vendor adapter, a new remote-connector type, or `public.*` schema migrations. ProstaCare stays config-only **unless** it integrates a specific HIS/EMR vendor or a non-REST data source.

(Minor doc drift: local Postgres port is cited as both 5433 and 5434 — verify locally.)

---

## 4. Integration reality (the code-heavy frontier)

| Capability | Status on platform | Effort for ProstaCare |
|---|---|---|
| **Local-as-source-of-record + `his_*` shadow columns** | ✅ Shipped pattern (appointments) | Config — the proven integration shape |
| **HIS appointment adapter** (`his.Adapter`, 8 methods, per-tenant resolver) | ✅ Local + Mock shipped; HTTPAdapter deferred | New vendor = `internal/integrations/his/{vendor}.go` + one resolver line + tests → **days-to-weeks of Go per vendor** |
| **Read-only virtual entities** (data lake / LIS / PACS / FHIR REST) | ✅ Complete (generic REST connector, JSONPath mapping) | **Config-only** if source is REST/JSON; treat as read-mostly federation |
| **FHIR** | ⚠️ Data-model-aligned, **no wire connector** | FHIR *read* = config via generic connector today. FHIR *write*/appointment round-trip = net-new Go adapter (+ likely external FastAPI facade for Bundles/OAuth/mTLS) |
| **ABDM** (India health stack) | ⚠️ Survey/comments only | **Greenfield** — consent manager + HIP/HIU gateway + OAuth2/Bundles; budget as a connector project (external facade + Go adapter), not a preset |
| **ABHA** (India health ID) | ❌ Absent (zero code/docs) | **Greenfield** — ABHA verification/linking flow is net-new |
| **Patient identity matching** | ⚠️ Adapter-level contract shipped; Identity-Broker is a design | Schema fields + a workflow calling `/internal/identity/resolve` is config; the matching engine + real HIS search depend on a connector you implement |

---

## 5. Gaps & work-to-budget (revised)

None is a blocker; each is additive on top of the config baseline.

| # | Gap | Impact | Mitigation / effort |
|---|---|---|---|
| **G1** | **Confirm/extend frontend chart renderers** (line, percentile band, Kaplan-Meier) | PSA-over-time, survival curves | Platform doesn't restrict chart subtype; the renderer lives in `metadata-auto-ui` (not audited). Verify line/area exist; KM is custom. **Re-scoped down from "platform can't do it."** |
| **G2** | **No MDT / tumour-board concept** on the platform | The collaborative review object ProstaCare centers on | **Net-new:** `mdt_review` + `mdt_participant` + `discussion_entry` entities, review lifecycle, discussion UI. Notification plumbing already exists. |
| **G3** | **Guideline rule evaluation is yours to own** | The clinical "why a gap exists" logic | Build as in-platform workflows (Option A) or upstream (Option B). Platform gives lifecycle/dedup/audit/scheduling, not NCCN/EAU rules. |
| **G4** | **No ABHA / ABDM connector; FHIR has no wire layer** | India health-ID + EMR interop | FHIR read = config; FHIR write/ABDM = net-new connector project (external facade + Go). De-risked by FHIR-aligned schemas + data-driven adapter resolver. |
| **G5** | **Numeric/cross-row computed fields** not in the `compute` DSL | ADT-months, PSA doubling time, completeness % | Materialized views / workflow steps (the DSL covers string composition only). |
| **G6** | **No field-level PHI encryption toggle** in schema | Column-encrypt for Aadhaar/ABHA | At-rest/DB encryption + `read_roles` + `context_mask`; add `Encrypted` attr usage / column-encrypt if compliance requires. |
| **G7** | **No regex/range/length validation DSL** | Input validation beyond required/unique/enum/FK/type | App-layer/`branch` validation; required/unique/enum/FK/type constraints do exist. |
| **G8** | **Email/SMS templating inline in workflow JSON** (no template library; WhatsApp excepted) | Maintaining MDT/email HTML | Acceptable short-term; consider a `message_templates` entity. |
| **G9** | **Hard single-patient session caging is code, not config** | Only if you embed external single-patient launches | Role-scoped "own patients" is config and sufficient for the main app; code-cage per the Bayanaty pattern only for external deep-links. |
| **G10** | **Care-gap lifecycle is binary open/closed; no snooze; external launch read-only** | If reusing the shipped care-gap product as-is | Add a `snooze`/status + disposition write-back; or use Option A nudges where you control the lifecycle. |

---

## 6. Recommended approach

1. **Fork `novahub_v2`** (clinical/care-gap) — optionally cherry-pick from `hospital_crm`/`diagnostic_lab` — into a `prostate_cancer` preset.
2. **Author prostate entities** in `schemas.json` (`psa_result`, `biopsy`, `staging`, `treatment`, `imaging_workup`, `nudge`, `journey_event`) as extensions on canonical `patient`; partition the time-series; use the `compute` DSL for string derivations.
3. **Model the net-new MDT** (`mdt_review`/`mdt_participant`/`discussion_entry` + lifecycle).
4. **Build the Patient File** as a `b2b_account`-style detail page in `ui/schema_ui.json`.
5. **Encode nudge rules** (Option A): one parameterized rules workflow + a `guideline_rule` config entity, bound to `on_update` subscriptions + a daily `policies` cron.
6. **Wire MDT notify** via nudge/`mdt_review` `on_create` → resolve participants → `for_each` → email/in-app.
7. **Build cohort dashboards** in `pages.json` over RLS-scoped `mat_views.json`; drill-to-patient via `navigate`/`link_to_detail`.
8. **Scope & mask** via `scopes` (own-panel/department) + column `read_roles`/`context_mask`.
9. **Theme** via `config.json` + `app_theme.json`.
10. **Plan the connector work** separately: FHIR read (config) now; FHIR write / ABHA / ABDM as a budgeted connector project later.

---

## 7. One-line answer

> **Yes — ProstaCare can run on nova-edge-pg, and the build is pure configuration to stand up.** The platform supplies records, dashboards, RBAC/PII, notifications, documents, care-gap lifecycle, audit, search, partitioned time-series, computed columns, and a data-driven HIS adapter. The genuinely net-new work is the **MDT/tumour-board model**, the **guideline rule logic itself** (authored as workflows), and **India health-system connectors** (ABHA/ABDM greenfield; FHIR write needs an adapter). Chart richness is a frontend-renderer question, not a platform limit.

---

*Source: deep read of nova-edge-pg requirement docs, guides, and source (cited in the header) plus the `sakra` and `novahub_v2` presets. Supersedes the first-draft caveats; see §0 for corrections.*
