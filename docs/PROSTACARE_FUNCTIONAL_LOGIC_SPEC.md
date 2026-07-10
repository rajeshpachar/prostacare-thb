# ProstaCare — Functional & Logic Specification (Clinical Sign-off Draft)

**Who this is for:** the clinical team, product owners, and engineers — together. It describes, in plain language plus pseudo-code, **what data we capture, how the data relates, and how every workflow runs** (inputs → logic → outputs → derived data). It is written to be **signed off at the pseudo-code level** before build.

**How to read it:**
- **§1 Data models** — what we capture about each thing, its variables, an example, and how it links to others.
- **§2 The one core idea** — "current state" vs "history," with a worked example.
- **§3 Workflows** — each flow as a visual diagram + inputs/logic/outputs pseudo-code.
- **§4 Care-gap rules** — the 8 rules in full, with a worked patient example.
- **§5 Derived data** — every computed number and its formula.
- **§6 Visual master flow** + **§7 sign-off checklist**.

> Naming note: field keys (e.g. `psma_pet_ct`) match the workbook `Field_Dictionary` exactly, so this spec and the data-entry pack stay in lockstep.

---

## 0. Plain-English glossary (read this first)

This document is written for **clinicians and engineers together**. Wherever a technical word appears, here is what it actually means.

| Term you'll see | What it means, plainly |
|---|---|
| **Record type** (also "entity" / "data model") | A *kind* of information we store — a PSA reading, a staging assessment, a treatment line |
| **Cardinality** | Simply: **how many of these a patient can have** |
| **1:1 ("one-to-one")** | The patient has **exactly one** — e.g. one demographics record, one biopsy record |
| **1:N ("one-to-many")** | The patient can have **many**, each with its own date — e.g. many PSA readings over time |
| **Dated log / "append-only"** | Each time something changes we **add a new dated entry**; we never overwrite the old one. History is preserved. |
| **Current state** | The **most recent** dated entry — the patient's status *today* |
| **Derived / calculated** | A number the system **works out by itself** from what you entered. Never typed by hand. |
| **Fixed list of choices** (technically an "enum") | A dropdown where only the listed options are allowed — e.g. *Not done · Done — abnormal · Done — normal* |
| **A rule "fires"** | The system spots a care gap and raises a nudge |
| **Auto-resolve** | The nudge closes **by itself** once the underlying field changes. Nobody clicks "done". |
| **Trigger** | The moment the system runs something — nearly always *"when you press Save"* |
| **Audit trail** | A permanent record of who changed what, and when |
| **Record lock** | After an editing window, a saved record becomes read-only (the HOD can reopen it briefly) |
| **Tenant** | One hospital's own separate, isolated copy of the system |
| **De-identified** | No name, no ABHA/Aadhaar, no phone — only a patient code |
| **Aggregate** | A summary count or percentage across many patients — never one person's data |
| **Pseudo-code** | A step-by-step recipe of the logic, written so engineers build exactly what you signed off. **You do not need to read the code blocks** — each one has a plain-English summary above it. |

**The single most useful idea in this document:**
> *One-to-one* means the fact can only be true once at a time — a patient has **one treatment plan**.
> *One-to-many* means the fact repeats over time — a patient has **many treatment lines** (first ADT, later ARSI, later chemotherapy).
> Getting this right is what stops duplicate and contradictory records.

---

## 1. What the platform captures


Each box below is one **record type**. The "How many per patient" column tells you whether a patient has exactly one of these, or many dated entries over time.

### 1.1 Who uses it (roles) — *simplified: no department*
> **Tenant = institution.** Each onboarded hospital is its own tenant, so **no `institution_id` is stored**. There is **no `department` entity**: all clinical users see that institution's patients, and access differs by **role**, not by department. "Teams" (the MDT panel) are a **notification group, not an access boundary**. Cross-*institution* reporting is a separate **de-identified aggregation layer above tenants**.

| Record type | How many per patient | What it holds | Plain meaning |
|---|---|---|---|
| **User** | many per tenant | `user_id`, name, **`email` (login identity)**, specialty, `role` | Anyone who logs in |
| **Role** | config | **Clinician · HOD (privileged) · Admin** *(Ops/Quality optional)* | What you may do |
| **MDT membership** | flag on User | `is_mdt_member` (boolean) | The "notify all MDT" group — **no access implication, no separate table** |
| **Primary clinician** | 1 per patient | `patient.primary_clinician_id` | The treating clinician (attribution, not restriction) |

**Access by role (the whole model):**
| Role | Sees | May do |
|---|---|---|
| **Clinician** | all patients in the institution | enter/edit clinical data **within the edit window** (§1.8); act on nudges; notify a member |
| **HOD** | all patients | everything a Clinician can **+ privileged:** **unlock a locked record** (time-bound), notify all MDT, view audit, manage roster/MDT flags |
| **Ops / Quality** | **de-identified aggregates only** | dashboards; no patient records |
| **Admin** | no clinical data | users, roles, rules, config |

### 1.2 The patient and their current clinical state
*(exactly one of each per patient)*
| Record type | How many per patient | What it holds | Example |
|---|---|---|---|
| **Patient** (hub) | 1 per patient | `patient_code`, `age_at_diagnosis_years`, `healthcare_coverage`, `state`, `referral_source`, `registry_enrolment_date`, `diagnosis_date` | `PCR-001`, 68, CGHS, Delhi, Govt OPD |
| **Pathology** | 1 per patient | `gleason_score`, `isup_grade_group`, `biopsy_type`, `pi_rads_score`, `cores_positive_total`, `perineural_invasion`, `ece`, `dre_findings`, `ipss_score`, `prostate_volume_cc` | Gleason 4+4=8, ISUP 4, MRI-fusion |
| **Comorbidity / family history** | **flags on Pathology** | 9 comorbidity + 6 family-history Yes/No columns | Diabetes = Yes; Breast Ca (family) = Yes *(no separate table)* |

