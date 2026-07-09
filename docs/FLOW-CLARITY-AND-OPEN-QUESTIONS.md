# ProstaCare — Flow Clarity, Boundaries & Open Questions (Pre-Build Discovery)

**Status: BLOCKING gate before any NOVA Edge preset work.**
We will not start the `prostate_cancer` preset until the team model, data boundaries, permission boundaries, and end-to-end flows are signed off by the business/clinical team.

**Purpose.** The repo demo and the requirement docs (`PRD.md`, `FUNCTIONAL_REQUIREMENTS.md`, `SCOPE.md`, `ProstaCare_Nudge_Logic_Handoff.md`) describe a **single-user prototype**. They do not define the multi-user reality the real product needs. This document (a) maps every end-to-end flow, (b) marks exactly where each flow hits an **undefined boundary**, (c) lists the **blocking questions** for the business team, and (d) proposes a **straw-man default** for each so the business team can react/confirm rather than design from scratch.

---

## 1. Headline — what we actually have vs what we need

| Area | What the demo / docs define | What is undefined (and blocks the build) |
|---|---|---|
| **Users** | One persona: HOD, always logged in | Are clinicians, MDT members, coordinators, ops real **logins**? Is this multi-user at all? |
| **"Team"** | A hardcoded 5-name MDT directory used as notify targets | What *is* a team? Global vs per-facility vs per-patient? Who manages membership? Team = MDT = tumour board, or distinct? |
| **Accessing the team** | "Send to a member" / "send to all MDT" (one-directional) | How does the **inbound** side work — does a member log in, get an inbox, act, reply? Is discussion two-way? |
| **Patient visibility (data boundary)** | HOD sees the whole department (filters 8 of 10 by department) | Who sees which patients? Own-panel vs department vs care-team vs shared? Is there patient "ownership"? |
| **Permissions (action boundary)** | Everything is open (single user) | Who can edit which sections, resolve nudges, register patients, send to all-MDT, configure rules, see identified analytics? |
| **Nudge lifecycle** | Rules fire; "acknowledge" logs but never resolves | Who **owns** a nudge? Who can resolve/dismiss? SLA/escalation? Snooze? |
| **Source of truth** | Patients are local sample records | Are patients **created** in ProstaCare or **synced** from HIS/registry? What's the match key (UHID/ABHA)? |
| **Org / tenancy** | Single site (AIIMS) | One hospital or a multi-site network? One department or Urology + Radiation Oncology as separate units? |

**Bottom line:** the demo answers "what screens exist," not "who can do what to whose data, and how the team actually collaborates." Those are exactly the things a NOVA Edge preset has to encode (entities, scopes, roles, workflows) — so they must be resolved first.

### Decisions log (live)
| ID | Decision | Status |
|---|---|---|
| O-TEN | **Tenant = institution** (one schema per hospital; no `institution_id`). Within-institution cross-doctor/dept reporting is native; cross-institution = de-identified aggregation layer above tenants. *(Supersedes the earlier "single shared tenant" note.)* | ✅ DECIDED (updated) |
| O-DEP | Deployment model: institutional single tenant **vs** per-doctor SaaS tenant ("tenant-C", internet self-serve) | ⬜ OPEN (P0) |
| O-ONB | Predefined doctor-teams to onboard? **None found in docs/scope** | ⬜ OPEN (P0) |
| O-ACC (A) | Clinical operational visibility = **department/team-scoped** (HOD/coordinator may be tenant-wide) | ✅ DECIDED |
| O-ACC (B) | Non-clinical / ops / quality / **pharma sponsor = de-identified aggregate only** (PHI firewall) | ✅ DECIDED |
| O-ACC (C) | Identifiers **masked-by-default + audited reveal** | ✅ DECIDED |
| O-A1 | Multi-user vs single console | ⬜ OPEN (P0) |
| O-T1/T2 | "Team" model + care-team vs tumour-board | ⬜ OPEN (P0) |
| O-S1 | Patients created here vs synced from HIS (match key) | ⬜ OPEN (P0) |
| O-TMPL1 | Single-disease vs templatable multi-disease core | ⬜ OPEN (P0) |
| O-PH1/2/3 | Pharma role (NVS=Novartis?), data model, rule governance/COI | ⬜ OPEN (P0) |
| O-CH | Notification channels = **in-app inbox + email via AWS SES** (login identity = email); SMS/WhatsApp future | ✅ DECIDED |
| O-N* | Nudge ownership + SLA/escalation + snooze | ⬜ OPEN (P1) |
| O-AGG | Cross-tenant aggregation via Zygo Data Cloud (de-identified `sponsor_metric` → pull → sponsor) | 🟡 SPEC'D — see `CROSS_TENANT_AGGREGATION_SPEC.md` |
| O-REP* | Reporting grain & destination | ⬜ OPEN (P1) |
| O-DOM* | Domain / hosting / data-residency / IP | ⬜ OPEN (P2) |

