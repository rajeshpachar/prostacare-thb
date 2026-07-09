# ProstaCare Field Dictionary (from workbook V2)

Every UI field mapped to its control, data type, requiredness, and allowed values. Field keys match the canonical schema exactly. Source: `ProstaCare_Schema_08072026_V2.xlsx` · `Field_Dictionary`.


## Demographics_Entry

| Section | Field Key | Label | Control | Type | UI Req | Allowed Options / List | Notes |
|---|---|---|---|---|---|---|---|
| Registry Linkage | `patient_code` | Unique Patient Code | text | text | No |  | Only patient-level identifier permitted in this workbook. Reuse the same code across all sheets. |
| Registry Linkage | `registry_enrolment_date` | Registry Enrolment Date | date | date | No | yyyy-mm-dd | Needed for monthly registration trends on the home and population dashboards. |
| De-identified Demographics | `age_at_diagnosis_years` | Age at Diagnosis (years) | number | whole number | No | Years | Enter numeric age at diagnosis. Do not capture date of birth. |
| De-identified Demographics | `language_preference` | Language Preference | dropdown | categorical | No | Hindi  /  English  /  Tamil  /  Telugu  /  Bengali  /  Marathi  /  Kannada  /  Malayalam  /  Gujarati  /  Punjabi  /  Odia |  |
| Coverage & Access | `healthcare_coverage` | Healthcare Coverage | dropdown | categorical | Yes | PMJAY (Ayushman Bharat)  /  CGHS  /  ESIC  /  State Scheme (Rajya Bima / Aarogyasri)  /  Private Insurance  /  Self-pay |  |
| Coverage & Access | `referring_hospital_centre` | Referring Hospital / Centre | dropdown | categorical | No | AIIMS New Delhi  /  Tata Memorial Centre, Mumbai  /  CMC Vellore  /  PGIMER Chandigarh  /  RGCI Delhi  /  SGPGI Lucknow  /  Government General Hospital  /  Private Urologist / Clinic |  |
| Coverage & Access | `referral_source` | Referral Source | dropdown | categorical | No | Government Hospital / OPD  /  Private Urologist  /  CGHS Panel Hospital  /  District Cancer Centre  /  Self-referral  /  Other | Normalized for dashboard referral-source donut. |
| Geography & Access | `state` | State | dropdown | categorical | No | Delhi  /  Maharashtra  /  Tamil Nadu  /  Uttar Pradesh  /  Karnataka  /  West Bengal  /  Rajasthan  /  Punjab  /  Gujarat  /  Telangana  /  Andhra Pradesh  /  Madhya Pradesh  /  Bihar  /  Other |  |
| Geography & Access | `travel_distance_km` | Travel Distance to Centre (km) | number | decimal number | No | Kilometres | Used for travel-distance chart buckets. |

## Clinical_Entry