| **Outcome** | 1 per patient | `best_response`, `psa_nadir_value/date`, `psa_doubling_time_months`, `biochemical_recurrence_status/date`, `crpc_progression_status/date`, `rt_outcome_status` | Nadir 0.8 @ 2026-05, no recurrence |

### 1.3 The dated histories — *many entries per patient, never overwritten*
| Record type | How many per patient | What it holds | Why we keep a dated history instead of one box |
|---|---|---|---|
| **PSA reading** | many (dated) | `psa_date`, `psa_ng_ml`, `free_psa_pct`, `psa_density`, `context_remarks` | PSA moves over time; drives the trend chart |
| **Staging assessment** | many (dated) | `assessed_on`, `clinical_t_stage`, `n_stage`, `m_stage`, `eau_risk_category`, `ecog_performance_status`, `castration_status` | Restaging & HSPC→CRPC are dated facts, not overwrites |
| **Imaging study** | many (dated) | `study_date`, `modality` (mpMRI/bone scan/PSMA/CT/DEXA/germline), `result` | "Is PSMA done, and how recently" is time-sensitive |
| **Treatment line** | many (dated) | `line_type` (ADT/anti-androgen/ARSI/chemo/RT), `agent`, `start_date`, `end_date`, `status` (+ RT & CGHS fields) | Therapy is sequential: ADT → ARSI → chemo |
| **Supportive-care event** | many (dated) | `at`, `bone_protection_therapy`, `calcium_vitamin_d`, `next_follow_up_psa_date`, `testosterone_monitoring`, `phq9`, `nutrition` | Bone-protection start/stop needs an audit trail |
| **Journey event** | many (dated) | `event_type`, `event_date`, `event_notes` | The human-readable milestone story |
| **Visit** ⭐ | many (dated) | `visit_date`, `visit_type`, `disease_state_at_visit`, `seen_by`, `visit_outcome`, `next_visit_due_date` | **The patient comes back again and again.** Each attendance is its own entry. |
| **Treatment plan** ⭐ | many (dated) | `plan_date`, `line_of_therapy`, `treatment_intent`, `mdt_tumour_board_status`, `date_of_mdt_review`, `reason_for_plan_change`, `plan_status` | A **new plan** is agreed at progression or toxicity. The old plan is kept, marked *Superseded*. |

### 1.4 Care gaps, team messages, documents
| Record type | How many per patient | What it holds | Plain meaning |
|---|---|---|---|
| **Nudge** | many | `nudge_id`, `rule_id`, `severity`, `current_status`, `opened_at`, `resolved_at` | One open care gap for one patient |
| **Nudge event** | many | `nudge_id`, `at`, `action` (**opened · acknowledged · resolved**), `actor` | The lifecycle log behind trend charts + audit |
| **Notification / discussion** | many | sender, recipients, reason, subject, note, delivery, `at` | An MDT message + the per-patient discussion trail |
| **Document** | many | file ref, type, size, uploader, `at` | Rx / report uploads |
| **Guideline rule** | config | `rule_id`, condition, `severity`, version, sign-off | The 8 care-gap rules as governed config |
| **Audit event** | many | actor, action, target, `at` | Who did what, when (incl. identity reveal) |

### 1.5 How everything links together
```mermaid
erDiagram
  USER ||--o{ PATIENT : "primary clinician (1:N)"
  PATIENT ||--|| PATHOLOGY : "1:1"
  PATIENT ||--|| TREATMENT_PLAN : "1:1"
  PATIENT ||--|| OUTCOME : "1:1"
  PATIENT ||--o{ PSA_READING : "dated log"
  PATIENT ||--o{ STAGING_ASSESSMENT : "dated log"
  PATIENT ||--o{ IMAGING_STUDY : "dated log"
  PATIENT ||--o{ TREATMENT_LINE : "dated log"
  PATIENT ||--o{ SUPPORTIVE_CARE_EVENT : "dated log"
  PATIENT ||--o{ JOURNEY_EVENT : "dated log"
  PATIENT ||--o{ NUDGE : "care gaps"
  NUDGE ||--o{ NUDGE_EVENT : "lifecycle log"
  PATIENT ||--o{ NOTIFICATION : "MDT trail"
  GUIDELINE_RULE ||--o{ NUDGE : "produces"
```

### 1.6 Visits — the patient comes back again and again ⭐ *(now included)*

**Decision changed.** We previously deferred a Visit record, because visit *timing* could be inferred from follow-up dates. The clinical team has asked for **visits to be recorded properly** — so a **Visit** is now a first-class dated record. ProstaCare is a **registry**, so it is organised by **clinical event date** (each PSA, staging, imaging, treatment line, supportive-care entry carries its own date). That is lower-burden than a full EMR and is exactly what the care-gap engine and cohort analytics need. Forcing every entry inside a visit would add data-entry friction and doesn't help the current-state or rules logic.

