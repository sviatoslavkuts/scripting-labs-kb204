from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
import requests

from labs.lab04.api_client import NvdApiError, fetch_cves_from_api, load_cves_from_file


def test_load_cves_from_file_success(tmp_path, sample_nvd_payload):
    file_path = tmp_path / "cves.json"
    file_path.write_text(json.dumps(sample_nvd_payload), encoding="utf-8")

    loaded = load_cves_from_file(file_path)
    assert len(loaded["vulnerabilities"]) == 6


def test_load_cves_from_file_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_cves_from_file(tmp_path / "does_not_exist.json")


def test_load_cves_from_file_invalid_json(tmp_path):
    bad_file = tmp_path / "broken.json"
    bad_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(NvdApiError):
        load_cves_from_file(bad_file)


def test_fetch_cves_from_api_success(sample_nvd_payload):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = sample_nvd_payload

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    result = fetch_cves_from_api(
        url="https://example.test/cves",
        params={"resultsPerPage": 10},
        timeout=5.0,
        session=mock_session,
    )

    assert result == sample_nvd_payload
    mock_session.get.assert_called_once_with(
        "https://example.test/cves",
        params={"resultsPerPage": 10},
        timeout=5.0,
    )


def test_fetch_cves_from_api_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("503 Server Error")

    mock_session = MagicMock()
    mock_session.get.return_value = mock_response

    with pytest.raises(NvdApiError):
        fetch_cves_from_api(url="https://example.test/cves", session=mock_session)