| Section | Field Key | Label | Control | Type | UI Req | Allowed Options / List | Notes |
|---|---|---|---|---|---|---|---|
| Workbook Linkage | `patient_code` | Unique Patient Code | text | text | No |  | Match the Demographics_Entry unique patient code. |
| Presenting Complaint | `diagnosis_date` | Date of Diagnosis | date | date | No | yyyy-mm-dd | Needed for age-at-diagnosis and time-to-treatment analytics. |
| Presenting Complaint | `primary_complaint` | Primary Complaint | dropdown | categorical | No | LUTS (Lower urinary tract symptoms)  /  Haematuria  /  Bone pain / backache  /  Incidental PSA elevation  /  Asymptomatic screening  /  Urinary retention |  |
| Presenting Complaint | `duration` | Duration | text | text | No |  |  |
| Presenting Complaint | `ipss_score` | IPSS Score | dropdown | categorical | No | 0–7 (Mild)  /  8–19 (Moderate)  /  20–35 (Severe) |  |
| Presenting Complaint | `bowel_rectal_symptoms` | Bowel / Rectal Symptoms | dropdown | categorical | No | None  /  Constipation  /  Blood in stool  /  Tenesmus |  |
| Digital Rectal Examination (DRE) | `dre_findings` | DRE Findings | single-select chip group | categorical | Yes | Normal  /  Enlarged (BPH)  /  Nodule – unilateral  /  Nodule – bilateral  /  Induration / fixity  /  Seminal vesicle ext. |  |
| Digital Rectal Examination (DRE) | `prostate_volume_cc` | Prostate Volume (TRUS / MRI cc) | text | decimal number | No | cc | Workbook expects numeric cc value. |
| Biopsy Details | `biopsy_date` | Biopsy Date | date | date | No | yyyy-mm-dd |  |
| Biopsy Details | `biopsy_type` | Biopsy Type | dropdown | categorical | No | 12-core TRUS biopsy  /  MRI-targeted / Fusion biopsy  /  Cognitive targeted  /  Transperineal biopsy  /  TURP chips |  |
| Biopsy Details | `pi_rads_score` | PI-RADS Score (mpMRI) | dropdown | categorical | No | PI-RADS 1  /  PI-RADS 2  /  PI-RADS 3  /  PI-RADS 4  /  PI-RADS 5  /  Not done |  |
| Biopsy Details | `gleason_score` | Gleason Score | dropdown | categorical | No | 3+3=6  /  3+4=7  /  4+3=7  /  4+4=8  /  4+5=9  /  5+4=9  /  5+5=10 | gs |
| Biopsy Details | `isup_grade_group` | ISUP Grade Group | dropdown | categorical | No | Grade 1 (3+3)  /  Grade 2 (3+4)  /  Grade 3 (4+3)  /  Grade 4 (4+4)  /  Grade 5 (≥4+5) |  |
| Biopsy Details | `cores_positive_total` | Cores Positive / Total | text | text | No |  | UI stores as free text, e.g. 10 / 12. |
| Biopsy Details | `core_involvement_pct` | % Core Involvement | text | decimal number | No | % | Workbook expects percent as whole number, e.g. 83. |
| Biopsy Details | `perineural_invasion` | Perineural Invasion | dropdown | categorical | No | Not assessed  /  Absent  /  Present |  |
| Biopsy Details | `ece_extracapsular_extension` | ECE (Extracapsular Extension) | dropdown | categorical | No | Not assessed  /  Absent  /  Present (radiological) |  |
| TNM Staging & Risk Classification | `clinical_t_stage` | Clinical T Stage | dropdown | categorical | Yes | cT1a  /  cT1b  /  cT1c  /  cT2a  /  cT2b  /  cT2c  /  cT3a  /  cT3b  /  cT4 |  |
| TNM Staging & Risk Classification | `n_stage` | N Stage | dropdown | categorical | No | cN0  /  cN1  /  cNX |  |
| TNM Staging & Risk Classification | `m_stage` | M Stage | dropdown | categorical | No | cM0  /  M1a (Non-regional LN)  /  M1b (Bone mets)  /  M1c (Visceral mets) |  |
| TNM Staging & Risk Classification | `eau_risk_category` | EAU Risk Category | dropdown | categorical | No | Low  /  Intermediate – Favourable  /  Intermediate – Unfavourable  /  High  /  Very High / Locally Advanced  /  M1 – Metastatic HSPC | risk-s |
| TNM Staging & Risk Classification | `ecog_performance_status` | ECOG Performance Status | dropdown | categorical | No | 0 – Fully active  /  1 – Restricted strenuous activity  /  2 – Ambulatory, self-care only  /  3 – Limited self-care  /  4 – Completely disabled |  |
| TNM Staging & Risk Classification | `castration_status` | Castration Status | dropdown | categorical | No | Hormone-sensitive (HSPC)  /  Castration-resistant (CRPC)  /  Not on ADT | cast-s |
| Imaging & Molecular Workup | `mpmri_pelvis` | mpMRI Pelvis | dropdown | categorical | No | Not done  /  Done — abnormal  /  Done — normal |  |
| Imaging & Molecular Workup | `bone_scan_spect` | Bone Scan / SPECT | dropdown | categorical | No | Not done  /  Done — no metastases  /  Done — bone metastases present | bone-s |
| Imaging & Molecular Workup | `psma_pet_ct` | PSMA PET-CT | dropdown | categorical | No | Not done  /  Done — no uptake  /  Done — pelvic nodal uptake  /  Done — distant metastases | psma-s |
| Imaging & Molecular Workup | `ct_abdomen_pelvis` | CT Abdomen / Pelvis | dropdown | categorical | No | Not done  /  Done — lymphadenopathy  /  Done — normal |  |
| Imaging & Molecular Workup | `dexa_bone_density` | DEXA Bone Density | dropdown | categorical | No | Not done  /  Normal (T-score ≥ −1)  /  Osteopenia (T −1 to −2.5)  /  Osteoporosis (T-score < −2.5) | dexa-s |
| Imaging & Molecular Workup | `germline_somatic_testing` | Germline / Somatic Testing | dropdown | categorical | No | Not done  /  BRCA1/2 — pathogenic variant  /  BRCA1/2 — negative  /  MSI-H / dMMR  /  HRR mutation (non-BRCA)  /  Pending | gen-s |
| Comorbidities & Family History | `comorbidity_1` | Active Comorbidity: Type 2 Diabetes | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `comorbidity_2` | Active Comorbidity: Hypertension | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `comorbidity_3` | Active Comorbidity: CAD / IHD | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `comorbidity_4` | Active Comorbidity: CKD (Stage) | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `comorbidity_5` | Active Comorbidity: COPD | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `comorbidity_6` | Active Comorbidity: Stroke / TIA | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `comorbidity_7` | Active Comorbidity: Anaemia | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `comorbidity_8` | Active Comorbidity: Osteoporosis | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `comorbidity_9` | Active Comorbidity: None significant | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `family_history_1` | Family History: Prostate Ca (first-degree) | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `family_history_2` | Family History: Breast Ca (family) | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `family_history_3` | Family History: Ovarian cancer | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `family_history_4` | Family History: Colon cancer | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `family_history_5` | Family History: Pancreatic cancer | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |
| Comorbidities & Family History | `family_history_6` | Family History: None known | multi-select chip group | categorical | No |  /  Yes  /  No | Original UI is a multi-select chip group. |

