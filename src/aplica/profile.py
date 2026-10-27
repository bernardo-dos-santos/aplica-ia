"""Schema e carregamento do perfil do candidato (`perfil.yaml`).

O perfil é a única fonte de verdade sobre o candidato: o filtro fixo usa as
preferências, e a IA só pode citar o que estiver aqui.
"""

from enum import StrEnum
from pathlib import Path
from typing import Annotated, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, StringConstraints, model_validator

YearMonth = Annotated[str, StringConstraints(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]
"""Data no formato `AAAA-MM`. Strings comparam corretamente nesse formato."""


class WorkMode(StrEnum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"


class Shift(StrEnum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    FLEXIBLE = "flexible"


class JobType(StrEnum):
    INTERNSHIP = "internship"
    TRAINEE = "trainee"
    JUNIOR = "junior"


class _Model(BaseModel):
    # extra="forbid" faz um erro de digitação no YAML falhar em vez de ser ignorado.
    model_config = ConfigDict(extra="forbid", frozen=True)


class Links(_Model):
    github: HttpUrl | None = None
    linkedin: HttpUrl | None = None
    portfolio: HttpUrl | None = None


class Education(_Model):
    institution: str
    course: str
    start: YearMonth
    expected_end: YearMonth
    current_term: int | None = Field(default=None, ge=1)


class Experience(_Model):
    organization: str
    role: str
    start: YearMonth
    end: YearMonth | None = None
    highlights: list[str] = []
    skills: list[str] = []

    @model_validator(mode="after")
    def _end_after_start(self) -> Self:
        if self.end is not None and self.end < self.start:
            raise ValueError("end must not be before start")
        return self


class Preferences(_Model):
    job_types: list[JobType] = Field(min_length=1)
    areas: list[str] = Field(min_length=1)
    work_modes: list[WorkMode] = Field(min_length=1)
    shifts: list[Shift] = Field(min_length=1)
    onsite_cities: list[str] = []
    salary_expectation: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _onsite_needs_cities(self) -> Self:
        needs_city = WorkMode.ONSITE in self.work_modes or WorkMode.HYBRID in self.work_modes
        if needs_city and not self.onsite_cities:
            raise ValueError("onsite_cities is required when accepting onsite or hybrid work")
        return self


class Profile(_Model):
    name: str
    email: str
    phone: str | None = None
    city: str
    state: str = Field(min_length=2, max_length=2)
    links: Links = Links()
    summary: str | None = None
    education: list[Education] = Field(min_length=1)
    experience: list[Experience] = []
    skills: list[str] = []
    languages: list[str] = []
    preferences: Preferences


def load_profile(path: Path) -> Profile:
    """Lê e valida o perfil. Levanta `pydantic.ValidationError` se for inválido."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Profile.model_validate(data)
