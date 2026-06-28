# ProstaCare India — Visual Workflows, User Stories & Feature Map

Visual companion to `PRODUCT-PRD.md`. Diagrams are written in **Mermaid** (renders on GitHub and most markdown viewers). Each major capability has: a user story, a visual flow, and acceptance criteria.

---

## 0. Product at a Glance — Capability Map

```mermaid
mindmap
  root((ProstaCare<br/>India))
    Home Command Center
      Cohort KPIs
      Pulse indicators
      Benchmark gap cards
      Attention queue
      Nudge trends
    Patient File
      Demographics + IDs
      Clinical assessment + PSA
      Treatment plan
      Patient journey
      Documents / Rx
    Decision Support
      Nudges engine
      Guideline reference
      Acknowledge + log
    MDT Collaboration
      Notify member / all
      Preview + send
      Discussion log
    Population Analytics
      6 analytic domains
      35+ visualizations
      Universal drill-down
      Export / report
    Platform
      Roles + access
      Privacy masking
      Audit
      India localization
```

---

## 1. End-to-End Persona Journey (HOD)

```mermaid
flowchart LR
    L[Login] --> H[Home command center]
    H -->|scan KPIs| B{Where is the<br/>biggest gap?}
    B -->|benchmark card| D[Drill to affected patients]
    B -->|pulse: pending nudges| Q[Quality & gaps view]
    B -->|attention queue| P[Open flagged patient]
    D --> P
    Q --> D
    P --> N[Review nudges]
    N --> A[Acknowledge & log]
    A --> M[Notify MDT]
    M --> R[(Gap documented<br/>+ routed)]
    R --> H
```

---

## 2. Core Value Loop — Gap → Nudge → Action → Closure

```mermaid
flowchart TD
    subgraph Population
      G1[Top care gaps<br/>e.g. 42 no bone protection]
    end
    subgraph Patient
      G2[Nudge: bone protection<br/>not started — URGENT]
      G3[Acknowledge & log]
    end
    subgraph MDT
      G4[Notify member / all]
      G5[Discussion log entry]
    end
    subgraph Closure
      G6[Record updated]
      G7[Nudge resolves]
      G8[Cohort metric improves]
    end
    G1 -->|drill to patient| G2 --> G3 --> G4 --> G5 --> G6 --> G7 --> G8
    G8 -.recompute.-> G1
```

---

## 3. User Story Map (release-oriented)

```mermaid
flowchart LR
    subgraph EPIC1[Epic: Manage Patient Record]
      U11[See patient at a glance]
      U12[Enter / edit demographics + IDs]
      U13[Record PSA + staging + pathology]
      U14[Plan treatment + bone health]
      U15[Track journey timeline]
    end
    subgraph EPIC2[Epic: Decision Support]
      U21[See prioritized care gaps]
      U22[Understand the guideline rationale]
      U23[Acknowledge & log a nudge]
    end
    subgraph EPIC3[Epic: MDT Collaboration]
      U31[Notify a member or all MDT]
      U32[Preview before sending]
      U33[See discussion history]
    end
    subgraph EPIC4[Epic: Population Insight]
      U41[See cohort vs benchmark]
      U42[Drill any metric to patients]
      U43[Filter by time / segment]
      U44[Export a report]
    end
    subgraph EPIC5[Epic: Platform]
      U51[Log in by role]
      U52[Mask / reveal patient identity]
      U53[Upload & view documents]
      U54[Onboard a new patient + notify]
    end
```

---

## 4. Feature Workflows (per capability)

### 4.1 Login & Role-Scoped Entry
**Story:** *As a clinician, I log in and land on a workspace scoped to my role so I only see patients I'm responsible for.*

```mermaid
flowchart LR
    A[Open app] --> B[Authenticate<br/>SSO / credentials]
    B -->|valid| C{Role?}
    B -->|invalid| B
    C -->|HOD| D[Department cohort home]
    C -->|Treating clinician| E[My panel home]
    C -->|MDT member| F[Shared patients + inbox]
    C -->|Data staff| G[Incomplete-records queue]
```
**Acceptance:** access scope enforced server-side · session + lockout · all entries audited.