**How visits work**
- Each attendance is one **Visit** entry: date, type (first consultation · follow-up · day-care · MDT review · emergency · telemedicine), who saw the patient, the **disease state at that visit**, the outcome, and **when the next visit is due**.
- Everything captured that day — PSA, labs, imaging, a treatment change — can **optionally point at that visit** (`visit_id`), so you can see *"everything that happened on 15 June."* Entries remain valid **without** a visit, so historical data can still be loaded.
- `last_follow_up_date` is no longer typed: it is simply **the most recent visit**.

**How visits drive follow-up** (this is the loop the clinical pathway asks for):
```
Expected next visit  =  last visit date  +  protocol interval for the disease state
      curative follow-up → 3–6 months        mHSPC   → 3 months
      mCRPC             → 1–3 months          Pluvicto → 6 weeks
      long-term survivor → 12 months

visit_status(patient):
   no visit yet                                   → "New"
   next_visit_due_date in the future              → "Upcoming"
   next_visit_due_date has passed, no visit since → "Missed / Overdue"   ← raises a nudge
   otherwise                                      → "Last visit <date>"
```
Because this gap opens **as time passes** (not when someone saves), it is checked **nightly** — see W12.

**The design that gives us both:** a Visit is recorded, and clinical entries **may** link to it — but are never *forced* to. So we get real visit tracking and follow-up chasing, without blocking data entry or historical loading.

**Included from v1:** a `Visit` record — `encounter_id`, `encounter_date`, `type` (OPD / review / procedure / MDT), `clinician` — and a **nullable `encounter_id`** on each dated event. Events may reference an encounter (to group "everything done at the 2026-06-15 visit") but are **not required** to (registry backfill has no clean visits). It maps cleanly onto a hospital appointment system later, if HIS sync is added.

> **Sign-off question (§7):** confirm **registry-by-event, no Encounter entity in v1**.

---

### 1.7 Where every piece of information comes from
*(and how many of each a patient can have)*

**Two rules keep the record honest:**
1. **Every piece of information is either typed on a named screen, or calculated by the system.** Nothing is hidden or unexplained.
2. **One-to-one** when the fact can only be true once at a time · **one-to-many** when it repeats over time. This is what prevents duplicate and contradictory entries.

| Record type | How many per patient | Where the clinician enters it | Or calculated from | Can it be edited? |
|---|---|---|---|---|
| **Patient** (hub) | **1:1** | *Add New Patient* → Demographics form | — | edit window → lock |
| **Pathology** | **1:1** | *Clinical Assessment* → Complaint / DRE / Biopsy | — | edit window → lock |
| **Treatment plan** ⭐ | **1:N dated** | *Treatment Plan* → new plan at MDT / progression | — | append-only (old plan kept, marked Superseded) |
| **Visit** ⭐ | **1:N dated** | *Add Visit* | — | append-only |
| **Outcome** | **1:1** | *Outcomes* form | — | edit window → lock |
| **Comorbidity / family history** | **flags on `pathology`** | *Clinical Assessment* → chip groups | — | edit window → lock |
| **PSA reading** | **1:N dated** | *Clinical Assessment* → “+ Add PSA Entry” | — | append-only |
| **Staging assessment** | **1:N dated** | *Clinical Assessment* → TNM & Risk (each save = new dated row) | — | append-only |
| **Imaging study** | **1:N dated** | *Clinical Assessment* → Imaging & Molecular | — | append-only |
| **Treatment line** | **1:N dated** | *Treatment Plan* → ADT / Anti-androgen / ARSI / Chemo / RT | — | append-only |
| **Supportive-care event** | **1:N dated** | *Treatment Plan* → Bone Health & Supportive Care | — | append-only |
| **Journey event** | **1:N dated** | *Patient Journey* → Add Event | — | append-only |
| **Notification / discussion** | **1:N** | *Team modal* → Send | — | immutable |
| **Document (Rx)** | **1:N** | *Upload Rx* | — | immutable (removal audited) |
| **Nudge** | **1:N** | ❌ never entered | care-gap rules over current state | system |
| **Nudge event** | **1:N** | ❌ never entered | lifecycle actions | system |
| **Audit event** | **1:N** | ❌ never entered | every action | system |
| **Current state** (stage / line / castration / latest PSA) | derived | ❌ never entered | latest dated row per model (§2) | derived |
| **Dashboards, protocol score, completeness, benchmarks** | derived | ❌ never entered | aggregates | derived |
| **`sponsor_metric`** | derived | ❌ never entered | de-identified aggregates + suppression | derived |
| **Guideline rule** | config | *Admin* → Rules console | — | versioned config |
| **User / Role / MDT panel** | config | *Admin* → Users console | — | config |

**Worked answer to the cardinality question:**
```
A patient has ONE treatment PLAN  (intent + MDT status)          → 1:1
A patient has MANY treatment LINES (ADT → ARSI → chemo → RT)      → 1:N
  ...because prostate therapy is sequential: the patient is on ADT,
     later ARSI is added, later chemo. Each is its own dated line.
     Collapsing them into one row would make sequence unrepresentable.
```

**Duplicate prevention (enforced in the database):**
- 1:1 models → **unique key on `patient_code`** (a patient cannot have two Pathology rows).
- 1:N dated models → **unique key on `(patient_code, <date>, <type>)`** (e.g. one `imaging_study` per modality per date; one `psa_reading` per date) — accidental double-entry is rejected, genuine repeats are distinguished by date/type.

---

### 1.8 How long data stays editable (record lock)

Once data is entered it should not stay editable forever — the record has to become trustworthy for audit. But clinicians still need a way to correct genuine mistakes.