## Treatment_Entry

| Section | Field Key | Label | Control | Type | UI Req | Allowed Options / List | Notes |
|---|---|---|---|---|---|---|---|
| Workbook Linkage | `patient_code` | Unique Patient Code | text | text | No |  | Match the Demographics_Entry unique patient code. |
| Treatment Intent & MDT | `treatment_intent` | Treatment Intent | single-select chip group | categorical | No | Curative  /  Disease control (locally advanced)  /  Palliative / Symptomatic  /  Active surveillance  /  Watchful waiting |  |
| Treatment Intent & MDT | `mdt_tumour_board_status` | MDT / Tumour Board Status | dropdown | categorical | No | Pending review  /  Reviewed — plan agreed  /  Not applicable |  |
| Treatment Intent & MDT | `date_of_mdt_review` | Date of MDT Review | date | date | No | yyyy-mm-dd |  |
| Treatment Intent & MDT | `clinical_trial_eligibility` | Clinical Trial Eligibility | dropdown | categorical | No | Not screened  /  Eligible — under screening  /  Enrolled in trial  /  Not eligible |  |
| Treatment Intent & MDT | `treatment_start_date` | Treatment Start Date | date | date | No | yyyy-mm-dd | Use the first actual active treatment date for time-to-treatment analytics. |
| Androgen Deprivation Therapy (ADT) | `adt_type` | ADT Type | dropdown | categorical | No | Not on ADT  /  LHRH Agonist (Leuprolide / Lupride)  /  LHRH Agonist (Triptorelin / Decapeptyl)  /  LHRH Agonist (Goserelin / Zoladex)  /  GnRH Antagonist (Degarelix / Firmagon)  /  Bilateral orchidectomy |  |
| Androgen Deprivation Therapy (ADT) | `formulation_dose` | Formulation / Dose | dropdown | categorical | No | Leuprolide 11.25 mg (monthly)  /  Leuprolide 22.5 mg depot (3-monthly)  /  Leuprolide 45 mg depot (6-monthly)  /  Goserelin 3.6 mg (monthly)  /  Goserelin 10.8 mg (3-monthly) |  |
| Androgen Deprivation Therapy (ADT) | `adt_start_date` | ADT Start Date | date | date | No | yyyy-mm-dd |  |
| Androgen Deprivation Therapy (ADT) | `anti_androgen` | Anti-androgen | dropdown | categorical | No | None  /  Bicalutamide 50 mg OD (flare cover)  /  Bicalutamide 150 mg OD  /  Enzalutamide 160 mg OD  /  Apalutamide 240 mg OD  /  Darolutamide 1200 mg/day | aa-s |
| Androgen Deprivation Therapy (ADT) | `arsi_intensification` | ARSI Intensification | dropdown | categorical | No | Not initiated  /  Abiraterone + Prednisone (Zytiga / generic)  /  Enzalutamide (Xtandi)  /  Apalutamide (Erleada)  /  Darolutamide (Nubeqa) | arsi-s |
| Androgen Deprivation Therapy (ADT) | `testosterone_level` | Testosterone Level | text | text | No | ng/dL | UI placeholder: Castrate: <50 ng/dL. |
| Chemotherapy | `chemotherapy_regimen` | Chemotherapy Regimen | dropdown | categorical | No | Not indicated / Not started  /  Docetaxel 75 mg/m² q3w  /  Cabazitaxel 25 mg/m² q3w  /  Docetaxel → Cabazitaxel (sequential) |  |
| Chemotherapy | `number_of_cycles_completed` | Number of Cycles Completed | number | whole number | No | 0 to 20 |  |
| Chemotherapy | `last_cycle_date` | Last Cycle Date | date | date | No | yyyy-mm-dd |  |
| Radiotherapy Plan | `rt_indication` | RT Indication | dropdown | categorical | No | Not planned  /  Definitive RT (prostate ± LN)  /  Planned — awaiting CGHS approval  /  Salvage RT (post-RP)  /  Palliative RT (bone mets) |  |
| Radiotherapy Plan | `rt_status` | RT Status | dropdown | categorical | No | Not started  /  Planned  /  Active / Ongoing  /  Completed  /  Deferred / Cancelled | Used to distinguish planned, active, and completed RT on the treatment dashboard. |
| Radiotherapy Plan | `rt_modality` | RT Modality | dropdown | categorical | No | IMRT / VMAT  /  3D-CRT  /  SBRT (5 fractions)  /  LDR Brachytherapy  /  HDR Brachytherapy boost  /  Proton therapy |  |
| Radiotherapy Plan | `target_volume` | Target Volume | dropdown | categorical | No | Prostate only  /  Prostate + Whole Pelvis  /  Prostate + SV + LN |  |
| Radiotherapy Plan | `dose_fractionation` | Dose / Fractionation | dropdown | categorical | No | 60 Gy / 20 fx (moderate hypofractionation)  /  78 Gy / 39 fx (conventional)  /  36.25 Gy / 5 fx (SBRT)  /  Other / to be defined |  |
| Radiotherapy Plan | `rt_facility` | RT Facility | dropdown | categorical | No | AIIMS New Delhi  /  Tata Memorial Centre  /  RGCI Delhi  /  Max Cancer Centre  /  Fortis  /  Govt. Regional Cancer Centre |  |
| Radiotherapy Plan | `planned_rt_start_date` | Planned RT Start Date | date | date | No | yyyy-mm-dd |  |
| Radiotherapy Plan | `rt_completion_date` | RT Completion Date | date | date | No | yyyy-mm-dd |  |
| Radiotherapy Plan | `cghs_preauth_status` | CGHS Pre-auth Status | dropdown | categorical | No | Not required  /  Not initiated  /  Pending  /  Approved  /  Rejected | Tracks pending approvals behind the treatment dashboard access views. |
| Radiotherapy Plan | `cghs_request_date` | CGHS Request Date | date | date | No | yyyy-mm-dd |  |
| Radiotherapy Plan | `cghs_approval_date` | CGHS Approval Date | date | date | No | yyyy-mm-dd |  |
| Bone Health & Supportive Care | `bone_protection_therapy` | Bone Protection Therapy | dropdown | categorical | Yes | Not started  /  Zoledronic acid 4 mg IV q3m  /  Denosumab 120 mg SC q4w  /  Denosumab 60 mg SC q6m (osteoporosis)  /  Not indicated | bp-s |
| Bone Health & Supportive Care | `calcium_vitamin_d` | Calcium & Vitamin D | dropdown | categorical | No | Not prescribed  /  Calcium 500 mg + Vit D3 1000 IU OD  /  Calcium 1000 mg + Vit D3 OD |  |
| Bone Health & Supportive Care | `next_follow_up_psa_date` | Next Follow-up PSA Date | date | date | No | yyyy-mm-dd | fup-d |
| Bone Health & Supportive Care | `testosterone_monitoring` | Testosterone Monitoring | dropdown | categorical | No | Not checked this cycle  /  Castrate confirmed (<50 ng/dL)  /  Non-castrate — action needed |  |
| Bone Health & Supportive Care | `psychosocial_screening_phq9` | Psychosocial Screening (PHQ-9) | dropdown | categorical | No | Not done  /  Minimal (0–4)  /  Mild (5–9)  /  Moderate (10–14)  /  Severe (≥15) — refer |  |
| Bone Health & Supportive Care | `nutritional_assessment` | Nutritional Assessment | dropdown | categorical | No | Not done  /  Normal  /  At risk — dietitian referral made  /  Malnourished |  |
| Safety & Tolerability | `safety_side_effects` | Safety / Side Effects Observed | text | text | No |  | Capture active toxicity, intolerance, or clinically relevant side effects affecting the treatment pathway. |

## Outcomes_Entry

| Section | Field Key | Label | Control | Type | UI Req | Allowed Options / List | Notes |
|---|---|---|---|---|---|---|---|
| Workbook Linkage | `patient_code` | Unique Patient Code | text | text | No |  | Match the Demographics_Entry unique patient code. |
| Follow-up Status | `last_follow_up_date` | Last Follow-up Date | date | date | No | yyyy-mm-dd |  |
| Follow-up Status | `best_response` | Best Response | dropdown | categorical | No | Not yet assessable  /  PSA response  /  Stable disease  /  Biochemical recurrence  /  Radiological progression  /  Clinical progression |  |
| PSA Outcome Markers | `psa_nadir_value` | PSA Nadir Value | number | decimal number | No | ng/mL |  |
| PSA Outcome Markers | `psa_nadir_date` | PSA Nadir Date | date | date | No | yyyy-mm-dd |  |
| PSA Outcome Markers | `psa_doubling_time_months` | PSA Doubling Time | number | decimal number | No | Months |  |
| Disease Status | `biochemical_recurrence_status` | Biochemical Recurrence Status | dropdown | categorical | No | Not assessed  /  No recurrence documented  /  Biochemical recurrence |  |
| Disease Status | `biochemical_recurrence_date` | Biochemical Recurrence Date | date | date | No | yyyy-mm-dd |  |
| Disease Status | `crpc_progression_status` | CRPC Progression Status | dropdown | categorical | No | No CRPC progression documented  /  Progressed to CRPC  /  Suspected progression - workup pending |  |
| Disease Status | `crpc_progression_date` | CRPC Progression Date | date | date | No | yyyy-mm-dd |  |
| Disease Status | `rt_outcome_status` | RT Outcome Status | dropdown | categorical | No | Not yet assessed  /  Complete biochemical response  /  Partial biochemical response  /  Stable disease  /  Biochemical recurrence  /  Progressive disease |  |