---

### 4.2 Home → Navigate / Drill
**Story:** *As an HOD, I scan cohort health and jump straight to whatever needs attention.*

```mermaid
flowchart TD
    H[Home] --> K[Live KPIs + pulse indicators]
    K --> C1[Benchmark gap card] -->|drill| PL[Patient list for that gap]
    K --> C2[Attention queue] --> PF[Patient file]
    K --> C3[Pending-nudges pulse] --> QV[Quality & gaps]
    K --> C4[Go to dashboard] --> DASH[Population analytics]
    PL --> PF
    QV --> PL
```
**Acceptance:** every KPI computed live · each metric drillable to named patients · state deep-linkable.

---

### 4.3 Patient File — Record & Edit
**Story:** *As a treating clinician, I view and complete a patient's record across demographics, clinical, treatment, and journey.*

```mermaid
flowchart LR
    PF[Patient file] --> S1[Nudges & alerts]
    PF --> S2[Demographics + IDs]
    PF --> S3[Clinical: PSA, biopsy, staging, imaging]
    PF --> S4[Treatment: ADT, RT, bone health]
    PF --> S5[Journey timeline]
    S2 & S3 & S4 --> SV[Save -> validate + version + audit]
    SV --> RC[Recompute nudges]
    RC --> S1
```
**Acceptance:** PSA chart is data-bound · saves persist with versioning · nudges recompute on change.

---

### 4.4 Nudges (Decision Support)
**Story:** *As a clinician, I see guideline-based care gaps for this patient, ranked by urgency, with the reason and how to act.*

```mermaid
flowchart TD
    REC[Patient record] --> RE[Rules engine<br/>vs guideline version]
    RE --> N1[Urgent nudges]
    RE --> N2[Recommendations]
    RE --> N3[Reminders]
    N1 & N2 & N3 --> CARD[Nudge card:<br/>title · rationale · guideline cite]
    CARD --> ACK[Acknowledge & log]
    CARD --> RT[Route to MDT]
    ACK --> HIST[Care-decision history]
    RT --> NOTIFY[MDT notify flow 4.5]
```
**Acceptance:** rules versioned & clinically validated · status open/logged/resolved · rolls up to cohort metrics.

---

### 4.5 MDT Notify & Discussion
**Story:** *As a clinician, I notify a colleague or the whole MDT about a patient, preview the message, send it, and keep a discussion trail.*

```mermaid
flowchart LR
    T[Compose notification] --> M{Recipient?}
    M -->|specific| M1[Typeahead MDT directory]
    M -->|all MDT| M2[Whole team]
    M1 & M2 --> F[Reason · subject · note<br/>+ secure summary link]
    F --> PV[Preview rendered message]
    PV --> SEND[Send via email / in-app]
    SEND --> DEL[(Delivery tracked)]
    SEND --> LOG[Discussion log entry]
    LOG --> RV[Re-view sent item]
```
**Acceptance:** real delivery + status · summary links access-controlled & expiring · full audit.

---

### 4.6 Documents (Rx & Reports)
**Story:** *As staff, I attach prescriptions/reports to a patient and the team can view them.*

```mermaid
flowchart LR
    U[Upload PDF/image] --> ST[Secure object storage]
    ST --> LIST[Document list w/ metadata]
    LIST --> OPEN[View]
    LIST --> RM[Remove]
    OPEN & RM --> AUD[(Audited)]
```
**Acceptance:** scoped access · uploads/views/removes audited.

---

### 4.7 New Patient Onboarding + Team Notify
**Story:** *As a clinician, I register a new patient and the MDT is automatically notified.*

```mermaid
flowchart TD
    A[Add patient form] --> V{Valid + not duplicate?}
    V -->|no| A
    V -->|yes| REG[Create record]
    REG --> Q[Appears in roster]
    REG --> NOTE[Notify MDT: new-patient summary + open link]
    NOTE --> DEL[(Delivery tracked)]
    Q --> PF[Open patient file]
```
**Acceptance:** duplicate detection · notification reaches MDT with working link · immediate roster visibility.