| Concept | Rule (all values configurable) |
|---|---|
| **Edit window** | A record is editable for **`EDIT_WINDOW`** after creation (default **48 h**) |
| **Auto-lock** | After the window it **locks** (immutable) |
| **HOD unlock** | An **HOD** may unlock a specific record for **`UNLOCK_WINDOW`** (default **24 h**) with a **mandatory reason**; it then re-locks automatically |
| **Audit** | Every edit, lock, unlock (with reason), and removal is written to `audit_event` |
| **No hard delete** | Corrections never destroy data |

**Why locking is safe here (important):** the longitudinal tiers are **append-only**. Clinical progress never needs an unlock — if bone protection is started, you **append a new `supportive_care_event`**; if the patient is restaged, you **append a new `staging_assessment`**. The nudge auto-resolves from the *new* row. So the lock only prevents **rewriting history**; it never blocks care. An unlock is needed only to **correct a mistake** in a 1:1 current-state record (demographics, pathology, treatment plan, outcome) or a mistyped dated row.

Fields carried on every entered record: `created_at`, `created_by`, `last_edited_at`, `locked`, `locked_at`, `unlocked_until`, `unlock_reason`.

---

## 2. The one core idea — today's status is read from the history

Everything the patient header shows — current stage, current treatment, current castration status — is simply **the most recent dated entry**. We never store a separate "current" box that could go stale. A worked example:

```
STAGING history for PCR-001:
  Row A  assessed_on = 2026-01-10   risk = High             castration = HSPC
  Row B  assessed_on = 2026-06-15   risk = Very High        castration = HSPC

CURRENT STAGE  = latest row by assessed_on  = Row B (Very High, HSPC)
→ Header badge shows "Very High · HSPC"
→ Care-gap engine reads risk = Very High   (Row B), not High (Row A)
→ When the patient later progresses, a Row C (castration = CRPC) is ADDED,
  never overwriting Row B — so the HSPC→CRPC transition date is preserved.
```

**🔧 For engineers** — the rule, stated precisely:
```
FUNCTION current(model, patient):
    RETURN newest row in `model` WHERE patient_code = patient  ORDER BY <date> DESC  LIMIT 1
```

---

## 3. Workflows — inputs, logic, outputs (pseudo-code + visuals)

Each workflow states: **Trigger → Inputs → Logic (pseudo-code) → Outputs → Derived data touched.**

### W1 · Patient onboarding
**In plain terms:** you register a new patient. The system creates their record, links them to you as treating clinician, and emails the MDT that a new patient has joined.

```mermaid
flowchart LR
  A[Add New Patient] --> B{Valid + not duplicate?}
  B -- no --> A
  B -- yes --> C[Create Patient hub row]
  C --> D[Attach to institution/department + primary clinician]
  D --> E[Notify MDT: new patient]
  C --> F[Appears in roster + cohort counts]
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: user submits Add-New-Patient
INPUTS : patient_code, age_at_diagnosis, coverage, state, referral_source,
         department_id, primary_clinician_id            // institution = the tenant (implicit)
LOGIC  :
  IF patient_code already exists within this tenant → reject "duplicate code"
  ELSE create Patient(hub) with inputs; set registry_enrolment_date = today
       create empty Pathology, Treatment_plan, Outcome shells
       route MDT new-patient notification (see W7)
OUTPUT : new Patient visible in roster; cohort counts +1
DERIVED: registrations-this-month, cohort volume recompute
```

### W2 · Clinical workup & staging
**In plain terms:** you enter the biopsy, staging and imaging. Staging and imaging are saved as **new dated entries** (so restaging never erases the old stage). Saving immediately re-checks the care-gap rules.

```mermaid
flowchart LR
  A[Enter biopsy/DRE/complaint] --> P[Save Pathology 1:1]
  B[Enter TNM + risk + castration] --> S[Add Staging assessment - dated]
  C[Enter imaging results] --> I[Add Imaging study rows - dated]
  S --> R[Recompute current stage/risk]
  I --> R
  R --> N[Run care-gap engine → W5]
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: clinician saves clinical assessment
INPUTS : pathology fields; staging fields (assessed_on defaults today);
         imaging modality+result rows
LOGIC  :
  Save Pathology (1:1, upsert)
  APPEND Staging_assessment row (never overwrite)
  FOR EACH imaging modality entered → APPEND Imaging_study row
  current_risk       = current(Staging, patient).eau_risk_category
  current_castration = current(Staging, patient).castration_status
  imaging_status(m)  = current(Imaging WHERE modality=m, patient).result  (else "Not done")
OUTPUT : updated current-state; header badges refresh
DERIVED: triggers W5 (care-gap re-evaluation)
```

### W3 · PSA capture & trend
**In plain terms:** each PSA you add is a new dated entry. The trend chart is drawn straight from these entries — nothing is duplicated or typed twice.

```mermaid
flowchart LR
  A[Add PSA row: date + value] --> L[Append PSA_reading - dated]
  L --> T[PSA trend chart reads this table]
  L --> D[Cohort PSA median/percentile recompute]
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: clinician adds a PSA entry
INPUTS : psa_date, psa_ng_ml, free_psa_pct?, psa_density?
LOGIC  : APPEND PSA_reading row (dated)
         latest_psa = current(PSA_reading, patient).psa_ng_ml
OUTPUT : patient trend chart (bound to PSA_reading, not hardcoded points)
DERIVED: cohort PSA median, percentile bands, diagnostic-PSA distribution
```

