from __future__ import annotations

from typing import Any

import pytest


def make_cve_item(
    cve_id: str,
    *,
    base_score: float | None = 7.5,
    availability_impact: str | None = "LOW",
    vector_string: str | None = "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L",
    description: str = "Sample vulnerability description.",
    published: str = "2025-01-15T10:00:00.000",
    metric_type: str = "Primary",
    include_cvss_v31: bool = True,
) -> dict[str, Any]:
    metrics: dict[str, Any] = {}
    if include_cvss_v31:
        cvss_data: dict[str, Any] = {}
        if base_score is not None:
            cvss_data["baseScore"] = base_score
        if availability_impact is not None:
            cvss_data["availabilityImpact"] = availability_impact
        if vector_string is not None:
            cvss_data["vectorString"] = vector_string
        metrics["cvssMetricV31"] = [
            {
                "type": metric_type,
                "cvssData": cvss_data,
            }
        ]

    return {
        "cve": {
            "id": cve_id,
            "published": published,
            "descriptions": [{"lang": "en", "value": description}],
            "metrics": metrics,
        }
    }


@pytest.fixture
def sample_nvd_payload() -> dict[str, Any]:
    return {
        "vulnerabilities": [
            make_cve_item("CVE-2025-0001", base_score=6.0, availability_impact="LOW"),
            make_cve_item("CVE-2025-0002", base_score=8.5, availability_impact="LOW"),
            make_cve_item("CVE-2025-0003", base_score=5.9, availability_impact="LOW"),
            make_cve_item("CVE-2025-0004", base_score=9.0, availability_impact="HIGH"),
            make_cve_item("CVE-2025-0005", base_score=7.2, availability_impact="NONE"),
            make_cve_item("CVE-2025-0006", include_cvss_v31=False),
        ]
    }
