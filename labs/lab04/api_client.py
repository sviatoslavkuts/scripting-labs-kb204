from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests

NVD_CVE_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


class NvdApiError(RuntimeError):
    """Raised when fetching or parsing NVD CVE data fails."""


def load_cves_from_file(file_path: str | Path) -> dict[str, Any]:
    """Load an NVD CVE 2.0 JSON payload from a local file."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input JSON file not found: {path}")

    try:
        raw_text = path.read_text(encoding="utf-8")
        data = json.loads(raw_text)
    except (OSError, json.JSONDecodeError) as exc:
        raise NvdApiError(f"Failed to read JSON from {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise NvdApiError("Expected top-level JSON object in NVD payload.")
    return data


def fetch_cves_from_api(
    *,
    url: str = NVD_CVE_API_URL,
    params: dict[str, Any] | None = None,
    timeout: float = 15.0,
    session: requests.Session | None = None,
) -> dict[str, Any]:
    """Fetch CVE records from NVD CVE API 2.0."""
    requester = session if session is not None else requests
    try:
        response = requester.get(url, params=params, timeout=timeout)
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        raise NvdApiError(f"NVD API request failed: {exc}") from exc
    except ValueError as exc:
        raise NvdApiError(f"Invalid JSON returned by NVD API: {exc}") from exc

    if not isinstance(payload, dict):
        raise NvdApiError("Expected top-level JSON object from NVD API.")
    return payload