## PSA_History

| Section | Field Key | Label | Control | Type | UI Req | Allowed Options / List | Notes |
|---|---|---|---|---|---|---|---|
| PSA History & Trend | `patient_code` | Unique Patient Code | text | text | No |  |  |
| PSA History & Trend | `psa_date` | Date | date | date | No | yyyy-mm-dd |  |
| PSA History & Trend | `psa_ng_ml` | PSA (ng/mL) | number | decimal number | No | ng/mL |  |
| PSA History & Trend | `free_psa_pct` | Free PSA % | number | decimal number | No | Whole-number percent, e.g. 12 |  |
| PSA History & Trend | `psa_density` | PSA Density | text | decimal number | No |  |  |
| PSA History & Trend | `context_remarks` | Context / Remarks | text | text | No |  |  |

## Journey_Events

| Section | Field Key | Label | Control | Type | UI Req | Allowed Options / List | Notes |
|---|---|---|---|---|---|---|---|
| Patient Journey | `patient_code` | Unique Patient Code | text | text | No |  |  |
| Add New Journey Event | `event_type` | Event Type | dropdown | categorical | No | Outpatient Visit  /  Lab / PSA  /  Imaging  /  Biopsy / Procedure  /  Treatment Initiation  /  Treatment Change  /  Hospital Admission  /  MDT Review  /  Adverse Event  /  Palliative Referral |  |
| Add New Journey Event | `event_date` | Event Date | date | date | No | yyyy-mm-dd |  |
| Add New Journey Event | `event_notes` | Notes | text | text | No |  | UI placeholder: Brief description. |

