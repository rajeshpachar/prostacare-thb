# ProstaCare — Data Types, Enum Closure & Derived-Field Formulas

**Purpose (in plain terms):** two checks, so the clinical team can sign off with confidence.
1. **Is every question in the data-entry pack complete?** — does each field have a defined answer type, and does every dropdown have its full list of allowed answers? *(Yes — see §1–§2.)*
2. **Is every automatically-calculated number clearly defined?** — for each figure the system works out on your behalf, exactly how is it calculated? *(§3.)*

Checked automatically against the workbook `ProstaCare_Schema_08072026_V2.xlsx`, so this is verified, not assumed.

> **A note on wording:** an *"enum"* just means **a dropdown with a fixed list of allowed answers**. *"Derived"* means **the system calculates it — nobody types it.** *"Band"* means **a grouping range**, e.g. ages 65–69.

---

## 1. Every field has a defined answer type ✅

| Data type | Fields |
|---|---|
| `categorical` (enum) | 67 |
| `date` | 18 |
| `text` | 12 |
| `decimal number` | 8 |
| `whole number` | 2 |
| `file` | 1 |
| **Total** | **108** |

**Fields with no data type: 0.** Every field is typed.

**Platform mapping (NOVA Edge):** `categorical → enum(enumValues)` · `date → datetime` *(platform gotcha: never `date`)* · `decimal → number` · `whole → integer` · `text → string/text` · `file → file` + attachment entity.

---

## 2. Every dropdown has its complete list of answers ✅

| Check | Result |
|---|---|
| Categorical/dropdown fields with **no options** | **0** |
| Option sets that **don't match any Value_List** | **0** |
| Value_Lists defined but **never used** (orphans) | **0** |
| **Value lists matched** | **53 / 53** |

### 2.1 The exact words the care-gap rules depend on — all present ✅
The rules look for specific answers word-for-word (e.g. *"Not done"*). If one of those answers were spelled differently in the dropdown, **the rule would never fire and the gap would never be flagged** — a silent safety failure. We checked all of them:

| Enum list | Value the rules depend on | ✓ |
|---|---|---|
| `boneScanSpect` · `psmaPetCt` · `dexaBoneDensity` · `germlineSomaticTesting` · `psychosocialScreening` | `Not done` | ✅ |
| `boneProtectionTherapy` | `Not started` · `Not indicated` | ✅ |
| `arsiIntensification` | `Not initiated` | ✅ |
| `castrationStatus` | `Hormone-sensitive (HSPC)` · `Castration-resistant (CRPC)` · `Not on ADT` | ✅ |
| `eauRiskCategory` | `High` · `Very High / Locally Advanced` · `M1 – Metastatic HSPC` | ✅ |
| `mdtStatus` | `Not applicable` | ✅ |

### 2.2 ⚠ Two findings that need a decision

**F1 — Use explicit enum IN-lists, never substring matching.**
The demo evaluated risk with JavaScript `includes("High")`. That substring **also matches `Very High / Locally Advanced`** — which happens to be desired for rules 1/2, but is fragile and would silently break if an enum value changed. The production rules must use explicit sets:
```
risk_high_plus     = ('High', 'Very High / Locally Advanced', 'M1 – Metastatic HSPC')   -- rule 1
risk_high_veryhigh = ('High', 'Very High / Locally Advanced')                            -- rule 2
risk_arsi          = ('High', 'Very High / Locally Advanced')  -- rule 6: confirm if M1 included
```

**F2 — The risk enum has no `M1 – Metastatic CRPC`.**
Full list: `Low · Intermediate – Favourable · Intermediate – Unfavourable · High · Very High / Locally Advanced · M1 – Metastatic HSPC`.
A metastatic patient who progresses to castration-resistance keeps a risk label that reads **"HSPC"**, while `castration_status` correctly says CRPC.
❓ **Clinical decision:** add `M1 – Metastatic CRPC` to the risk enum, or treat `castration_status` as the sole source of truth for castration state? *(Recommendation: the latter — risk category is a staging construct; castration state is a separate axis. But confirm.)*

---

## 3. Every automatically-calculated figure, and how it is worked out

