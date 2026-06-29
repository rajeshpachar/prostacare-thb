# ProstaCare Scope

## 1. Scope Summary

This repository currently contains a static HTML prototype of ProstaCare India. The scope of this version is to demonstrate the intended prostate cancer registry, care-gap, patient-file, MDT coordination, and analytics experience using sample data.

## 2. In Scope for Current Repository

- Static browser demo for stakeholder review.
- Demo login flow.
- Home dashboard with cohort pulse, care gaps, benchmark cards, nudge trends, and drilldowns.
- Patient list with search, filters, privacy toggle, and open-file actions.
- New patient onboarding demo modal and team notification preview.
- Patient file experience covering demographics, clinical profile, PSA history, staging, treatment planning, nudges, patient journey, guideline reference, Rx upload, team discussion, and print summary.
- Client-side nudge calculation for demonstration.
- Client-side team notification preview and patient-level discussion log.
- Browser-based Rx upload storage for demo files.
- Population analytics dashboard across overview, clinical profile, treatment, outcomes, quality gaps, and demographics/geography.
- Chart drilldowns from cohort analytics to affected patient rows.
- Static deployment through direct file hosting or simple web hosting.

## 3. Out of Scope for Current Repository

- Production authentication and authorization.
- Real patient data ingestion or storage.
- Real email, SMS, WhatsApp, EHR, HIS, LIS, PACS, payer, or ABHA integrations.
- Multi-user data synchronization.
- Server-side audit trail.
- Production database schema and API implementation.
- Clinical rules governance, medical review workflow, and versioned guideline publishing.
- Regulatory-grade clinical decision support validation.
- Consent management and legal compliance workflows.
- Enterprise deployment, monitoring, backup, and disaster recovery.

## 4. Demo Data Scope

The prototype uses representative prostate cancer records, including sample patient identifiers, PSA values, risk groups, treatment states, care gaps, and cohort counts. These records are intended to demonstrate workflow and should not be treated as real clinical data.

## 5. Functional Scope Boundaries

### 5.1 Patient-Level Workflow

In scope:

- Search and open a patient record.
- Review clinical and treatment sections.
- Review and refresh patient nudges.
- Upload and view local Rx files.
- Start a team discussion from the patient record or a nudge.
- Print the current patient summary.

Out of scope:

- Persisting patient edits to a shared database.
- Sending real notifications.
- Validating clinical orders.
- Reconciling source-of-truth hospital data.

### 5.2 Cohort-Level Workflow

In scope:

- Review aggregate cohort metrics.
- Navigate analytics sections.
- Drill into chart segments and patient rows.
- Move from cohort-level gaps to patient records.
- Print/export through browser functionality.

Out of scope:

- Live data refresh from source systems.
- Configurable analytics definitions.
- Statistical validation of demo metrics.
- Production BI permissions and row-level access.

### 5.3 Guideline and Nudge Workflow

In scope:

- Show guideline-oriented demo content.
- Explain why a care gap is being flagged.
- Link selected nudges to team discussion logging.

Out of scope:

- Maintaining authoritative guideline content.
- Automatic treatment recommendation approval.
- Replacing MDT or clinician review.

## 6. Future Production Scope

A production version should add:

- Secure backend services and database.
- Role-based authentication and user management.
- Real patient registry data model.
- Integration adapters for hospital and diagnostic systems.
- Document storage with virus scanning, access controls, and retention policies.
- Notification delivery with templates, delivery status, and audit logs.
- Clinical rules engine with reviewed guideline versions.
- Consent, privacy, and compliance workflows.
- Admin console for team directory, rules, facilities, and configuration.
- Reporting exports with reproducible data definitions.

## 7. Acceptance Criteria for Current Documentation Scope

- PRD, functional requirements, and scope documents exist in the repo as markdown files.
- Documents reflect the current static prototype rather than an unrelated generic product.
- Documents distinguish current demo capability from future production requirements.
- Existing application files and unrelated uncommitted changes remain untouched.

