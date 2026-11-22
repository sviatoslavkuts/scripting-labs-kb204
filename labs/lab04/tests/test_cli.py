from __future__ import annotations

import json

from labs.lab04.main import run_cli


def test_cli_input_and_output_file(tmp_path, sample_nvd_payload):
    input_file = tmp_path / "input.json"
    output_file = tmp_path / "report.json"
    input_file.write_text(json.dumps(sample_nvd_payload), encoding="utf-8")

    exit_code = run_cli(["--input", str(input_file), "--output", str(output_file)])
    assert exit_code == 0
    assert output_file.is_file()

    report = json.loads(output_file.read_text(encoding="utf-8"))
    assert report["variant"] == 14
    assert report["matched_count"] == 2


def test_cli_missing_input_returns_error(tmp_path, capsys):
    missing = tmp_path / "missing.json"
    exit_code = run_cli(["--input", str(missing)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Error:" in captured.err