## Field_Dictionary only

| Section | Field Key | Label | Control | Type | UI Req | Allowed Options / List | Notes |
|---|---|---|---|---|---|---|---|
| Rx Uploads | `rx_upload` | Prescription / Rx Upload | file upload (multiple) | file | No |  | rx-upload-input  /  Workflow attachment control for PDF/image uploads; excluded from row-based Excel entry sheets. |


# Value Lists (dropdown option sets)

| List | Options (in order) |
|---|---|
| `yesNo` | Yes · No |
| `languagePreference` | Hindi · English · Tamil · Telugu · Bengali · Marathi · Kannada · Malayalam · Gujarati · Punjabi · Odia |
| `healthcareCoverage` | PMJAY (Ayushman Bharat) · CGHS · ESIC · State Scheme (Rajya Bima / Aarogyasri) · Private Insurance · Self-pay |
| `referringHospitalCentre` | AIIMS New Delhi · Tata Memorial Centre, Mumbai · CMC Vellore · PGIMER Chandigarh · RGCI Delhi · SGPGI Lucknow · Government General Hospital · Private Urologist / Clinic |
| `referralSource` | Government Hospital / OPD · Private Urologist · CGHS Panel Hospital · District Cancer Centre · Self-referral · Other |
| `state` | Delhi · Maharashtra · Tamil Nadu · Uttar Pradesh · Karnataka · West Bengal · Rajasthan · Punjab · Gujarat · Telangana · Andhra Pradesh · Madhya Pradesh · Bihar · Other |
| `primaryComplaint` | LUTS (Lower urinary tract symptoms) · Haematuria · Bone pain / backache · Incidental PSA elevation · Asymptomatic screening · Urinary retention |
| `ipssScore` | 0–7 (Mild) · 8–19 (Moderate) · 20–35 (Severe) |
| `bowelRectalSymptoms` | None · Constipation · Blood in stool · Tenesmus |
| `dreFindings` | Normal · Enlarged (BPH) · Nodule – unilateral · Nodule – bilateral · Induration / fixity · Seminal vesicle ext. |
| `biopsyType` | 12-core TRUS biopsy · MRI-targeted / Fusion biopsy · Cognitive targeted · Transperineal biopsy · TURP chips |
| `piRadsScore` | PI-RADS 1 · PI-RADS 2 · PI-RADS 3 · PI-RADS 4 · PI-RADS 5 · Not done |
| `gleasonScore` | 3+3=6 · 3+4=7 · 4+3=7 · 4+4=8 · 4+5=9 · 5+4=9 · 5+5=10 |
| `isupGradeGroup` | Grade 1 (3+3) · Grade 2 (3+4) · Grade 3 (4+3) · Grade 4 (4+4) · Grade 5 (≥4+5) |
| `perineuralInvasion` | Not assessed · Absent · Present |
| `ece` | Not assessed · Absent · Present (radiological) |
| `clinicalTStage` | cT1a · cT1b · cT1c · cT2a · cT2b · cT2c · cT3a · cT3b · cT4 |
| `nStage` | cN0 · cN1 · cNX |
| `mStage` | cM0 · M1a (Non-regional LN) · M1b (Bone mets) · M1c (Visceral mets) |
| `eauRiskCategory` | Low · Intermediate – Favourable · Intermediate – Unfavourable · High · Very High / Locally Advanced · M1 – Metastatic HSPC |
| `ecogPerformanceStatus` | 0 – Fully active · 1 – Restricted strenuous activity · 2 – Ambulatory, self-care only · 3 – Limited self-care · 4 – Completely disabled |
| `castrationStatus` | Hormone-sensitive (HSPC) · Castration-resistant (CRPC) · Not on ADT |
| `mpmriPelvis` | Not done · Done — abnormal · Done — normal |
| `boneScanSpect` | Not done · Done — no metastases · Done — bone metastases present |
| `psmaPetCt` | Not done · Done — no uptake · Done — pelvic nodal uptake · Done — distant metastases |
| `ctAbdomenPelvis` | Not done · Done — lymphadenopathy · Done — normal |
| `dexaBoneDensity` | Not done · Normal (T-score ≥ −1) · Osteopenia (T −1 to −2.5) · Osteoporosis (T-score < −2.5) |
| `germlineSomaticTesting` | Not done · BRCA1/2 — pathogenic variant · BRCA1/2 — negative · MSI-H / dMMR · HRR mutation (non-BRCA) · Pending |
| `treatmentIntent` | Curative · Disease control (locally advanced) · Palliative / Symptomatic · Active surveillance · Watchful waiting |
| `mdtStatus` | Pending review · Reviewed — plan agreed · Not applicable |
| `clinicalTrialEligibility` | Not screened · Eligible — under screening · Enrolled in trial · Not eligible |
| `adtType` | Not on ADT · LHRH Agonist (Leuprolide / Lupride) · LHRH Agonist (Triptorelin / Decapeptyl) · LHRH Agonist (Goserelin / Zoladex) · GnRH Antagonist (Degarelix / Firmagon) · Bilateral orchidectomy |
| `formulationDose` | Leuprolide 11.25 mg (monthly) · Leuprolide 22.5 mg depot (3-monthly) · Leuprolide 45 mg depot (6-monthly) · Goserelin 3.6 mg (monthly) · Goserelin 10.8 mg (3-monthly) |
| `antiAndrogen` | None · Bicalutamide 50 mg OD (flare cover) · Bicalutamide 150 mg OD · Enzalutamide 160 mg OD · Apalutamide 240 mg OD · Darolutamide 1200 mg/day |
| `arsiIntensification` | Not initiated · Abiraterone + Prednisone (Zytiga / generic) · Enzalutamide (Xtandi) · Apalutamide (Erleada) · Darolutamide (Nubeqa) |
| `chemotherapyRegimen` | Not indicated / Not started · Docetaxel 75 mg/m² q3w · Cabazitaxel 25 mg/m² q3w · Docetaxel → Cabazitaxel (sequential) |
| `rtIndication` | Not planned · Definitive RT (prostate ± LN) · Planned — awaiting CGHS approval · Salvage RT (post-RP) · Palliative RT (bone mets) |
| `rtModality` | IMRT / VMAT · 3D-CRT · SBRT (5 fractions) · LDR Brachytherapy · HDR Brachytherapy boost · Proton therapy |
| `rtStatus` | Not started · Planned · Active / Ongoing · Completed · Deferred / Cancelled |
| `targetVolume` | Prostate only · Prostate + Whole Pelvis · Prostate + SV + LN |
| `doseFractionation` | 60 Gy / 20 fx (moderate hypofractionation) · 78 Gy / 39 fx (conventional) · 36.25 Gy / 5 fx (SBRT) · Other / to be defined |
| `rtFacility` | AIIMS New Delhi · Tata Memorial Centre · RGCI Delhi · Max Cancer Centre · Fortis · Govt. Regional Cancer Centre |
| `cghsPreauthStatus` | Not required · Not initiated · Pending · Approved · Rejected |
| `boneProtectionTherapy` | Not started · Zoledronic acid 4 mg IV q3m · Denosumab 120 mg SC q4w · Denosumab 60 mg SC q6m (osteoporosis) · Not indicated |
| `calciumVitaminD` | Not prescribed · Calcium 500 mg + Vit D3 1000 IU OD · Calcium 1000 mg + Vit D3 OD |
| `testosteroneMonitoring` | Not checked this cycle · Castrate confirmed (<50 ng/dL) · Non-castrate — action needed |
| `psychosocialScreening` | Not done · Minimal (0–4) · Mild (5–9) · Moderate (10–14) · Severe (≥15) — refer |
| `nutritionalAssessment` | Not done · Normal · At risk — dietitian referral made · Malnourished |
| `bestResponse` | Not yet assessable · PSA response · Stable disease · Biochemical recurrence · Radiological progression · Clinical progression |
| `biochemicalRecurrenceStatus` | Not assessed · No recurrence documented · Biochemical recurrence |
| `crpcProgressionStatus` | No CRPC progression documented · Progressed to CRPC · Suspected progression - workup pending |
| `rtOutcomeStatus` | Not yet assessed · Complete biochemical response · Partial biochemical response · Stable disease · Biochemical recurrence · Progressive disease |
| `eventType` | Outpatient Visit · Lab / PSA · Imaging · Biopsy / Procedure · Treatment Initiation · Treatment Change · Hospital Admission · MDT Review · Adverse Event · Palliative Referral |