---

## 2. Actors — intended vs defined

PRD §3 names six user types but the demo implements only the first as a real session:

| Actor (PRD §3) | In the demo? | Needs definition |
|---|---|---|
| Urologist | ❌ (only HOD persona) | Own-panel? Edit which sections? |
| Radiation oncologist | ❌ | RT-plan authorship? MDT role? |
| Medical oncologist | ❌ | Systemic-therapy/ARSI authorship? |
| MDT coordinator | ❌ | Triage nudges? Manage tumour-board? Assign actions? |
| Clinical ops / quality | ❌ | Identified or aggregate-only access? |
| Demo stakeholder | ✅ (HOD login) | — |
| **MDT directory members** (5 clinicians) | ⚠️ as *notify targets only*, not users | Are these the same people as the actors above, with logins? |

**Open question O-A1:** Is ProstaCare **multi-user** (each clinician logs in, has a panel and an inbox), or a **single-coordinator console** (one user drives everything, "team" is just a notify list)? *This single answer reshapes the entire data/permission model.*
**Straw-man:** Multi-user. Each clinician has a login, a patient scope, and an inbox; "send to team" creates real items others act on.

---

## 3. The "Team" concept — deep dive (the core of the question)

The demo's "team" is a static array of 5 clinicians (Radiation Oncology, Medical Oncology, Onco-radiology, Nuclear Medicine, Nurse Specialist). It is used **only** as the recipient list for a notification. There is no membership management, no per-patient team, no inbound participation. We need the business team to pick a model:

| Candidate model | What it means | Implication |
|---|---|---|
| **(a) One global department MDT** | A fixed roster for the whole unit; every patient's "team" is this panel | Simplest; "team" = a config list; notify = broadcast to the panel |
| **(b) Per-facility MDT** | Each hospital/site has its own MDT roster | Needs org-unit model; team scoped to facility |
| **(c) Per-patient care team** | Each patient has a specific set of involved clinicians (treating urologist + assigned RT onc + …) | Needs `care_team_member` per patient; visibility can follow team membership |
| **(d) Named tumour boards** | A patient is *presented to* one or more tumour-board sessions; membership per board | Needs `tumour_board` + `board_session` + presentation flow |

**Open questions:**
- **O-T1:** Which model (a/b/c/d) — or a combination (e.g. a global MDT panel **plus** a per-patient treating clinician)?
- **O-T2:** Are "care team" (who manages this patient day-to-day) and "tumour board / MDT" (who reviews the case formally) **the same concept or two different things**? Clinically they usually differ.
- **O-T3:** Who **manages team membership** — an admin, the HOD, or self-serve? Does it change over time (and do we keep history)?
- **O-T4:** Can a patient belong to **more than one** team/board? Can a clinician belong to multiple teams?
- **O-T5:** Are **referring / external** clinicians part of the team (read-only? notified?) or out of scope?
- **O-T6:** Does "send to all MDT" mean *this patient's* team, or the *whole department* MDT?

**Straw-man:** (a)+(c) hybrid — a **global department MDT panel** (config roster, the default "all MDT" target) **plus** a per-patient **treating clinician** and an optional small **care team**. Tumour-board = the MDT panel reviewing a case (a review event), distinct from the care team. Membership managed by an admin/coordinator, with history retained.

