# ProstaCare — Clinical Pathway vs Our Data Model: Gap Analysis

> **Who this is for:** clinical, business and legal teams. **No technical background needed.**
> Terms are explained in the glossary at the top of `PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md` §0.

**What this is:** the prostate-cancer MDT care pathway (NCCN/EAU, adapted for India) names exactly what a registry must capture. We checked our data model against it, panel by panel. **We found 11 gaps** — one of which reverses an earlier simplification decision.

---

## 1. Registration gap — confirmed ❌

The demo patient file captured **Religion · Marital Status · Occupation · Education**. The V2 workbook (`Demographics_Entry`) captures **none of them** — verified: 0 of 108 fields.

The pathway's first registry capture point is **"Patient demographics & risk factors."** So these are not optional nice-to-haves; they are the demographic base of the registry.

**Proposed additions to `patient` (Registration screen):**

| Field key | Label | Type | Suggested options |
|---|---|---|---|
| `religion` | Religion | dropdown | Hindu · Muslim · Christian · Sikh · Buddhist · Jain · Other · Prefer not to say |
| `marital_status` | Marital Status | dropdown | Married · Unmarried · Widowed · Divorced / Separated |
| `education_level` | Education | dropdown | No formal education · Primary · Secondary · Higher secondary · Graduate · Post-graduate |
| `occupation` | Occupation | dropdown | Agriculture · Labour · Service / Salaried · Business / Self-employed · Retired · Unemployed · Other |
| `tobacco_use` *(risk factor)* | Tobacco Use | dropdown | Never · Former · Current |
| `family_history_prostate` | already exists (`family_history_1`) | — | — |

> ❓ **Clinical question:** the pathway says *"demographics **& risk factors**"*. Beyond family history, which risk factors do you want — tobacco, BMI, ethnicity? *(Our proposal: tobacco only, for v1.)*

---

## 2. Pathway → model gap matrix

| # | The pathway requires | We capture today | Verdict |
|---|---|---|---|
| **G-a** | Patient demographics **& risk factors** | age, coverage, geography, language, referral | ❌ **Gap** — religion, marital, education, occupation, tobacco (§1) |
| **G-b** | **Labs: CBC, RFT, LFT, ALP, Testosterone** (serial, and 6-weekly on Pluvicto) | PSA only (`psa_reading`); testosterone as a single text box | ❌ **Gap** — no general lab record. **Proposal:** generalise to a `lab_result` record (test name · value · unit · date), with PSA as one test type. |
| **G-c** | **Surgery** (radical prostatectomy) as a treatment option | `treatment_line` types = ADT · anti-androgen · ARSI · chemo · RT. Orchidectomy sits oddly inside `adt_type`. `rt_indication` even offers *"Salvage RT (post-RP)"* — implying a prostatectomy we never recorded | ❌ **Gap** — add `line_type = surgery` (radical prostatectomy, orchidectomy, TURP) |
| **G-d** | **Radioligand therapy — Pluvicto (Lu-177 PSMA)**: cycles, dose, adverse events. Also **Radium-223** | Nothing | ❌ **Major gap** — an entire treatment modality, and an explicit registry capture point |
| **G-e** | **Adverse events & toxicity** (structured) | one free-text box (`safety_side_effects`) | ❌ **Gap** — free text cannot be counted or reported. **Proposal:** `adverse_event` record (term · CTCAE grade 1–5 · onset date · action taken · related line) |
| **G-f** | **Outcomes: PFS, OS, QoL, bone events** | BCR, CRPC progression, PSA nadir, PSADT, RT outcome | ❌ **Major gap** — **no vital status / date of death**, so **Overall Survival cannot be computed at all**. No QoL instrument. No skeletal-related events. |
| **G-g** | **Resource utilisation** (hospitalisations, ER visits) | `journey_event` has a *Hospital Admission* type | ⚠️ **Partial** — countable only if entered consistently; no ER-visit type |
| **G-h** | **Follow-up schedule by disease state** (curative q3–6m → mHSPC q3m → mCRPC q1–3m → Pluvicto q6w → survivors annual) | a single `next_follow_up_psa_date` | ❌ **Gap** — and it **reverses a simplification** (see §4) |
| **G-i** | **Response assessment (PSA *and* imaging)** | PSA response + `best_response` | ⚠️ **Partial** — no imaging-response record (PCWG3/RECIST) |
| **G-j** | **Support services**: nursing, dietician, physiotherapy, psychology, social work, **genetic counselling** | PHQ-9 + nutritional assessment | ⚠️ **Partial** — no referral record for physio / social work / genetic counselling |
| **G-k** | **Key investigations**: PSA, DRE, mpMRI, fusion biopsy, histopath, PSMA PET, CT C/A/P, bone scan, germline (BRCA1/2, **ATM**) | all present except **CT *chest*** and the ATM gene | ✅ **Near-complete** — minor: `ct_abdomen_pelvis` should read *CT Chest/Abdomen/Pelvis*; germline list should include ATM |

