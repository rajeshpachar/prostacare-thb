# ProstaCare Product Requirements Document

## 1. Product Overview

ProstaCare India is a prostate cancer clinical analytics and patient management demo for oncology teams. The product brings together patient file review, care-gap nudges, MDT coordination, prescription attachment, and cohort-level analytics into a browser-based workflow.

The current repository is a static front-end prototype intended for stakeholder demos. It uses representative prostate cancer records and locally stored browser data to show the intended clinical workflow without requiring a production backend.

## 2. Problem Statement

Prostate cancer care often spans urology, radiation oncology, medical oncology, diagnostics, and payer workflows. Teams need a faster way to see which patients need action, which records are incomplete, where treatment pathways vary from guidelines, and which cohort-level gaps are affecting quality.

ProstaCare should help clinicians and program teams:

- Identify urgent patient-level care gaps.
- Track staging, PSA, biopsy, treatment, bone health, MDT, and follow-up status in one record.
- Coordinate action with the relevant MDT member or the full MDT.
- Review population trends across risk, treatment, outcomes, and quality metrics.
- Demonstrate how a future integrated registry could support prostate cancer care delivery in India.

## 3. Target Users

- Urologists reviewing prostate cancer intake, staging, and procedural history.
- Radiation oncologists planning RT, ADT duration, MDT review, and follow-up.
- Medical oncologists reviewing systemic therapy and ARSI intensification opportunities.
- MDT coordinators tracking tumour board status, missing documents, and follow-up actions.
- Clinical operations and quality teams reviewing cohort-level protocol adherence.
- Demo stakeholders evaluating the registry and analytics workflow.

## 4. Goals

- Provide a clear front door for daily prostate cancer clinic review.
- Make patient-level nudges visible and actionable.
- Show how guideline signals translate into operational gaps.
- Support quick movement from cohort metrics to affected patient records.
- Preserve a demo-safe experience with sample data and privacy controls.
- Keep the product deployable as static HTML for stakeholder review.

## 5. Non-Goals

- Replace clinician judgment or provide autonomous diagnosis or treatment decisions.
- Serve as a production electronic medical record.
- Store real patient data in the current static prototype.
- Integrate with hospital HIS, LIS, PACS, payer, ABHA, or email systems in this repository version.
- Provide regulatory-grade clinical decision support without validation, governance, and audit controls.

## 6. Current Product Surfaces

### 6.1 Login

The app includes a demo login screen for controlled presentation flow. It is not a production authentication system.

### 6.2 Home Dashboard

The home dashboard summarizes clinic and cohort activity, including open care gaps, record completeness, new registrations, benchmark comparisons, nudge trends, and attention-required patient lists.

### 6.3 Patient List

The patient list provides searchable and filterable access to sample patient files, with patient name visibility controls and status filters.

### 6.4 Patient File

The patient file shows demographics, clinical details, PSA history, staging, treatment plan, patient journey, nudges, guideline references, team discussion, Rx upload, and printable summary actions.

### 6.5 Team Discussion

The team discussion flow lets a user prepare a focused MDT notification, target a specific team member or all MDT members, preview the notification, and preserve a local audit-style log.

### 6.6 Rx Uploads

The Rx upload flow stores prescription or medication documents in browser storage for the active sample patient and supports open/remove actions.

### 6.7 Population Analytics

The population dashboard summarizes 347 representative patients across overview, clinical profile, treatment, outcomes, quality gaps, and demographics/geography. Chart drilldowns reveal affected patient rows.

## 7. Success Metrics

For the prototype:

- Stakeholders can understand the end-to-end workflow without facilitator explanation.
- Users can navigate from home metrics to patient records and back.
- Patient-level nudges are clear enough to explain the next operational action.
- Population analytics can support demo discussion of quality gaps and cohort trends.
- Static deployment works consistently in a browser.

For a future production product:

- Reduction in unreviewed high-risk patient records.
- Increase in complete staging, MDT documentation, bone health, and follow-up fields.
- Faster turnaround from identified gap to assigned action.
- Higher proportion of eligible patients reviewed for guideline-concordant treatment intensification.
- Reliable audit trail for communication and action closure.

## 8. Key Risks and Assumptions

- Current data is representative demo data, not validated real-world clinical evidence.
- Current persistence uses local browser storage and is not multi-user.
- Guideline content must be medically reviewed before production use.
- Production deployment would require security, consent, privacy, audit, interoperability, and clinical governance work.
- Any real notification, upload, or patient data workflow must be backed by a secure server-side architecture.

