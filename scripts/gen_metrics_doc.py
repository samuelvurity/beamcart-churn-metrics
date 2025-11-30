#!/usr/bin/env python3
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
YML = ROOT / "docs" / "metrics.yaml"
OUT = ROOT / "docs" / "metrics_definitions.md"


def sec(title):
    return f"## {title}\n"


def render_metric(m):
    parts = []
    parts.append(f"### {m['name']}\n")
    kv = [
        ("Grain", m.get("grain", "")),
        ("Window", m.get("window", "")),
        ("Business intent", m.get("business_intent", "")),
        ("Definition", m.get("definition", "")),
        ("Inclusion/exclusion", m.get("inclusion_exclusion", "")),
        ("Formula", f"`{m.get('formula','')}`" if m.get("formula") else ""),
        ("SQL", m.get("sql_file", "(pandas)")),
        ("Segments", ", ".join(m.get("segments", [])) or "—"),
        ("Guardrails", ", ".join(m.get("guardrails", [])) or "—"),
        ("Edge cases", m.get("edge_cases", "—")),
    ]
    for k, v in kv:
        if v:
            parts.append(f"- **{k}:** {v}")
    parts.append("")  # blank line
    return "\n".join(parts)


def main():
    data = yaml.safe_load(YML.read_text())
    hdr = "# Metrics Definitions\n\n"
    hdr += f"- **Timezone:** {data.get('timezone','UTC')}\n"
    hdr += f"- **ISO week start:** {data.get('iso_week_start','Monday')}\n\n"
    if data.get("notes"):
        hdr += f"{data['notes'].rstrip()}\n\n"
    body = []
    for m in data["metrics"]:
        body.append(render_metric(m))
    OUT.write_text(hdr + "\n".join(body))
    print(f"✅ wrote {OUT}")


if __name__ == "__main__":
    main()
