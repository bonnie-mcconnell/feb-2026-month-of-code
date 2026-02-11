from src.uptime_monitor.cli import main
import sys


def test_cli_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["monitor"])
    try:
        main()
    except SystemExit:
        pass

    captured = capsys.readouterr()
    assert "usage" in captured.out.lower()
