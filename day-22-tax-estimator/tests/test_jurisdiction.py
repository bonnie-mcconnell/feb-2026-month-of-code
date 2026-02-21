from pathlib import Path
from decimal import Decimal
import pytest

from tax_engine.domain.jurisdiction import Jurisdiction


CONFIG_PATH = Path("tax_engine/config/jurisdictions/nz_self_employed.json")


def test_load_nz_jurisdiction():
    j = Jurisdiction.load_from_file(CONFIG_PATH)

    assert j.name == "NZ_SELF_EMPLOYED"
    assert j.currency == "NZD"
    assert j.scale == 2
    assert j.rounding == "ROUND_HALF_UP"
    assert j.self_employment_rate is None
    assert j.tax_schedule is not None


def test_missing_required_key():
    data = {
        "name": "BAD",
        "currency": "NZD"
    }

    with pytest.raises(ValueError):
        Jurisdiction._from_dict(data)  # intentional internal test


def test_reject_float_in_config():
    bad = {
        "name": "BAD",
        "currency": "NZD",
        "scale": 2,
        "rounding": "ROUND_HALF_UP",
        "round_per_bracket": False,
        "tax_brackets": [
            {"min": 0, "max": 10000, "rate": 0.1}
        ]
    }

    # inject float explicitly
    bad["tax_brackets"][0]["rate"] = 0.1

    with pytest.raises(TypeError):
        Jurisdiction._from_dict(bad)


def test_invalid_rate_rejected():
    bad = {
        "name": "BAD",
        "currency": "NZD",
        "scale": 2,
        "rounding": "ROUND_HALF_UP",
        "round_per_bracket": False,
        "tax_brackets": [
            {"min": 0, "max": None, "rate": 1.5}
        ]
    }

    with pytest.raises(ValueError):
        Jurisdiction._from_dict(bad)


def test_jurisdiction_deterministic():
    j1 = Jurisdiction.load_from_file(CONFIG_PATH)
    j2 = Jurisdiction.load_from_file(CONFIG_PATH)

    assert j1.tax_schedule.compute_tax == j2.tax_schedule.compute_tax