---

## 4. Data boundary — patient visibility (who sees whom)

The demo shows the HOD seeing the whole department and filtering two out-of-department patients. That's the *only* signal. Real visibility must be a rule.

| Candidate visibility model | Who sees a patient |
|---|---|
| **Department-wide** | Any clinician in the department sees all department patients (≈ demo) |
| **Own-panel** | A clinician sees only patients where they are the treating/owning clinician |
| **Care-team** | A clinician sees a patient only if they're on that patient's care team / tumour board |
| **Role-tiered** | Clinicians see identified records in scope; ops/quality see **aggregate/de-identified** cohort with drill to limited fields |

**Open questions:**
- **O-D1:** What is the default visibility — department-wide, own-panel, or care-team? (The HOD likely sees all; what about a treating urologist or a nuclear-medicine member?)
- **O-D2:** Is there a notion of **patient ownership / primary clinician**, and how is it assigned (at registration? by coordinator? by referral)?
- **O-D3:** Is **department** the hard boundary (as the demo implies), and how is "department" defined when Urology and Radiation Oncology are combined?
- **O-D4:** Do **ops/quality** users get identified patient data or aggregate-only? (PHI-minimisation matters for sign-off.)
- **O-D5:** Is ProstaCare ever **launched from a hospital EMR for one patient** (single-patient caged session, like the platform's Bayanaty pattern)? If yes, that's a distinct, code-level visibility mode.

**Straw-man:** Default **department-wide** read for clinical roles (matches the HOD-centric demo and tumour-board reality), **own-panel emphasis** on the home screen ("my patients" first), **aggregate-first** for ops/quality with drill limited to clinically necessary fields, and **no external single-patient launch** in v1 (revisit if an EMR-embed is required).

---

## 5. Permission boundary — capability × role (all UNKNOWN today)

Nothing in the demo restricts actions (one user does everything). We need a capability matrix. Below is our **straw-man** — every cell needs business confirmation.

| Capability | HOD | Treating clinician | MDT member | Coordinator | Ops/Quality | Admin |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| View patient (in scope) | ✅ | ✅ | ✅ (care-team) | ✅ | aggregate | ✅ |
| Edit demographics/IDs | ✅ | ✅ | — | ✅ | — | ✅ |
| Edit **clinical** (PSA/staging/biopsy) | ✅ | ✅ | 🔸 own-specialty | — | — | ✅ |
| Edit **treatment** (ADT/RT/ARSI) | ✅ | ✅ | 🔸 own-specialty | — | — | ✅ |
| Resolve / dismiss a nudge | ✅ | ✅ | 🔸 | 🔸 | — | ✅ |
| Send to a member | ✅ | ✅ | ✅ | ✅ | — | ✅ |
| Send to **all MDT** | ✅ | ✅ | 🔸 | ✅ | — | ✅ |
| Register a patient | ✅ | ✅ | — | ✅ | — | ✅ |
| Upload Rx/documents | ✅ | ✅ | 🔸 | ✅ | — | ✅ |
| View population analytics (identified) | ✅ | 🔸 own-panel | — | ✅ | aggregate | ✅ |
| Configure guideline rules | — | — | — | — | — | ✅ (+ clinical sign-off) |
| Manage team / directory / facilities | — | — | — | 🔸 | — | ✅ |

✅ full · 🔸 limited/conditional · — none

**Open questions:**
- **O-P1:** Is record editing **section-gated by specialty** (e.g. only Radiation Oncology edits the RT plan), or can any clinician in scope edit anything?
- **O-P2:** Who may **resolve/dismiss** a nudge — only the responsible role, or anyone in scope? Does dismissal require a reason (audited)?
- **O-P3:** Should "send to **all MDT**" be restricted (it's high-noise) — e.g. HOD/coordinator only?
- **O-P4:** Who configures **guideline rules**, and what is the **clinical sign-off** workflow before a rule goes live?

---

## 6. End-to-end flow map (with boundary + clarity status)

Legend: 🟢 clear · 🟡 partial · 🔴 blocked (needs business answer).

| # | Flow | Actor(s) | What the demo shows | Boundary question | Status |
|---|---|---|---|---|---|
| 1 | Login & landing | any | One HOD login | Roles? Per-role home screen? (O-A1) | 🔴 |
| 2 | Cohort review | HOD/ops | Whole-department KPIs | Whose cohort? Identified vs aggregate? (O-D4) | 🟡 |
| 3 | "My panel" review | treating clinician | — (absent) | Does own-panel view exist? (O-A1, O-D2) | 🔴 |
| 4 | Open patient file | clinician | Anyone opens anyone | Visibility rule (O-D1) | 🔴 |
| 5 | Edit record | clinician | All sections editable | Section gating by specialty? (O-P1) | 🔴 |
| 6 | Nudge generation | system | 8 rules fire (well-specified) | Who **owns** the nudge? | 🟡 |
| 7 | Act on / resolve nudge | clinician | "Acknowledge" logs, never resolves | Who resolves/dismisses? SLA? Snooze? (O-P2, O-N1..3) | 🔴 |
| 8 | **Access / notify the team** | clinician | Send to member / all (one-way) | Team model + recipient scope (O-T1, O-T6) | 🔴 |
| 9 | MDT member **receives & responds** | MDT member | — (no inbound side) | Inbox? Act-from-notification? Reply? (O-A1, O-N4) | 🔴 |
| 10 | Discussion thread | team | Per-patient log (one-way) | One-way log vs threaded conversation? | 🔴 |
| 11 | New patient onboarding | clinician/coord | Modal create + notify preview | Created here vs synced from HIS? Match key? Who may register? (O-S1..3) | 🔴 |
| 12 | Rx / document upload | clinician/staff | Browser-local upload | Who uploads? Retention/access? (O-P, future) | 🟡 |
| 13 | Population analytics | ops/HOD | 6 dashboards + drilldown | Identified vs aggregate per role; whose cohort (O-D4) | 🟡 |
| 14 | Guideline reference + rule governance | clinician/admin | Static reference content | Who owns/approves/versions rules? (O-P4, O-G1) | 🔴 |
| 15 | External single-patient launch | external EMR | — | Does an EMR-embed/caged session exist? (O-D5) | 🔴 |

**Read-out:** the *clinical record* flows (4–6, 12, 13) are mostly understood; the **collaboration, identity, and boundary** flows (1, 3, 7–11, 14, 15) — i.e. everything that makes it a *team product* — are blocked.

---

## 7. Blockers — questions to pose to the business team (prioritised)

**P0 — cannot model entities/scopes/roles without these:**
1. **O-A1** Multi-user or single-console? (Do clinicians/MDT members log in and act, or is "team" just a notify list?)
2. **O-T1/O-T2** What is a "team"? Global department MDT vs per-facility vs per-patient care team vs named tumour boards — and is care-team distinct from tumour-board?
3. **O-D1/O-D2** Default patient visibility (department / own-panel / care-team) and is there a primary-clinician/ownership concept?
4. **O-S1** Source of truth: are patients **created** in ProstaCare or **synced** from a hospital HIS/registry? If synced, match key (UHID/ABHA) and which fields are read-only?
5. **O-O1** Org/tenancy: single hospital or multi-site network? Is "Urology & Radiation Oncology" one unit or two?

**P1 — shapes the flows and screens:**
6. **O-T3/O-T4** Who manages team membership; can a patient be on multiple teams/boards; history retained?
7. **O-N1** Nudge ownership: when a nudge fires, who is responsible (treating clinician / relevant specialist / coordinator)?
8. **O-N2/O-N3** Resolve/dismiss rules, dismissal reason+audit, **SLA/escalation** for unactioned urgent nudges, and **snooze**?
9. **O-N4** Notification channel (email / in-app inbox / SMS / WhatsApp) and whether a recipient can **act/reply from** the notification (does it create a task for them)?
10. **O-P1/O-P3** Section-level edit gating by specialty; restrict "send to all MDT"?

**P2 — governance & refinement:**
11. **O-P4/O-G1** Who owns/approves/versions the guideline rules (clinical governance), global vs per-facility?
12. **O-D4** Identified vs aggregate analytics access for ops/quality (PHI minimisation).
13. **O-D5** Any external single-patient EMR-launch (caged session) requirement?
14. **O-H1** Are NCCN/benchmark targets configurable, and who sets them?

---

## 8. Our straw-man "to-be" model (for the business team to react to)

So the discussion starts from a position, not a blank page, here is what we would build **unless told otherwise** (each maps to a blocker above):

- **Multi-user**, role-based: HOD, Treating Clinician, MDT Member, Coordinator, Ops/Quality, Admin.
- **Team = a global department MDT panel** (config roster, default "all-MDT" target) **+ a per-patient treating clinician** and optional small **care team**. **Tumour-board review** is an *event* where the MDT reviews a case (distinct from care team).
- **Visibility:** department-wide read for clinical roles, "my patients" emphasised on the home screen; ops/quality **aggregate-first**.
- **Patients synced from HIS/registry** as source of truth (ABHA/UHID match), ProstaCare authoritative for the oncology overlay (nudges, MDT, journey); manual registration allowed as fallback.
- **Nudge ownership** = the patient's treating clinician, with coordinator visibility; **resolve** when the source field changes (auto) or via explicit dismiss-with-reason; **urgent nudges escalate** to HOD/coordinator after an SLA.
- **Notifications** = in-app inbox + email; a notification **creates an actionable item** in the recipient's inbox; discussion is a **threaded** per-patient log.
- **Rules** authored as config (`guideline_rule`), **versioned with clinical sign-off**, admin-managed.
- **Single hospital, single department** in v1; org-unit model ready for multi-site later. No external EMR-embed in v1.

---

## 9. Round-2 dimensions (tenancy, templates, reporting, channels, pharma, domain)

These were raised after the first pass and several are **P0** — they change the entity/tenancy model itself.

### 9.1 Tenancy & isolation model — `O-TEN` ✅ DECIDED: SINGLE TENANT
**Decision (confirmed):** a **single tenant** for the whole product, chosen because **cross-reporting across doctors/departments is a core need**. On NOVA Edge this is one Postgres schema, so cohort analytics span all users natively — no cross-tenant aggregation layer required.

**Key consequence — single-tenant ≠ open access.** The privacy boundary is enforced *inside* the tenant by two independent mechanisms, so cross-reporting and least-privilege coexist:
- **Operational reads** (identified patient records) → **row-level scopes** (`row_policies`/`scopes`) per user / role / team, plus **field-level** `read_roles` for sensitive columns.
- **Reporting reads** (cohort) → **RLS-scoped materialized views**, which can be authored **de-identified** so ops / quality / sponsor users see aggregates with no PHI.

➡️ The remaining live decision is **§9.1a — where we draw the access-boundary lines** (below).

### 9.1a Data access boundary inside the single tenant — `O-ACC` ✅ DECIDED
**Decisions (confirmed):**
- **(A) Operational/clinical visibility = Department/team-scoped.** A clinical user sees identified patients in their department/team; HOD/coordinator roles may be granted tenant-wide. Cross-department insight comes from the de-identified reporting layer, not raw record access.
- **(B) Non-clinical / ops / quality / pharma sponsor = De-identified aggregate only.** Hard firewall from PHI — cohort stats + drill to masked rows. (Satisfies DPDP least-privilege and removes sponsor conflict-of-interest risk.)
- **(C) Identifiers masked-by-default** (name, ABHA/Aadhaar, phone) with **audited reveal** for in-scope clinical users.

➡️ NOVA Edge encoding: department/team `row_policies` + role grants for HOD/coordinator; column `read_roles`/`context_mask` for identifiers; **de-identified, RLS-scoped materialized views** as the only surface exposed to ops/quality/sponsor roles.

_Original option analysis retained below for the record:_

**(A) Operational/clinical visibility — who sees which *identified* patients:**
| Option | Who sees a patient (identified) | Trade-off |
|---|---|---|
| **Tenant-wide clinical** | Every clinical user sees all patients | Simplest, max collaboration (≈ demo HOD view); weakest PHI least-privilege |
| **Department/team-scoped** | Clinical user sees patients in their dept/team | Balanced; cross-dept still served via de-identified reporting layer |
| **Own-panel + care-team** | Clinician sees own patients + those whose care-team/tumour-board they're on | Tightest PHI control; needs care-team membership upkeep |

**(B) Reporting/non-clinical boundary — what ops / quality / sponsor see:**
| Option | What they see |
|---|---|
| **De-identified aggregate only** (recommended) | Cohort stats + drill to **masked** rows; hard firewall from PHI |
| Identified in scope | Full records within their scope (only if a clinical/governance need is proven) |

- **O-ACC1:** Operational default = tenant-wide / department-scoped / own-panel? (Can differ by role — e.g. HOD tenant-wide, treating clinician own-panel-first.)
- **O-ACC2:** Confirm non-clinical/sponsor users are **de-identified aggregate only** (the firewall), regardless of (A).
- **O-ACC3:** Field-level masking — which columns are always masked unless explicitly revealed (names, ABHA/Aadhaar, phone), and is every reveal audited?
- **Straw-man:** Role-tiered — **clinical roles get broad (tenant-wide/department) identified access** for collaboration + cross-reporting, with the *ability* to tighten to own-panel via scopes; **all non-clinical/sponsor access is de-identified aggregate**; identifiers masked-by-default with audited reveal.

### 9.1b Deployment / go-to-market model — `O-DEP` (P0, OPEN — revisits O-TEN)
Separate from *isolation*, this is *how the product is sold/run*. A second model is on the table: a **public-internet SaaS where each doctor (or doctor + team) self-onboards into their own dedicated tenant** — i.e. the "per-doctor tenant" / "tenant-C" option — rather than one institutional deployment.

| Model | Shape | Cross-reporting | Onboarding |
|---|---|---|---|
| **Institutional single tenant** (current decision) | One shared tenant for an institution; doctors = scopes | ✅ Native (one schema) | Admin provisions doctors/teams |
| **Per-doctor SaaS tenant** (`O-DEP`, internet) | Each doctor/team gets a dedicated isolated tenant; self-serve sign-up | ❌ Not native — needs a **separate de-identified registry/aggregation layer above tenants** to report across doctors | Self-onboarding flow + per-tenant bootstrap |

- **O-DEP1:** Is the target an **institutional deployment** (single tenant) **or** an **internet SaaS with a dedicated tenant per doctor/team** — or **both** (institutional now, SaaS later)?
- **O-DEP2:** If per-doctor tenants are in scope, cross-reporting requires a **registry aggregation layer** (de-identified) above the tenants. Is that layer in scope, and who owns it (us / sponsor / network)?
- **O-DEP3:** Self-serve sign-up implies public auth, billing, per-tenant provisioning/bootstrap, and tenant-level data-isolation guarantees — confirm these are wanted.
- **Tension to resolve:** the current **single-tenant decision (O-TEN)** is optimised for cross-reporting; a per-doctor-tenant SaaS is optimised for isolation/self-serve and **breaks native cross-reporting**. The only way to have both is single-tenant-with-scopes **or** per-doctor-tenants **plus** a registry layer. The business must pick the primary model.
- **Straw-man:** Institutional single tenant for v1 (matches O-TEN); design the schema/scoping so a future per-doctor-tenant SaaS + de-identified registry layer remains possible, but do **not** build the SaaS multi-tenant control plane in v1.

### 9.2 Template / framework variation — `O-TMPL` (P0/P1)
- **O-TMPL1 (single vs multi-disease):** Is this **only prostate cancer**, or the **first of several disease frameworks** (breast, lung, …)? "Template variation per framework" suggests a reusable platform, which changes how we model the core.
- **O-TMPL2 (per-department):** Do **Urology / Radiation Onc / Medical Onc** need different record templates, nudge sets, and dashboards — or one shared template with role views?
- **O-TMPL3 (overlay strategy):** If multi-disease: a **shared clinical core + disease-specific overlay**, or fully separate builds?
- **Straw-man:** Prostate first, but **schema designed as shared clinical core + disease overlay** so other cancers template later. Per-department differences handled as **role/department-scoped layouts + tagged nudge-rule subsets**, not separate schemas. (NOVA Edge supports this via per-role `ui/schema_ui.json` layouts + per-vertical presets.)

### 9.3 Reporting & data-structure expectations — `O-REP` (P1)
"How should data be structured to be usable for end-user reporting/queries?" — needs the analytics contract defined up front, because it dictates the grain we model at.
- **O-REP1 (grain):** Which reporting grains are needed — patient, encounter/visit, **treatment-line**, **nudge-event**, lab-observation?
- **O-REP2 (destination):** In-product dashboards only, or must data **export to a warehouse / BI (Power BI/Tableau)** or to the pharma sponsor?
- **O-REP3 (questions):** Confirm/extend the KPI list the model must answer (the 347-cohort dashboards are the starting set: protocol adherence, care-gap closure, time-to-treatment, outcomes/survival).
- **O-REP4 (identified vs de-identified + cadence):** Per audience, and refresh real-time vs daily/periodic?
- **O-REP5 (longitudinal):** Confirm PSA series / treatment timelines / survival need time-series + event modeling.
- **Straw-man:** Model **fine-grained event/observation tables** (PSA, staging, treatment-line, nudge-event) so any rollup is possible → curated **RLS-scoped materialized views** for the known dashboards → a **de-identified export feed** for pharma/BI; daily refresh.

### 9.4 Communication channels for nudges — `O-CH` (P1)
- **O-CH1:** Are nudges **portal-only (in-app alerts)**, or also **email / SMS / WhatsApp**?
- **O-CH2:** Inbound — does a notified member get an **inbox item / email they can act on**, and does it create a **task** for them?
- **O-CH3:** **Digest vs real-time** (e.g. daily care-gap digest per clinician + immediate for urgent)?
- **O-CH4:** Any **patient-facing** communication (reminders), or clinician-only?
- **Straw-man:** In-app inbox primary; **email digest** for clinicians + immediate email for urgent; **clinician-only** (no patient-facing) in v1; WhatsApp later. (All are config workflow comms steps in NOVA Edge; channel choice drives the provider integration.)

### 9.5 Pharma role, data access & governance — `O-PH` (P0, sensitive) ⚠️
**Context we must confirm:** the demo watermark says *"THB Sample Prostate Ca Screens prepared for **NVS** Team."* We infer **NVS = Novartis** (its stock ticker) — i.e. a **pharma sponsor/audience**. The care gaps the product foregrounds (**ARSI intensification, PSMA PET-CT, bone protection**) are areas of direct pharma commercial interest. This must be clarified because it drives **data governance, consent, and access boundaries**, and a potential **conflict-of-interest** concern.
- **O-PH1:** Is pharma (Novartis?) the **sponsor/funder**, a **data consumer**, both, or neither? What's the commercial model?
- **O-PH2:** What data does pharma receive — **none / aggregate de-identified / patient-level de-identified (RWE) / identified (consent-only)**?
- **O-PH3 (governance/COI):** If a sponsor has commercial interest in a recommended therapy, what **independent clinical governance + versioned sign-off** ensures nudges are **guideline-driven, not promotional**? *(Essential for clinician trust and compliance.)*
- **O-PH4 (consent/legal):** Consent basis for any secondary (pharma/research) use — India **DPDP Act**, ICMR, ethics-committee approval?
- **O-PH5 (firewall):** Is there a hard separation between the **identified care-delivery** product and any **pharma-facing analytics/RWE** layer?
- **Straw-man:** Pharma receives **de-identified aggregate** care-gap/cohort reporting only, via a **separate registry/RWE layer** with its own consent basis; clinical nudge rules governed by an **independent clinical committee** (versioned sign-off); **hard firewall** between identified care data and pharma outputs. **Flag for legal/ethics review before build.**

### 9.6 Domain, hosting, data residency & ownership — `O-DOM` (P2)
- **O-DOM1:** Product **domain/URL** — decided? Is domain procurement/ownership **our scope** or the client's?
- **O-DOM2:** **Hosting/deployment** ownership (our managed NOVA Edge vs client infra vs cloud) and **India data-residency** requirement?
- **O-DOM3:** **Data & IP ownership** — hospital, pharma sponsor, or us?
- **Straw-man:** Client/sponsor owns domain + data; we host NOVA Edge in an **India region**; IP/ownership pinned in the contract.

### 9.7 Onboarding cohort — predefined doctor-teams? — `O-ONB` (P0, OPEN)
**Finding (checked):** no predefined set of doctor-teams or institutions to onboard exists in the docs or scope. The only "team" anywhere is the demo's **single illustrative directory** — Dr. Anand Sharma (HOD) + 5 MDT members (Radiation Onc, Medical Onc, Onco-radiology, Nuclear Medicine, Nurse Specialist), one department ("Urology & Radiation Oncology"), AIIMS — plus a few sample treating-doctor names inside patient records. `SCOPE.md` mentions an "Admin console for team directory" only as a **future** capability; it lists no actual roster. So we have **no clarity** on who is onboarded at launch.

- **O-ONB1:** Is there a **predefined list of doctor-teams / departments / institutions** to onboard at launch, or is onboarding open/admin-driven over time?
- **O-ONB2:** If predefined — please provide the roster (names, specialty, department, email/identity source) so we can seed roles, team membership, and scopes.
- **O-ONB3:** What is the **onboarding mechanism** — admin-provisioned, bulk import, HIS/HR-directory sync, or self-serve (links to O-DEP3)?
- **O-ONB4:** What is the **identity source** for clinician logins — hospital SSO (Azure AD), email/OTP, or platform-local accounts?
- **O-ONB5:** How are clinicians **mapped to departments/teams and patient scopes** at onboarding (drives the O-ACC department/team boundary)?
- **Straw-man:** A small **predefined pilot roster** (one department, one institution) is admin-provisioned for v1, identity via hospital SSO if available else platform-local; team membership and department scope set at onboarding. Confirm the actual roster.

### 9.8 Round-2 additions to the gate
New **P0** (join §7's P0 list — preset cannot start without them): **O-TEN1/O-TEN2** (tenancy/isolation), **O-TMPL1** (single vs multi-disease), **O-PH1/O-PH2/O-PH3** (pharma role, data access, governance).
New **P1:** O-TMPL2, O-REP1/O-REP2, O-CH1/O-CH2. New **P2:** O-DOM1–3, O-REP4, O-CH3/O-CH4.

---

## 10. Process — how we get to sign-off

1. **Review this doc with the business/clinical team**; get the P0/P1 answers (a 60–90 min working session would clear most).
2. We update this doc with confirmed decisions → it becomes the **agreed flow + boundary spec**.
3. We then produce **"our version"**: the to-be end-to-end flows (swimlane diagrams per role) + the entity/scope/role model — for **sign-off**.
4. **Only then** do we start the NOVA Edge `prostate_cancer` preset, encoding the signed-off model (entities + `scopes`/`row_policies` + `roles` + nudge `guideline_rule` workflow + MDT/notify flows).

> **Gate:** no preset work begins until §7 P0 (and ideally P1) are answered and §8 is confirmed or amended.

---

*Companion docs: `PRODUCT-PRD.md` / `FEATURE-PRD.md` / `FLOW-PRD.md` (intended product), `NOVA-EDGE-FEASIBILITY.md` (platform mapping), and the upstream `PRD.md` / `FUNCTIONAL_REQUIREMENTS.md` / `SCOPE.md` / `ProstaCare_Nudge_Logic_Handoff.md` (demo requirements). This doc is the discovery gate that must close before the preset build.*
