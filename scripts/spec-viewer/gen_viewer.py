#!/usr/bin/env python3
"""Bundle the ProstaCare spec docs into one self-contained HTML viewer.
Reads docs/*.md, renders client-side with marked + mermaid. Run from anywhere."""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent          # scripts/spec-viewer -> repo root
DOCS = ROOT / "docs"

ORDER = [
    ("▶ Dev-Start Gate (open questions)", "DEV_START_GATE.md"),
    ("👤 Patient Data Walkthrough", "PATIENT_JOURNEY_DATA_WALKTHROUGH.md"),
    ("🩺 Clinical Pathway Gaps", "CLINICAL_PATHWAY_GAP_ANALYSIS.md"),
    ("✂ Simplification Review", "SIMPLIFICATION_REVIEW.md"),
    ("Functional & Logic Spec", "PROSTACARE_FUNCTIONAL_LOGIC_SPEC.md"),
    ("NOVA Edge Alignment Review", "NOVAEDGE_ALIGNMENT_REVIEW.md"),
    ("Build Spec (v1)", "PROSTACARE_BUILD_SPEC_V1.md"),
    ("Cross-Tenant Aggregation", "CROSS_TENANT_AGGREGATION_SPEC.md"),
    ("Tenant Onboarding Plan", "TENANT_ONBOARDING_PLAN.md"),
    ("Field Dictionary", "FIELD_DICTIONARY.md"),
    ("Types · Enums · Derived", "DATA_TYPES_ENUMS_AND_DERIVED_FIELDS.md"),
    ("Flow Clarity & Open Questions", "FLOW-CLARITY-AND-OPEN-QUESTIONS.md"),
]

payload = []
for title, fn in ORDER:
    p = DOCS / fn
    if not p.exists():
        print(f"  ! skip missing {fn}")
        continue
    payload.append({"title": title, "file": fn, "md": p.read_text(encoding="utf-8")})

data_js = json.dumps(payload, ensure_ascii=False).replace("</script>", "<\\/script>")
template = (HERE / "viewer_template.html").read_text(encoding="utf-8")
out = DOCS / "prostacare-spec-viewer.html"
out.write_text(template.replace("__DATA__", data_js), encoding="utf-8")
print(f"WROTE {out.relative_to(ROOT)} ; {len(payload)} tabs")