### W4 · Treatment planning & lines
**In plain terms:** the agreed plan (intent, MDT status) is stored once. Each therapy you start — ADT, then ARSI, then chemotherapy — is added as its own dated treatment line, so the sequence is preserved.

```mermaid
flowchart LR
  A[Agree pathway] --> P[Update Treatment_plan 1:1: intent, MDT, start]
  B[Start/refresh a therapy] --> L[Add Treatment_line - dated]
  C[Bone health / follow-up] --> S[Add Supportive-care event - dated]
  L --> N[Run care-gap engine → W5]
  S --> N
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: team records/updates treatment
INPUTS : plan header (intent, mdt_status, mdt_date, treatment_start_date);
         one Treatment_line (line_type, agent, start_date, status, +RT/CGHS fields);
         one Supportive_care_event (bone_protection, dexa follow-up, phq9, follow-up PSA date)
LOGIC  : upsert Treatment_plan; APPEND Treatment_line; APPEND Supportive_care_event
         current_arsi = current(Treatment_line WHERE line_type=ARSI).status (else "Not initiated")
         current_bone_protection = current(Supportive_care_event).bone_protection_therapy
OUTPUT : treatment state auditable; cohort treatment analytics update
DERIVED: ADT duration, time-to-treatment, CGHS delay, ARSI uptake → W5 + §5
```

### W5 · Care-gap (nudge) engine — the heart of the product
**In plain terms:** every time you save, the system re-reads the patient's *current* status and checks the 8 agreed rules. A gap that now applies opens a nudge; a gap that no longer applies **closes itself**. Nobody has to tick anything off.

```mermaid
flowchart TD
  T1[On clinical/treatment save] --> E[Evaluate 8 rules on CURRENT state]
  T2[Daily scheduled re-scan] --> E
  E --> C{Rule condition true?}
  C -- yes, no open nudge --> O[Open Nudge + log 'opened' event]
  C -- yes, already open --> K[Keep existing nudge]
  C -- no, but nudge open --> R[Auto-resolve + log 'resolved' event]
  O --> B[Recount severity + refresh badges/banner]
  R --> B
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: any staging/imaging/treatment/supportive save  (on-write only —
         all 8 rules are state-based, not time-based, so no daily cron is
         needed in v1; add one when a time-based rule appears)
INPUTS (current state per patient):
  risk = current(Staging).eau_risk_category
  castration = current(Staging).castration_status
  bone_scan  = imaging_status(bone_scan);   psma = imaging_status(psma_pet_ct)
  dexa = imaging_status(dexa);              germline = imaging_status(germline)
  bone_protection = current(Supportive).bone_protection_therapy
  arsi = current(Treatment_line WHERE ARSI).status
  next_follow_up_psa_date = current(Supportive).next_follow_up_psa_date
  phq9 = current(Supportive).phq9
LOGIC:
  FOR EACH rule IN guideline_rules(active):
     fired = evaluate(rule.condition, current_state)
     IF fired AND no open nudge with this rule_id:
         create Nudge(rule_id, severity, status=open); log Nudge_event(opened)
     IF (NOT fired) AND open nudge with this rule_id exists:
         set nudge.status = resolved; log Nudge_event(resolved)   // auto-resolve
OUTPUT: the patient's live nudge list (severity-coded, explainable)
DERIVED: urgent/warning/info counts, highest severity, primary focus,
         cohort gap counts, protocol score, nudge-trend (from Nudge_event)
NOTE  : "Acknowledge" (W6) does NOT resolve a nudge — only a changed source field does.
```

### W6 · Nudge lifecycle (acknowledge → route → resolve)
**In plain terms:** acknowledging a nudge records that you saw it and opens the message to the team. It does **not** close the nudge — only changing the underlying clinical field does that.

```mermaid
stateDiagram-v2
  [*] --> Open : rule fires (on write)
  Open --> Acknowledged : acknowledge & route to MDT (W7)
  Acknowledged --> Resolved : source field changed → rule stops firing (W5, auto)
  Open --> Resolved : source field changed (auto)
  Resolved --> Open : condition recurs
  Resolved --> [*]
```
> **No `snoozed` or `dismissed` state.** Clinical non-applicability is already expressed **in the data** — `bone_protection = "Not indicated"`, `mdt_status = "Not applicable"`, `germline = "Pending"` — so the rule simply never fires. Resolution is always data-driven. *(See `SIMPLIFICATION_REVIEW.md` T1/T2.)*
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: clinician clicks Acknowledge & log on a nudge
INPUTS : nudge_id, actor
LOGIC  : log Nudge_event(acknowledged); open Team modal prefilled (W7)
         (status stays 'open'/'logged' — resolution is data-driven, not a click)
