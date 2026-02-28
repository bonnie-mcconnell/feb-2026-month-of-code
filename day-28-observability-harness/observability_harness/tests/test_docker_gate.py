import pytest
from unittest.mock import patch
from ci.docker_gate import verify_docker_build


def test_docker_failure():
    with patch("subprocess.run") as mocked:
        mocked.return_value.returncode = 1
        with pytest.raises(SystemExit):
            verify_docker_build()