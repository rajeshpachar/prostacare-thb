# ProstaCare Demo: Current Nudge Logic

## Summary

The current nudge engine is a client-side ruleset implemented in `patient-file.html`. It reads specific form fields from the patient file, evaluates a fixed set of rule conditions, and renders patient-level nudges with `urgent`, `warning`, or `info` severity.

This is live only inside the patient file. The home and population analytics nudge trend charts are still driven by static demo arrays and are not calculated from patient records.

## 1. Scope

This note documents the current prototype logic that powers the **Nudges & Alerts** section inside the patient file.

It covers:

- Which inputs are read by the rule engine
- Which nudges are currently generated
- When nudges are recalculated
- What happens when the user clicks **Acknowledge & log**
- What is still demo-only and not yet production logic

## 2. Inputs Read by the Rule Engine

The `computeNudges()` function reads the following patient-file fields:

| Field ID | Meaning |
| --- | --- |
| `risk-s` | Risk group / disease context |
| `bone-s` | Bone scan / SPECT status |
| `psma-s` | PSMA PET-CT status |
| `bp-s` | Bone protection therapy status |
| `dexa-s` | DEXA scan status |
| `gen-s` | Germline / somatic genomics status |
| `cast-s` | Castration status |
| `arsi-s` | ARSI treatment status |
| `fup-d` | Follow-up visit / PSA date |

Values are read using the helper `gv(id)`, which fetches the current value from the DOM.

## 3. Active Nudge Rules

### 3.1 Bone scan / SPECT not performed

**Condition**

- `bone-s === "Not done"`
- `risk-s` includes `High`, `Very`, or `M1`

**Output**

- Severity: `urgent`
- Tag: `Action required`
- Purpose: flags staging incompleteness in higher-risk disease

### 3.2 PSMA PET-CT not done

**Condition**

- `psma-s === "Not done"`
- `risk-s` includes `High` or `Very`

**Output**

- Severity: `urgent`
- Tag: `Action required`
- Purpose: flags incomplete staging where PSMA imaging is expected in the demo logic

### 3.3 Bone protection therapy not initiated

**Condition**

- `bp-s === "Not started"`

**Output**

- Severity: `urgent`
- Tag: `Action required`
- Purpose: flags missing bone-protection action in the current treatment flow

### 3.4 DEXA scan not performed

**Condition**

- `dexa-s === "Not done"`

**Output**

- Severity: `warning`
- Tag: `Recommendation`
- Purpose: highlights missing baseline bone-density workup

### 3.5 Germline / somatic genomic testing not ordered

**Condition**

- `gen-s === "Not done"`

**Output**

- Severity: `warning`
- Tag: `Recommendation`
- Purpose: highlights missing genetics workup

### 3.6 ARSI intensification opportunity

**Condition**

- `cast-s === "Hormone-sensitive (HSPC)"`
- `risk-s` includes `High`
- `arsi-s === "Not initiated"`

**Output**

- Severity: `warning`
- Tag: `Recommendation`
- Purpose: surfaces an ARSI intensification prompt in high-risk hormone-sensitive disease

### 3.7 Follow-up PSA visit not scheduled

**Condition**

- `fup-d` is empty

**Output**

- Severity: `info`
- Tag: `Reminder`
- Purpose: reminds the user to schedule follow-up monitoring

### 3.8 Psychosocial and sexual health screening

**Condition**

- Always added in the current demo

**Output**

- Severity: `info`
- Tag: `Reminder`
- Purpose: acts as a persistent documentation reminder

## 4. Recompute and Display Behavior

Nudges are recalculated when:

- The patient file initializes
- The user clicks **Save & Refresh Nudges**
- A team-notification entry is sent from the nudge flow

After evaluation, the engine:

- Rebuilds the nudge card list in `#nudge-container`
- Updates the sidebar badge count
- Counts `urgent` nudges
- Shows or hides the top alert banner based on whether any urgent nudges exist

## 5. What `Acknowledge & log` Does Today

The button label on each nudge is:

- `Acknowledge & log ->` when no matching log entry exists yet
- `Logged with team ->` when a team notification has already been stored for the same nudge title

When the user clicks the action:

1. The nudge opens the team discussion modal through `openTeamModalFromNudge(index)`.
2. The modal is prefilled with:
   - `sourceType: "nudge"`
   - `sourceTitle`: the nudge headline
   - reason: `FYI` for info nudges, otherwise `Care gap`
   - a prefilled subject and note
3. When the user sends the notification, an entry is stored in browser storage.
4. `computeNudges()` runs again.

Important: this does **not** resolve the nudge. The nudge will continue to appear unless the underlying source fields are changed so the rule no longer fires.

## 6. Current Demo Limitations

### 6.1 Patient-file nudges are live, but home/dashboard trends are static

The patient file uses real in-browser rule evaluation. However:

- `index.html` uses hard-coded nudge trend arrays for the home dashboard
- `population-analytics.html` uses hard-coded nudge trend arrays for the analytics dashboard

This means patient-file edits do not currently recalculate the cohort trend charts.

### 6.2 Rule logic is fixed in code

Rules are hard-coded in `computeNudges()` and are not:

- versioned
- configurable by admin
- governed through a clinical rule editor
- backed by server-side audit logic

### 6.3 State is browser-local

Notification logs and demo interactions are stored locally in the browser. There is no shared backend, no cross-user sync, and no durable audit service in this prototype.

## 7. Production-Oriented Next Step

If this is taken forward beyond the prototype, the next logical architecture step would be:

- move rule definitions out of front-end code
- evaluate rules on a backend service or governed rules engine
- version each rule with clinical sign-off metadata
- separate `opened`, `viewed`, `acted`, and `resolved` states
- connect patient-level nudge events to cohort analytics so trend charts become real

## 8. Source References

This note is based on the current implementation in:

- `patient-file.html`
  - `gv(id)`
  - `computeNudges()`
  - `openTeamModalFromNudge(index)`
  - `sendTeamNotification()`
- `index.html`
  - home dashboard nudge trend demo arrays
- `population-analytics.html`
  - population dashboard nudge trend demo arrays
