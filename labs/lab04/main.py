from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from labs.lab04.analysis import (
    DEFAULT_SCORE_THRESHOLD,
    TARGET_AVAILABILITY_IMPACT,
    Variant14Rule,
    analyze_cves,
)
from labs.lab04.api_client import NvdApiError, fetch_cves_from_api, load_cves_from_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze NVD CVE 2.0 records using CVSS v3.1 Variant 14 criteria."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to a local NVD JSON payload file (skips live API request when provided).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the JSON report (prints to stdout when omitted).",
    )
    parser.add_argument(
        "--results-per-page",
        type=int,
        default=20,
        help="Number of records to request from NVD API when --input is not used.",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="Optional keyword search query for NVD API.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP request timeout in seconds for NVD API.",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=DEFAULT_SCORE_THRESHOLD,
        help=f"Minimum CVSS v3.1 base score threshold (default: {DEFAULT_SCORE_THRESHOLD}).",
    )
    parser.add_argument(
        "--availability-impact",
        type=str,
        default=TARGET_AVAILABILITY_IMPACT,
        help=f"Target CVSS v3.1 availabilityImpact value (default: {TARGET_AVAILABILITY_IMPACT}).",
    )
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.input is not None:
            payload = load_cves_from_file(args.input)
        else:
            params: dict[str, Any] = {"resultsPerPage": args.results_per_page}
            if args.keyword:
                params["keywordSearch"] = args.keyword
            payload = fetch_cves_from_api(params=params, timeout=args.timeout)

        rule = Variant14Rule(
            score_threshold=args.min_score,
            availability_impact=args.availability_impact,
        )
        report = analyze_cves(payload, rule=rule)
    except (FileNotFoundError, NvdApiError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    serialized = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized + "\n", encoding="utf-8")
    else:
        print(serialized)

    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli())