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
    data = json.loads(result.stdout)

    assert isinstance(data, dict)

    v1 = data.get("Variant 1")
    assert v1 is not None
    assert "posts" in v1
    assert isinstance(v1["posts"], list)


def test_cli_max_chars_respected():
    """Test that no post exceeds max_chars."""
    max_chars = 50
    result = run_cli([str(SAMPLE_BLOG), "--variant", "1", "--max-chars", str(max_chars), "--json"])
    assert result.returncode == 0
    data = json.loads(result.stdout)
    posts = data["Variant 1"]["posts"]

    for post in posts:
        assert post["char_count"] <= max_chars

def extract_posts(data, variant="Variant 1"):
    if "posts" in data:
        return data["posts"]
    return data[variant]["posts"]