OUTPUT : nudge shows "Logged with team"; discussion trail entry
DERIVED: nudge-trend "acted" count increments
```

### W7 · MDT notify & discussion (explicit steps + email via AWS SES)
**In plain terms:** you pick one colleague or the whole MDT, write the reason and note, preview it, and send. Each recipient gets an inbox item and an email. Everything is kept in the patient's discussion trail.

```mermaid
flowchart LR
  A[From nudge or patient] --> M{Recipient?}
  M -- specific --> M1[Pick MDT member]
  M -- all --> M2[Whole MDT panel]
  M1 --> F[Reason + subject + note]
  M2 --> F
  F --> P[Preview message]
  P --> Q[Create Notification queued]
  Q --> IN[In-app inbox item + task]
  Q --> EM[Send email via AWS SES]
  EM --> DS[Record delivery status: sent / bounced / failed]
  IN --> L[Append discussion_entry]
  DS --> L
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: acknowledge-from-nudge (W6)  OR  "Discuss with Team"  OR  new-patient (W1)
INPUTS : recipient_mode, recipient(s), reason, subject, note, patient_code
LOGIC (explicit steps):
  1. RESOLVE recipients:
        IF mode = member → [selected app_user]
        IF mode = all    → all users WHERE is_mdt_member = true
     recipient_emails = [u.email for u in recipients]        // email = the login identity
  2. RENDER template(reason, subject, note, patient_code, de-identified summary link)
  3. CREATE Notification(status = queued, recipients, body, at = now)
  4. FOR EACH recipient:
        a. CREATE in_app_notification  → inbox item (+ optional task) + live push (sse)
        b. SEND email via AWS SES      → from = configured verified sender,
                                          to  = recipient.email
        c. ON SES accept  → delivery_status = sent (store SES messageId)
           ON SES failure → delivery_status = failed → retry (transient) / flag (hard bounce)
  5. APPEND discussion_entry to the patient's discussion trail
  6. IF source = nudge → LOG Nudge_event(acknowledged)   // 'routed' is inferable from the notification row
OUTPUT : MDT informed (inbox + email); per-patient discussion log; per-recipient delivery status; toast
DERIVED: MDT-review-rate, collaboration audit, notification delivery metrics
```

**Notification triggers · channels · delivery (covers the whole notification surface):**
| Trigger | Fires from | Channel |
|---|---|---|
| Care-gap routed to MDT | W6 acknowledge | in-app + **email (SES)** |
| New patient registered | W1 | in-app + email (SES) to MDT panel |
| MDT review request / case discussion | Patient File "Discuss with Team" | in-app + email (SES) |
| ~~Urgent escalation (SLA)~~ | — | **Not in v1** (`SIMPLIFICATION_REVIEW.md` T3) |

- **Email transport = AWS SES.** Users log in with their **email ID** (the identity), and every configured notification is delivered to that email via SES. Sender is a verified SES domain/address; `messageId` + status (sent / bounced / complaint / failed) are stored on `Notification` for audit and delivery metrics; transient failures retry, hard bounces are flagged.
- **In-app inbox** is the primary channel (each notification creates an inbox item and, where relevant, a task); **email (SES)** mirrors it so nothing is missed. SMS / WhatsApp are future channels behind the same `Notification` record.

### W8 · Cohort analytics (derivation)
**In plain terms:** all the dashboard numbers are calculated from the entries above — none are typed by hand. Every chart can be clicked through to the patients behind it.

```mermaid
flowchart LR
  A[All patient + event data] --> V[Nightly/On-write derivations]
  V --> K[KPIs + benchmarks + protocol score]
  V --> N[Nudge trend from Nudge_event]
  K --> D[Dashboards]
  N --> D
  D --> P[Drill any chart → patient list]
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: on-write + scheduled refresh
INPUTS : every model in §1
LOGIC  : compute derived metrics (§5) as views; apply de-identification for
         non-clinical/sponsor roles
OUTPUT : Home + Population dashboards; every widget drillable to patient_code
DERIVED: see §5 (all of it)
```

### W9 · AI Buddy (governed, stepwise)
```mermaid
flowchart LR
  A[Open AI Buddy on a case] --> S1[Step: pathway review]
  S1 --> S2[Step: progression branch]
  S2 --> S3[Step: access/affordability]
  S3 --> S4[Step: trials]
  S4 --> J[Jump back to patient file]
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box; the plain summary is above)*
```
TRIGGER: user opens AI Buddy
INPUTS : structured record (read-only) + approved evidence/guideline packs
         + access-rule config
LOGIC  : stepwise review bounded to configured brain; NO free generation,
         NO inventing gaps, NO autonomous decisions, NO unlisted drug access
OUTPUT : explainable, step-by-step next-path view; links back to the file
DERIVED: none (read-only); every step audited
```

### W10 · Record edit window, lock & HOD unlock
**In plain terms:** a record you save stays editable for a couple of days, then locks. If a genuine mistake needs fixing later, the HOD can reopen it for 24 hours with a stated reason, and that is recorded.

```mermaid
stateDiagram-v2
  [*] --> Editable : record created
  Editable --> Locked : EDIT_WINDOW elapses (auto)
  Locked --> Unlocked : HOD unlocks (reason required, audited)
  Unlocked --> Locked : UNLOCK_WINDOW elapses (auto re-lock)
  Editable --> Editable : edit by clinician (audited)
  Unlocked --> Unlocked : corrective edit (audited)
```
**🔧 For engineers — the exact logic** *(clinicians can skip this box)*
```
CONFIG : EDIT_WINDOW = 48h        // editable after creation
         UNLOCK_WINDOW = 24h      // HOD-granted correction window
         UNLOCK_ROLES = [HOD]

FUNCTION can_edit(record, actor):
    IF record.locked = false AND now < record.created_at + EDIT_WINDOW      → TRUE
    IF record.unlocked_until IS NOT NULL AND now < record.unlocked_until    → TRUE
    ELSE                                                                    → FALSE

WORKFLOW auto_lock  (scheduled, hourly):
    FOR EACH record WHERE locked = false AND now >= created_at + EDIT_WINDOW:
        SET locked = true, locked_at = now
    FOR EACH record WHERE unlocked_until IS NOT NULL AND now >= unlocked_until:
        SET locked = true, unlocked_until = null          // auto re-lock

WORKFLOW unlock  (HOD only):
    INPUTS : record_id, reason (mandatory), actor
    IF actor.role NOT IN UNLOCK_ROLES        → deny (403)
    IF reason is empty                       → deny (reason required)
    SET locked = false, unlocked_until = now + UNLOCK_WINDOW, unlock_reason = reason
    LOG audit_event(action = 'unlock', record, actor, reason, at = now)
    OUTPUT: record editable until unlocked_until, then auto re-locks

ON EDIT (any record):
    IF NOT can_edit(record, actor) → deny "record locked — request HOD unlock"
    ELSE apply change; LOG audit_event(action='edit', old→new, actor)

NOTE: append-only tiers (PSA, staging, imaging, treatment_line, supportive_care,
      journey) never require an unlock to record clinical progress — you APPEND a
      new dated row. Unlock exists to correct mistakes, not to continue care.
```

