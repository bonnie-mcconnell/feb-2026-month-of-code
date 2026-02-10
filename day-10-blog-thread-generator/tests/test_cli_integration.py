import json
import subprocess
import sys
from pathlib import Path


SRC_DIR = Path(__file__).parent.parent / "src"
CLI_PATH = SRC_DIR / "cli.py"
SAMPLE_BLOG = Path(__file__).parent.parent / "examples/sample_blog.md"

def run_cli(args):
    cmd = [sys.executable, "-m", "src.cli"] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result


def test_cli_text_output():
    """Test default text output of variant 1."""
    result = run_cli([str(SAMPLE_BLOG), "--variant", "1"])
    assert result.returncode == 0
    output = result.stdout
    assert "Thread (1 posts" in output or "Thread (" in output
    assert len(output) > 0


def test_cli_json_output():
    """Test JSON output of variants 1 and 2."""
    result = run_cli([str(SAMPLE_BLOG), "--variant", "1,2", "--json"])
    assert result.returncode == 0
    output = result.stdout
    data = json.loads(output.splitlines()[0] if output.startswith("{") else output)
    # JSON must have 'posts' array
    assert isinstance(data, dict) or isinstance(data, list)
    # Minimal structure checks
    if isinstance(data, dict):
        assert "posts" in data
        assert len(data["posts"]) > 0
        assert all("text" in p for p in data["posts"])


def test_cli_max_chars_respected():
    """Test that no post exceeds max_chars."""
    max_chars = 50
    result = run_cli([str(SAMPLE_BLOG), "--variant", "1", "--max-chars", str(max_chars), "--json"])
    assert result.returncode == 0
    data = json.loads(result.stdout.splitlines()[0])
    for post in data["posts"]:
        assert len(post["text"]) <= max_chars
