from __future__ import annotations

from dataclasses import dataclass
from typing import Any

DEFAULT_SCORE_THRESHOLD = 6.0
TARGET_AVAILABILITY_IMPACT = "LOW"


@dataclass(frozen=True)
class Variant14Rule:
    score_threshold: float = DEFAULT_SCORE_THRESHOLD
    availability_impact: str = TARGET_AVAILABILITY_IMPACT


def _extract_english_description(descriptions: Any) -> str:
    if not isinstance(descriptions, list):
        return ""
    for item in descriptions:
        if isinstance(item, dict) and item.get("lang") == "en":
            value = item.get("value")
            if isinstance(value, str):
                return value.strip()
    for item in descriptions:
        if isinstance(item, dict) and isinstance(item.get("value"), str):
            return item["value"].strip()
    return ""


def _extract_cvss_v31(metrics: Any) -> tuple[float | None, str | None, str | None]:
    """Return (base_score, availability_impact, vector_string) from CVSS v3.1."""
    if not isinstance(metrics, dict):
        return None, None, None

    cvss_list = metrics.get("cvssMetricV31")
    if not isinstance(cvss_list, list) or not cvss_list:
        return None, None, None

    chosen: dict[str, Any] | None = None
    for entry in cvss_list:
        if isinstance(entry, dict) and entry.get("type") == "Primary":
            chosen = entry
            break
    if chosen is None:
        chosen = next((e for e in cvss_list if isinstance(e, dict)), None)
    if chosen is None:
        return None, None, None

    cvss_data = chosen.get("cvssData")
    if not isinstance(cvss_data, dict):
        return None, None, None

    raw_score = cvss_data.get("baseScore")
    if isinstance(raw_score, bool) or not isinstance(raw_score, (int, float)):
        score: float | None = None
    else:
        score = float(raw_score)

    raw_impact = cvss_data.get("availabilityImpact")
    impact = (
        raw_impact.strip().upper()
        if isinstance(raw_impact, str) and raw_impact.strip()
        else None
    )

    raw_vector = cvss_data.get("vectorString")
    vector = (
        raw_vector.strip()
        if isinstance(raw_vector, str) and raw_vector.strip()
        else None
    )

    return score, impact, vector


def analyze_cves(
    payload: dict[str, Any],
    rule: Variant14Rule | None = None,
) -> dict[str, Any]:
    """Filter CVEs matching Variant 14: baseScore >= 6.0 and availabilityImpact == LOW."""
    active_rule = rule or Variant14Rule()
    expected_impact = active_rule.availability_impact.strip().upper()

    vulnerabilities = payload.get("vulnerabilities")
    if not isinstance(vulnerabilities, list):
        vulnerabilities = []

    matched: list[dict[str, Any]] = []
    skipped_missing_cvss = 0

    for item in vulnerabilities:
        if not isinstance(item, dict):
            continue
        cve_obj = item.get("cve")
        if not isinstance(cve_obj, dict):
            continue

        cve_id = cve_obj.get("id")
        if not isinstance(cve_id, str) or not cve_id.strip():
            continue

        base_score, avail_impact, vector = _extract_cvss_v31(cve_obj.get("metrics"))
        if base_score is None or avail_impact is None:
            skipped_missing_cvss += 1
            continue

        if (
            base_score >= active_rule.score_threshold
            and avail_impact == expected_impact
        ):
            matched.append(
                {
                    "cve_id": cve_id.strip(),
                    "published": cve_obj.get("published"),
                    "base_score": base_score,
                    "availability_impact": avail_impact,
                    "vector_string": vector,
                    "description": _extract_english_description(
                        cve_obj.get("descriptions")
                    ),
                }
            )

    matched.sort(key=lambda entry: (-entry["base_score"], entry["cve_id"]))

    return {
        "variant": 14,
        "rule": {
            "cvss_version": "3.1",
            "min_base_score": active_rule.score_threshold,
            "availability_impact": expected_impact,
        },
        "total_vulnerabilities": len(vulnerabilities),
        "skipped_missing_cvss_v31": skipped_missing_cvss,
        "matched_count": len(matched),
        "matches": matched,
    }