### W12 · Record a visit, and chase the follow-up ⭐
**In plain terms:** you record that the patient attended, what state their disease is in, and when they should come back. Overnight, the system checks who has passed their due date and flags them as overdue.

```mermaid
flowchart LR
  A[Patient attends] --> V[Add Visit: date, type, disease state, outcome]
  V --> N[Set next visit due date]
  N --> P{Protocol interval for this disease state}
  P --> D[(Expected next visit)]
  D --> C[Nightly check]
  C -->|due date passed, no visit| O[⚠ Follow-up overdue nudge<br/>+ patient shows as Missed/Overdue]
  C -->|still in future| U[Shows as Upcoming]
  V --> L[Entries that day may link to this visit]
```

**🔧 For engineers — the exact logic** *(clinicians can skip this box)*
```
TRIGGER: (a) clinician saves a Visit   (b) nightly scheduled check
INPUTS : visit_date, visit_type, disease_state_at_visit, visit_outcome,
         next_visit_due_date (typed, or defaulted from the protocol interval)
LOGIC  :
  ON SAVE:
     APPEND visit row
     IF next_visit_due_date is blank:
         next_visit_due_date = visit_date + protocol_interval(disease_state_at_visit)
     IF visit_outcome = 'Treatment plan changed':
         mark current treatment_plan.plan_status = 'Superseded'
         prompt to APPEND a new treatment_plan (next line_of_therapy)

  NIGHTLY (this is the time-based rule):
     FOR EACH patient WHERE current(visit).next_visit_due_date < today
                        AND no visit recorded since that due date:
         open nudge 'follow_up_overdue'   (auto-resolves when the next visit is recorded)

OUTPUT : visit history; accurate Last visit / Upcoming / Missed-Overdue segments;
         overdue nudges
DERIVED: last_follow_up_date = latest visit date · visit_status · attendance rate
```

---

## 4. The 8 care-gap rules (full) + worked example

Inputs are always **current state** (latest dated rows). Each rule = one `guideline_rule` config row (versioned, clinically signed-off).

| # | rule_id | Condition | Severity | Next step (shown to user) |
|---|---|---|---|---|
| 1 | `bone_scan_missing` | `bone_scan = Not done` AND risk ∈ {High, Very High, M1} | **Urgent** | Complete bone scan / SPECT |
| 2 | `psma_missing` | `psma = Not done` AND risk ∈ {High, Very High} | **Urgent** | Complete PSMA PET-CT |
| 3 | `bone_protection_missing` | `bone_protection = Not started` | **Urgent** | Start bone protection plan |
| 4 | `dexa_missing` | `dexa = Not done` | **Warning** | Order DEXA baseline |
| 5 | `genomics_missing` | `germline = Not done` | **Warning** | Order germline/somatic testing |
| 6 | `arsi_readiness` | `castration = HSPC` AND risk ⊇ High AND `arsi = Not initiated` | **Warning** | Review ARSI intensification |
| 7 | `followup_psa_missing` | `next_follow_up_psa_date` is empty | **Info** | Schedule follow-up PSA |
| 8 | `psychosocial_prompt` | `phq9` blank or "Not done" | **Info** | Complete PHQ-9 screening |

**Worked example — patient `PCR-001`** (values from the workbook sample):
```
CURRENT STATE:
  risk = High         castration = HSPC
  bone_scan = Not done   psma = Not done   bone_protection = Not started
  dexa = Not done        germline = Not done   arsi = Not initiated
  next_follow_up_psa_date = 2026-07-18 (present)   phq9 = Not done

EVALUATE:
  1 bone_scan_missing      → Not done AND High           → FIRES  (Urgent)
  2 psma_missing           → Not done AND High           → FIRES  (Urgent)
  3 bone_protection_missing→ Not started                 → FIRES  (Urgent)
  4 dexa_missing           → Not done                    → FIRES  (Warning)
  5 genomics_missing       → Not done                    → FIRES  (Warning)
  6 arsi_readiness         → HSPC AND High AND Not init   → FIRES  (Warning)
  7 followup_psa_missing   → date present                → does not fire
  8 psychosocial_prompt    → phq9 = Not done             → FIRES  (Info)

RESULT: 7 open nudges → Urgent 3 · Warning 3 · Info 1
        Highest severity = Urgent ; Primary focus = "Complete bone scan / SPECT"
        Header banner = "Urgent: 3 actions require attention"

LATER: clinician records bone_scan = "Done — no metastases" and saves.
  → W5 re-runs → rule 1 no longer fires → nudge #1 AUTO-RESOLVES
  → counts become Urgent 2 · Warning 3 · Info 1 (no manual "close" needed).
```

---