**Naming note:** the pathway says **ARPI** (Androgen Receptor Pathway Inhibitor); our schema says **ARSI**. Same class of drug — we should adopt one term. *(Recommend ARPI, matching the pathway.)*

---

## 3. Proposed model additions

| New / changed | Shape | Why |
|---|---|---|
| `patient` + 5 fields | religion, marital status, education, occupation, tobacco | §1 |
| **`lab_result`** (new, dated, many) | `test_name` (PSA · CBC · RFT · LFT · ALP · Testosterone) · `value` · `unit` · `date` | G-b. **`psa_reading` becomes a view over this**, so the PSA chart is unaffected |
| `treatment_line.line_type` + values | `surgery` · `radioligand` (Pluvicto Lu-177, Radium-223) | G-c, G-d |
| `treatment_line` + fields | `cycles_completed`, `dose`, for radioligand & chemo | G-d |
| **`adverse_event`** (new, dated, many) | `term` · `ctcae_grade` · `onset_date` · `action_taken` · `related_line` | G-e |
| `outcome` + fields | **`vital_status`** (Alive / Died) · **`date_of_death`** · `cause_of_death` · `progression_free_date` | G-f — **required for Overall Survival & PFS** |
| **`bone_event`** (new, dated) | skeletal-related event: fracture · cord compression · bone RT · bone surgery | G-f |
| **`qol_assessment`** (new, dated) | instrument (EQ-5D / FACT-P) · score · date | G-f |
| **`healthcare_contact`** (new, dated) | type: hospitalisation · ER visit · day-care · length of stay | G-g |
| **`follow_up_plan`** | protocol interval derived from disease state (see §4) | G-h |
| `imaging_study` + `response` field | PCWG3 / RECIST response at that study | G-i |
| **`referral`** (new, dated) | service: dietician · physiotherapy · psychology · social work · genetic counselling · palliative | G-j |
| `ct_abdomen_pelvis` → relabel | *CT Chest / Abdomen / Pelvis* | G-k |
| `germlineSomaticTesting` + option | `ATM mutation` | G-k |

---

## 4. ⚠️ This reverses one of our simplifications (T9)

We previously cut the nightly scheduled check, arguing **"all 8 rules are state-based, not time-based — they only change when someone saves."** That was true of the 8 rules **as written**.

The pathway introduces a rule that **is** time-based:

```
Follow-up interval by disease state:
   After curative treatment → PSA every 3–6 months for 2 years, then 6–12 monthly
   mHSPC                    → every 3 months
   mCRPC                    → every 1–3 months
   On Pluvicto              → every 6 weeks (CBC, RFT, LFT, PSA)
   Long-term survivors      → annual review (comorbidities, bone health, QoL)

Rule:  IF today > last_follow_up_date + protocol_interval(disease_state)
       THEN raise "Follow-up overdue" nudge
```
This gap opens **because time passes**, not because anyone saved a record. So **a scheduled (nightly) check is required after all.**

✅ **Correction to `SIMPLIFICATION_REVIEW.md` T9:** keep the on-save check for the 8 state-based rules, **and add a nightly check** for follow-up-interval adherence. This also unlocks the "Missed / Overdue" patient-list segment properly.

---

## 5. A governance note (factual)

The pathway's registry capture points explicitly include **"Pluvicto therapy details (cycles, dose, AEs)"**. Pluvicto (Lu-177 PSMA-617) is a **Novartis** product. This corroborates the sponsor inference in `DEV_START_GATE.md` **B7**, and sharpens the point already raised there:

> If the sponsor's own therapy is a named registry capture point, the **independent clinical governance of the care-gap rules** (who may add or amend a rule, and their independence from the sponsor) must be settled **before** build. Capturing the data is entirely legitimate; the control that matters is **who decides what the system nudges clinicians to do.**

---

## 6. Questions for the clinical team

1. **Registration (§1):** confirm religion / marital status / education / occupation, and which **risk factors** beyond family history (tobacco? BMI? ethnicity?).
2. **Labs (G-b):** confirm the panel to capture serially — CBC, RFT, LFT, ALP, Testosterone. Any others (Hb, PSMA SUV)?
3. **Outcomes (G-f):** confirm we capture **vital status + date of death** (without it there is no Overall Survival). Which **QoL instrument** — EQ-5D or FACT-P? Which **bone events**?
4. **Adverse events (G-e):** structured CTCAE grading, or free text as today?
5. **Radioligand (G-d):** confirm Pluvicto + Radium-223 capture (cycles, dose, AEs) is in v1 scope.
6. **Surgery (G-c):** confirm radical prostatectomy is recorded as a treatment line.
7. **Follow-up (G-h/§4):** confirm the protocol intervals above, so the "overdue" nudge can be built.
8. **Terminology:** adopt **ARPI** (pathway) in place of ARSI?
9. **Support services (G-j):** capture referrals to dietician / physio / psychology / social work / genetic counselling?

---

*Source: the prostate-cancer MDT care pathway (NCCN/EAU, adapted for India) supplied by the client; checked against `ProstaCare_Schema_08072026_V2.xlsx` and our canonical model.*