---

### 4.8 Population Analytics + Drill-Down
**Story:** *As an HOD, I explore cohort metrics, compare to benchmarks, and drill any chart to the patients behind it.*

```mermaid
flowchart LR
    DASH[Dashboard] --> SEC{Section}
    SEC --> O[Overview]
    SEC --> CL[Clinical]
    SEC --> TR[Treatment]
    SEC --> OU[Outcomes]
    SEC --> QA[Quality & gaps]
    SEC --> DE[Demographics]
    O & CL & TR & OU & QA & DE --> CH[Chart / KPI]
    CH -->|time filter re-queries| CH
    CH -->|click element| DP[Drill panel: filtered patients + stats]
    DP -->|select patient| PF[Patient file<br/>back to dashboard]
    DASH --> EXP[Export / report]
```
**Acceptance:** all metrics data-bound · time filters re-query · every chart drillable to patients · export works.

---

### 4.9 Privacy Masking (cross-cutting)
**Story:** *As a clinician, patient identities are masked by default and I reveal them deliberately.*

```mermaid
flowchart LR
    V[View any screen] --> MASK[Names/contact masked by default]
    MASK --> TOG{Reveal?}
    TOG -->|toggle on| SHOW[Visible + reveal audited]
    SHOW --> SYNC[State persists across all views]
    MASK --> SYNC
```
**Acceptance:** consistent across home/list/file/analytics · per-user persisted · reveal events audited.

---

## 5. Roles × Features (RACI-style matrix)

```mermaid
flowchart TB
    classDef ok fill:#1e9b61,color:#fff,stroke:#0a5;
```

| Feature | HOD | Treating clinician | MDT member | Data staff | Admin |
|---|:--:|:--:|:--:|:--:|:--:|
| Cohort home / analytics | ✅ full | ✅ own panel | 🔸 shared | — | ✅ |
| Patient record edit | ✅ | ✅ | 🔸 view/contribute | ✅ entry | ✅ |
| Nudges — act/log | ✅ | ✅ | 🔸 | — | ✅ |
| MDT notify / discuss | ✅ | ✅ | ✅ | — | ✅ |
| Documents upload/view | ✅ | ✅ | 🔸 view | ✅ | ✅ |
| New patient onboard | ✅ | ✅ | — | ✅ | ✅ |
| Reveal identity (audited) | ✅ | ✅ | 🔸 | 🔸 | ✅ |
| User / role / config | — | — | — | — | ✅ |

✅ full · 🔸 scoped/limited · — none

---

## 6. State Lifecycle — a Care Gap (Nudge)

```mermaid
stateDiagram-v2
    [*] --> Open: rules engine emits nudge
    Open --> Logged: acknowledge & route to MDT
    Logged --> InProgress: MDT action / order placed
    InProgress --> Resolved: record updated + criteria met
    Open --> Dismissed: clinically not applicable (reason)
    Resolved --> [*]
    Dismissed --> [*]
    Resolved --> Open: re-triggers if criteria recur
```

---

## 7. System Context (production target)

```mermaid
flowchart TB
    User[Clinician / Staff] --> APP[ProstaCare India app]
    APP --> SVC[Application services + rules engine]
    SVC --> DB[(Clinical data store)]
    SVC --> OBJ[(Document storage)]
    SVC --> AUD[(Audit log)]
    SVC <--> ABDM[ABHA / ABDM]
    SVC <--> HIS[HIS / EMR / LIS / RIS]
    SVC <--> TPA[Coverage: CGHS / PMJAY / ESIC]
    SVC --> MSG[Email / secure messaging]
    SVC --> GL[Versioned guideline content]
```

---

### Notes
- Diagrams describe the **intended product**, not the demo's iframe/localStorage implementation.
- Keep this file in sync with `PRODUCT-PRD.md` (requirements) and the as-built inventory in `FEATURE-PRD.md` / `FLOW-PRD.md`.
