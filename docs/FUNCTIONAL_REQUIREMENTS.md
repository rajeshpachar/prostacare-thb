# ProstaCare Functional Requirements

## 1. Login and Session

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-001 | Provide a demo login screen with user ID and password fields. | Must | Implemented as static demo login. |
| FR-002 | Show an error state for invalid demo credentials. | Must | Implemented. |
| FR-003 | Support production authentication, role-based access, and session timeout. | Future | Out of current static scope. |

## 2. Shell Navigation

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-010 | Provide top-level navigation for Home, Patient List, and Dashboard. | Must | Implemented. |
| FR-011 | Open patient files and the population dashboard inside a viewer frame. | Must | Implemented. |
| FR-012 | Preserve route state for patient and dashboard views within the demo session. | Should | Implemented with browser state/local storage patterns. |
| FR-013 | Provide clear back navigation from embedded views. | Must | Implemented. |

## 3. Home Dashboard

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-020 | Show cohort health KPIs including open care gaps, record completeness, and new registrations. | Must | Implemented. |
| FR-021 | Show benchmark comparison against guideline or protocol expectations. | Must | Implemented as demo content. |
| FR-022 | Show nudge trend analysis with weekly and monthly controls. | Should | Implemented. |
| FR-023 | Provide drilldowns from KPI cards to affected patient rows. | Must | Implemented. |
| FR-024 | Let users open patient files from drilldown rows. | Must | Implemented. |
| FR-025 | Provide guideline quick-reference content from the home surface. | Should | Implemented. |

## 4. Patient List

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-030 | Display a list of available patient records. | Must | Implemented with sample records. |
| FR-031 | Search patients by available demographic or clinical identifiers. | Must | Implemented. |
| FR-032 | Filter patient queues by visit status such as last visit, upcoming/planned, or missed/overdue. | Should | Implemented. |
| FR-033 | Provide a privacy toggle to hide or reveal patient names. | Must | Implemented. |
| FR-034 | Open a selected patient record from the queue. | Must | Implemented. |
| FR-035 | Start a new patient onboarding flow. | Should | Implemented as demo modal. |

## 5. New Patient Onboarding

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-040 | Capture basic new patient details from a modal form. | Should | Implemented for demo flow. |
| FR-041 | Generate a new patient context that can open in the patient file viewer. | Should | Implemented. |
| FR-042 | Show a team notification preview after a new patient is registered. | Should | Implemented as email-style preview. |
| FR-043 | Persist new patient records across users and devices. | Future | Requires backend. |

## 6. Patient File

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-050 | Display patient demographics, identifiers, risk state, PSA, stage, and doctor context. | Must | Implemented with sample/contextual data. |
| FR-051 | Allow patient name visibility to be toggled. | Must | Implemented. |
| FR-052 | Capture and display clinical profile fields including referral reason, DRE, biopsy, risk group, staging, imaging, and comorbidities. | Must | Implemented as prototype form sections. |
| FR-053 | Display PSA history in both table and trend chart form. | Must | Implemented. |
| FR-054 | Allow adding PSA rows during the browser session. | Should | Implemented. |
| FR-055 | Capture treatment intent, MDT status, ADT, ARSI, RT, bone health, and follow-up planning. | Must | Implemented as prototype form sections. |
| FR-056 | Show a patient journey timeline and allow additional timeline entries. | Should | Partially implemented for demo. |
| FR-057 | Print a patient summary. | Should | Implemented via browser print. |

## 7. Nudges and Care Gaps

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-060 | Compute patient-level nudges from entered clinical and treatment fields. | Must | Implemented client-side for demo. |
| FR-061 | Show severity, rationale, and suggested action for each nudge. | Must | Implemented. |
| FR-062 | Allow a nudge to initiate team discussion logging. | Must | Implemented. |
| FR-063 | Show acknowledged or completed actions. | Should | Implemented as demo content. |
| FR-064 | Support production rules governance, versioning, and auditability. | Future | Requires clinical governance and backend. |

## 8. Team Discussion and Notifications

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-070 | Open a team discussion modal from the patient file or a nudge. | Must | Implemented. |
| FR-071 | Support sending to a specific team member selected from a directory. | Must | Implemented as demo directory. |
| FR-072 | Support sending to all configured MDT members. | Should | Implemented. |
| FR-073 | Capture reason, subject, note, and optional patient summary inclusion. | Must | Implemented. |
| FR-074 | Preview the received notification. | Should | Implemented. |
| FR-075 | Store a visible team discussion log for the patient. | Must | Implemented in browser storage. |
| FR-076 | Send real email or messaging notifications. | Future | Requires backend and integrations. |

## 9. Rx and Document Uploads

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-080 | Let users upload PDF or image prescription files for a patient. | Should | Implemented using browser storage. |
| FR-081 | List uploaded files for the patient. | Should | Implemented. |
| FR-082 | Open an uploaded file from the patient file. | Should | Implemented. |
| FR-083 | Remove uploaded files. | Should | Implemented. |
| FR-084 | Store production documents securely with retention and audit controls. | Future | Requires backend. |

## 10. Guideline Reference

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-090 | Provide guideline reference views for India practice, NCCN comparison, staging, and references. | Should | Implemented as demo modal/content. |
| FR-091 | Link relevant guideline signals to patient nudges and cohort quality gaps. | Should | Implemented in demo language. |
| FR-092 | Maintain guideline content through a reviewed source and versioning workflow. | Future | Requires content governance. |

## 11. Population Analytics

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-100 | Show population overview for total patients, high-risk patients, median PSA, and active treatment. | Must | Implemented. |
| FR-101 | Show clinical profile analytics for PSA, Gleason, staging, comorbidities, and imaging completeness. | Must | Implemented. |
| FR-102 | Show treatment analytics for ADT, RT, ARSI, chemotherapy, pathway flow, and time-to-treatment. | Must | Implemented. |
| FR-103 | Show outcome analytics for PSA response, nadir, recurrence, progression, and response by treatment. | Should | Implemented with representative data. |
| FR-104 | Show quality and gap analytics for protocol adherence, PSMA, DEXA, bone Rx, genetics, MDT, and PSA monitoring. | Must | Implemented. |
| FR-105 | Show demographics and geography analytics. | Should | Implemented. |
| FR-106 | Allow chart drilldowns to show affected patient rows. | Must | Implemented. |
| FR-107 | Export or print dashboard reports. | Should | Implemented through browser print; download button is demo UI. |

## 12. Privacy, Audit, and Data Handling

| ID | Requirement | Priority | Current Prototype Status |
| --- | --- | --- | --- |
| FR-110 | Clearly avoid real patient data in the prototype. | Must | Assumed demo data. |
| FR-111 | Mask patient names until explicitly revealed. | Must | Implemented. |
| FR-112 | Store audit logs for user actions in production. | Future | Requires backend. |
| FR-113 | Support secure data storage, access control, encryption, and compliance controls in production. | Future | Requires backend and security architecture. |