The workbook names **22** derived fields but only describes them in prose ("bucket into configured bands") — **the band edges were never defined**. Below: the explicit formula for each, with **proposed band edges recovered from the demo dashboard**, marked for clinical confirmation.

Notation: `current(M)` = latest dated row of model `M` for the patient (see functional spec §2).

### 3.1 Today's status — read from the most recent entry
*(these drive the patient header and feed the care-gap rules)*
| Derived | Formula |
|---|---|
| `current_risk` | `current(staging_assessment).eau_risk_category` |
| `current_castration` | `current(staging_assessment).castration_status` |
| `current_line` | `current(treatment_line WHERE status='Active')` |
| `current_bone_protection` | `current(supportive_care_event).bone_protection_therapy` |
| `latest_psa` | `current(psa_reading).psa_ng_ml` |
| `imaging_status(m)` | `current(imaging_study WHERE modality=m).result` **else `'Not done'`** *(absence = not done)* |

### 3.2 Figures calculated for one patient
| Derived | Formula | Notes |
|---|---|---|
| `adt_duration_months` | `DATEDIFF(month, treatment_line[ADT].start_date, COALESCE(end_date, today))` | |
| `time_to_treatment_days` | `treatment_plan.treatment_start_date − patient.diagnosis_date` | |
| `cghs_delay_days` | `COALESCE(cghs_approval_date, today) − cghs_request_date` | only when `cghs_preauth_status ≠ 'Not required'` |
| `time_to_nadir_months` | `DATEDIFF(month, treatment_start_date, outcome.psa_nadir_date)` | `'Not reached'` if nadir date null |
| `treatment_started_flag` | `treatment_plan.treatment_start_date IS NOT NULL` | |
| `rt_completed_flag` | `treatment_line[RT].rt_status = 'Completed' OR rt_completion_date IS NOT NULL` | |
| `visit_status` | `next_follow_up_psa_date > today → 'Upcoming'`; `< today → 'Missed/Overdue'`; else `'Last Visit'` (use `last_follow_up_date`) | why no Encounter entity is needed |
| `diagnostic_psa` | earliest `psa_reading` within the diagnosis window (or flagged diagnostic) | ⚠ needs a rule — see §4 |

### 3.3 Tidying answers into groups for reporting
| Derived | Formula |
|---|---|
| `risk_group` | identity map over `eau_risk_category` (6 values) — **no collapsing** |
| `ecog_band` | `'0 – Fully active'→0 · '1 – …'→1 · '2 – …'→2 · '3 – …'→3 · '4 – …'→4` |
| `stage_at_presentation` | bucket `(clinical_t_stage, n_stage, m_stage)` → `cT1–2 N0M0 · cT3a · cT3b · cT4 · N1 · M1a · M1b · M1c` |
| `comorbidity_mask` | one-hot over the 9 boolean flags; **pairs** = all 2-combinations present |
| `response_group` | `RT+ADT+ARSI` / `RT+ADT` / `ADT alone` / `Active surveillance` from `treatment_line` types present |
| `bone_gap_category` | `no bone Rx` / `no DEXA` / `no Ca+VitD` / `protected (on zoledronate/denosumab)` |
| `period_month` | `to_char(date, 'YYYY-MM')` — the only date granularity that leaves a tenant |

