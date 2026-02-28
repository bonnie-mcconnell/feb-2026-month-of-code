from pathlib import Path
from unittest.mock import patch, MagicMock

from observability_harness.ci.run_ci import main


@patch("observability_harness.ci.run_ci.subprocess.run")
@patch("observability_harness.ci.run_ci.enforce_coverage")
def test_run_ci_success(mock_enforce: MagicMock, mock_run: MagicMock) -> None:
    mock_run.return_value.returncode = 0

    main()

    mock_enforce.assert_called_once_with(90.0, Path("coverage.xml"))


@patch("observability_harness.ci.run_ci.subprocess.run")
def test_run_ci_failure(mock_run: MagicMock) -> None:
    mock_run.return_value.returncode = 1

    try:
        main()
    except SystemExit as exc:
        assert exc.code == 1