## 5. Derived data — every computed number + its formula

> **Full catalogue:** all **22** workbook derived fields (plus platform-derived current-state and cohort metrics), with explicit formulas and **band edges**, live in **`DATA_TYPES_ENUMS_AND_DERIVED_FIELDS.md`**. The table below is the summary.

Nothing here is typed; all is computed from §1 (pseudo-code).

| Derived value | Formula (pseudo-code) | Feeds |
|---|---|---|
| current_stage / risk / castration | `current(Staging).<field>` | Header badges, rule inputs |
| latest_psa | `current(PSA_reading).psa_ng_ml` | Header, cohort median |
| ADT duration | `today − current(Treatment_line WHERE ADT).start_date` | Treatment dashboard, bone-gap logic |
| time-to-treatment | `treatment_start_date − diagnosis_date` | Access/delay analytics |
| CGHS delay | `(cghs_approval_date OR today) − cghs_request_date` | Access analytics |
| gap counts | `COUNT(Nudge WHERE status=open GROUP BY severity)` | Home KPIs, banner |
| protocol score | `weighted % of rule-families passing across cohort` | Home + Quality dashboard |
| record completeness | `% required fields present per field-group` | Home, incomplete-records list |
| benchmark deltas | `cohort % vs NCCN target` for ARSI/PSMA/bone/MDT | Benchmark cards |
| nudge trend | `COUNT(Nudge_event GROUP BY action, period)` | Nudge-trend chart |
| KM survival | `survival(risk_group, recurrence dates)` | Outcomes dashboard |
| registrations/month | `COUNT(Patient GROUP BY month(registry_enrolment_date))` | Home + Overview |

**Access rule on all derived data:** clinical roles see identified/in-scope; **ops/quality/sponsor see de-identified aggregate only** (masked drill rows).

---

## 6. Visual master flow (end-to-end)
```mermaid
flowchart TD
  ON[Onboard institution + doctors] --> ADD[Register patient - W1]
  ADD --> WU[Workup + staging - W2]
  ADD --> PSA[PSA history - W3]
  ADD --> TX[Treatment lines - W4]
  WU --> ENG[Care-gap engine - W5]
  TX --> ENG
  ENG --> NUD[Nudges on patient file]
  NUD --> ACK[Acknowledge - W6]
  ACK --> MDT[MDT notify + discussion - W7]
  MDT --> FIX[Clinician acts → source field changes]
  FIX --> ENG
  ENG --> ANA[Cohort analytics - W8]
  ANA --> DRILL[Drill chart → patient → file]
  DRILL --> NUD
  NUD --> AIB[AI Buddy review - W9]
```

---

## 7. Sign-off checklist (for the clinical team)

Please confirm, amend, or reject each:
1. **Data models (§1)** — are the variables per model complete and correctly named for clinical use? Any field missing (e.g. additional comorbidity, biomarker, toxicity grade)?
2. **Current-state rule (§2)** — agreed that "current stage/line/castration" = latest dated entry, and that restaging/progression is a **new** row (never an overwrite)?
3. **Cardinality calls** — `Pathology` and `Outcome` as 1-per-patient (re-biopsy → new row); `Supportive-care` as a **dated** log (bone-protection audit) — agreed?
4. **The 8 rules (§4)** — conditions, severities, and next-step wording clinically correct? Any rule to add/remove/retune (e.g. thresholds, risk sets)?
5. **Auto-resolve semantic (§3 W5/W6)** — agreed that acknowledging routes to MDT but only a changed source field resolves a nudge?
6. **Derived metrics (§5)** — formulas acceptable; benchmark targets (ARSI 60%, PSMA 85%, bone 85%, MDT 95%) confirmed by clinical governance?
7. **Governance** — who signs off the rule pack + evidence packs (independent of any sponsor)?
8. **Identity model** — de-identified registry (recommended) vs identified — confirm (drives everything downstream).
9. **Visits (§1.6)** — confirm the visit types, the follow-up intervals by disease state, and that a treatment plan is **one-to-many** (a new dated plan at each progression).
10. **Tenancy** — confirmed **tenant = institution** (no `institution_id`); cross-institution reporting via a de-identified aggregation layer — agreed?
11. **Roles & access (§1.1)** — **no department**; every clinician sees that institution's patients; **HOD is the privileged role** (unlock, notify-all-MDT, audit); Ops/Quality see de-identified aggregates only. Agreed?
12. **Record locking (§1.8)** — confirm **`EDIT_WINDOW` = 48 h**, **`UNLOCK_WINDOW` = 24 h**, **unlock restricted to HOD** with a mandatory reason. Do these durations suit clinic practice? Should any other role be allowed to unlock?
13. **Cardinality & provenance (§1.7)** — confirm every model is either entered on a named screen or derived, and the 1:1 / 1:N calls — in particular **one treatment *plan* (1:1) vs many treatment *lines* (1:N)**.

Once §7 is signed, this spec becomes the build contract; engineering maps it to the platform per `PROSTACARE_BUILD_SPEC_V1.md` / `NOVA-EDGE-FEASIBILITY.md`.

---

*Companion docs: `PROSTACARE_BUILD_SPEC_V1.md` (platform/NOVA Edge mapping), `FLOW-CLARITY-AND-OPEN-QUESTIONS.md` (decisions & open questions), `ProstaCare_Nudge_Logic_Handoff.md` (source of the 8 rules), and the `ProstaCare_Schema_08072026_V2.xlsx` workbook (authoritative field dictionary + value lists).*