### 3.4 Grouping ranges ("bands") — **we propose these; please confirm**
The workbook says *"bucket into configured bands"* but never says what the ranges are. These are recovered from the demo dashboard:
| Derived bucket | Proposed bands (recovered from the demo) | Confirm |
|---|---|---|
| `age_band` | 40-44 · 45-49 · 50-54 · 55-59 · 60-64 · 65-69 · 70-74 · 75-79 · 80+ | ☐ |
| `psa_at_dx_band` | 0-4 · 4-10 · 10-20 · 20-50 · 50-100 · >100 ng/mL | ☐ |
| `psa_density_band` | <0.1 · 0.1-0.2 · 0.2-0.4 · 0.4-0.6 · 0.6-0.8 · >0.8 | ☐ |
| `free_psa_band` | <7% · 7-10% · 10-15% · 15-20% · >20% | ☐ |
| `adt_duration_band` | <3m · 3-6m · 6-12m · 12-24m · 24-48m · >48m | ☐ |
| `time_to_treatment_band` | <14d · 14-30d · 30-60d · 60-90d · >90d | ☐ |
| `cghs_delay_band` | <14d · 14-30d · 30-60d · 60-90d · 90-120d · >120d | ☐ |
| `nadir_time_band` | 1-2m · 2-3m · 3-4m · 4-6m · 6-9m · >9m · **Not reached** | ☐ |
| `psadt_band` | <3m · 3-6m · 6-12m · 12-24m · 24-48m · >48m | ☐ |
| `travel_distance_band` | <50km · 50-200km · 200-500km · 500-1000km · >1000km | ☐ |
| `psa_response_band` | PSA<0.2 · 0.2-1 · 1-4 · 4-10 · >10 ng/mL | ☐ |
| KM / response timepoints | Baseline · 1m · 3m · 6m · 9m · 12m · 18m · 24m *(KM: 0-48m by 6)* | ☐ |

> ⚠️ Two demo arrays were ambiguous (`nadir_time_band` vs `psadt_band`). The mapping above is our best reading — **please confirm which band set belongs to which metric.**

### 3.5 Department-level figures (across all patients)
| Derived | Formula |
|---|---|
| `open_gap_count` | `COUNT(nudge WHERE current_status='open') GROUP BY severity` |
| `gap_rate(type)` | `open nudges of rule_id / eligible denominator for that rule` |
| benchmark rates | `arsi_intensification_rate = ARSI-initiated ÷ (HSPC ∧ risk≥High)`; likewise `psma_completion_rate`, `bone_protection_rate` (÷ on-ADT), `mdt_review_rate` |
| `protocol_adherence_score` | weighted mean of the 10 protocol axes (MDT, staging, PSMA, RT dose, ADT duration, bone Rx, genetics, PSA monitoring, ARSI intensity, psych screen) |
| `completeness_score` | `present required fields ÷ total required fields`, **per field group** (groups = the `Field_Dictionary` sections) |
| `nudge_trend` | `COUNT(nudge_event) GROUP BY action('opened','acknowledged','resolved'), period_month` · `net_active = opened − resolved` (cumulative) |
| `km_bcr_free_survival` | Kaplan-Meier over `outcome.biochemical_recurrence_date − treatment_start_date`, stratified by `risk_group` |
| `registrations_per_month` | `COUNT(patient) GROUP BY period_month(registry_enrolment_date)` |

### 3.6 The only thing the sponsor ever receives
```
sponsor_metric(institution_code, period_month, metric_key, dim1, dim2,
               numerator, denominator, patient_n, suppressed)

suppressed = (patient_n < THRESHOLD)          -- default 11
IF suppressed THEN numerator = NULL, denominator = NULL
```

---

## 4. Five questions we need the clinical team to answer

| # | Item | Why |
|---|---|---|
| **F1** | Confirm the risk **IN-lists** per rule (esp. does rule 6 ARSI include `M1 – Metastatic HSPC`?) | prevents silent rule mis-fire |
| **F2** | Add `M1 – Metastatic CRPC` to the risk enum, or rely on `castration_status`? | a CRPC patient currently carries an "HSPC" risk label |
| **F3** | Confirm all **band edges** in §3.4 (and the `nadir_time_band` vs `psadt_band` mapping) | the workbook never defined them |
| **F4** | `diagnostic_psa` selection rule — *"earliest PSA within N days of `diagnosis_date`"*? What is N? Or add a `context_remarks` marker? | drives the PSA-at-diagnosis histogram + heatmap |
| **F5** | `completeness_score` — which fields count as **required** per group? (`Field_Dictionary` marks `UI Required` on only 4 fields) | otherwise completeness is arbitrary |

---

*Audited against `ProstaCare_Schema_08072026_V2.xlsx` (`Field_Dictionary`, `Value_Lists`, `Dashboard_Derived`). Companion: `PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md` §5, `FIELD_DICTIONARY.md`.*
