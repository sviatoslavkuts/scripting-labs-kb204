from __future__ import annotations

from labs.lab04.analysis import Variant14Rule, analyze_cves
from labs.lab04.tests.conftest import make_cve_item


def test_variant14_filters_score_threshold_and_availability_impact(sample_nvd_payload):
    report = analyze_cves(sample_nvd_payload)

    assert report["variant"] == 14
    assert report["rule"] == {
        "cvss_version": "3.1",
        "min_base_score": 6.0,
        "availability_impact": "LOW",
    }
    assert report["total_vulnerabilities"] == 6
    assert report["skipped_missing_cvss_v31"] == 1
    assert report["matched_count"] == 2
    # Sorted descending by baseScore: 8.5 then 6.0
    assert [m["cve_id"] for m in report["matches"]] == [
        "CVE-2025-0002",
        "CVE-2025-0001",
    ]


def test_custom_rule_parameters():
    payload = {
        "vulnerabilities": [
            make_cve_item("CVE-2025-1001", base_score=7.5, availability_impact="HIGH"),
            make_cve_item("CVE-2025-1002", base_score=6.5, availability_impact="HIGH"),
        ]
    }
    rule = Variant14Rule(score_threshold=7.0, availability_impact="high")
    report = analyze_cves(payload, rule=rule)

    assert report["matched_count"] == 1
    assert report["matches"][0]["cve_id"] == "CVE-2025-1001"


def test_handles_empty_or_malformed_payload():
    assert analyze_cves({})["matched_count"] == 0
    assert analyze_cves({"vulnerabilities": []})["total_vulnerabilities"] == 0
