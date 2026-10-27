from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from aplica.profile import Shift, WorkMode, load_profile

EXAMPLE = Path(__file__).parents[1] / "perfil.example.yaml"


def _write(tmp_path: Path, data: dict[str, Any]) -> Path:
    path = tmp_path / "perfil.yaml"
    path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
    return path


@pytest.fixture
def example_data() -> dict[str, Any]:
    data: dict[str, Any] = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
    return data


def test_example_profile_is_valid() -> None:
    profile = load_profile(EXAMPLE)

    assert profile.preferences.shifts == [Shift.AFTERNOON]
    assert WorkMode.REMOTE in profile.preferences.work_modes
    assert profile.experience[0].end is None


def test_unknown_key_is_rejected(tmp_path: Path, example_data: dict[str, Any]) -> None:
    example_data["skils"] = ["typo"]

    with pytest.raises(ValidationError, match="skils"):
        load_profile(_write(tmp_path, example_data))


def test_onsite_without_cities_is_rejected(tmp_path: Path, example_data: dict[str, Any]) -> None:
    example_data["preferences"]["onsite_cities"] = []

    with pytest.raises(ValidationError, match="onsite_cities"):
        load_profile(_write(tmp_path, example_data))


def test_remote_only_does_not_need_cities(tmp_path: Path, example_data: dict[str, Any]) -> None:
    example_data["preferences"]["work_modes"] = ["remote"]
    example_data["preferences"]["onsite_cities"] = []

    assert load_profile(_write(tmp_path, example_data)).preferences.onsite_cities == []


def test_experience_ending_before_start_is_rejected(
    tmp_path: Path, example_data: dict[str, Any]
) -> None:
    example_data["experience"][0]["end"] = "2026-01"

    with pytest.raises(ValidationError, match="end must not be before start"):
        load_profile(_write(tmp_path, example_data))


@pytest.mark.parametrize("bad_date", ["2026-13", "2026/06", "06-2026"])
def test_invalid_year_month_is_rejected(
    tmp_path: Path, example_data: dict[str, Any], bad_date: str
) -> None:
    example_data["experience"][0]["start"] = bad_date

    with pytest.raises(ValidationError):
        load_profile(_write(tmp_path, example_data))
