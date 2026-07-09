#!/usr/bin/env python3
"""Regenerate docs/FIELD_DICTIONARY.md from the ProstaCare V2 workbook.
Skips silently if the workbook or openpyxl is unavailable (the committed
FIELD_DICTIONARY.md is then reused as-is). Override path with WORKBOOK env var."""
import os, sys, pathlib
from collections import OrderedDict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WB = os.environ.get("WORKBOOK", os.path.expanduser("~/Downloads/ProstaCare_Schema_08072026_V2.xlsx"))

if not pathlib.Path(WB).exists():
    print(f"  ! workbook not found ({WB}) — keeping existing FIELD_DICTIONARY.md")
    sys.exit(0)
try:
    import openpyxl
except ImportError:
    print("  ! openpyxl not installed — keeping existing FIELD_DICTIONARY.md")
    sys.exit(0)

wb = openpyxl.load_workbook(WB, data_only=True)

def rows(ws):
    return [[("" if c is None else str(c).strip()) for c in r] for r in ws.iter_rows(values_only=True)]

def cell(r, i):
    return r[i] if i < len(r) else ""

fd = rows(wb["Field_Dictionary"])
hdr = next(i for i, r in enumerate(fd) if "Field Key" in r)
data = [r for r in fd[hdr+1:] if any(r)]
groups = OrderedDict()
for r in data:
    groups.setdefault(cell(r, 0), []).append(r)

out = ["# ProstaCare Field Dictionary (from workbook V2)\n",
       "Every UI field mapped to its control, data type, requiredness, and allowed values. "
       "Field keys match the canonical schema exactly. Source: `ProstaCare_Schema_08072026_V2.xlsx` · `Field_Dictionary`.\n"]
for sheet, rs in groups.items():
    out.append(f"\n## {sheet}\n")
    out.append("| Section | Field Key | Label | Control | Type | UI Req | Allowed Options / List | Notes |")
    out.append("|---|---|---|---|---|---|---|---|")
    for r in rs:
        opts = cell(r, 9).replace("|", " / ")
        notes = cell(r, 10).replace("|", " / ")
        out.append(f"| {cell(r,1)} | `{cell(r,2)}` | {cell(r,3)} | {cell(r,4)} | {cell(r,6)} | {cell(r,7)} | {opts} | {notes} |")

vl = rows(wb["Value_Lists"])
vh = next(i for i, r in enumerate(vl) if "Option Value" in r or "List Name" in r)
lists = OrderedDict()
for r in [x for x in vl[vh+1:] if any(x)]:
    name, val = cell(r, 0), cell(r, 2)
    if name:
        lists.setdefault(name, []).append(val)
out.append("\n\n# Value Lists (dropdown option sets)\n")
out.append("| List | Options (in order) |")
out.append("|---|---|")
for name, vals in lists.items():
    out.append(f"| `{name}` | " + " · ".join(v for v in vals if v) + " |")

(ROOT / "docs" / "FIELD_DICTIONARY.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"WROTE docs/FIELD_DICTIONARY.md ; {len(groups)} sheets, {len(lists)} value lists, {len(data)} fields")
