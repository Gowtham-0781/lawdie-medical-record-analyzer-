from typing import Literal

from pydantic import BaseModel, Field


class SourceCitation(BaseModel):
    document_name: str
    page_number: int
    passage: str


class Injury(BaseModel):
    name: str
    body_part: str | None = None
    severity: str | None = None
    citations: list[SourceCitation] = Field(default_factory=list)


class Diagnosis(BaseModel):
    name: str
    diagnosis_code: str | None = None
    date: str | None = None
    provider: str | None = None
    citations: list[SourceCitation] = Field(default_factory=list)


class Provider(BaseModel):
    name: str
    specialty: str | None = None
    facility: str | None = None
    citations: list[SourceCitation] = Field(default_factory=list)


class TreatmentEvent(BaseModel):
    date: str | None = None
    provider: str | None = None
    treatment: str
    body_part: str | None = None
    outcome: str | None = None
    citations: list[SourceCitation] = Field(default_factory=list)


class PainAndSuffering(BaseModel):
    description: str
    category: Literal[
        "pain",
        "work",
        "sleep",
        "mobility",
        "hobby",
        "daily_activity",
        "emotional",
        "other",
    ] = "other"

    citations: list[SourceCitation] = Field(default_factory=list)


class Conflict(BaseModel):
    field: str
    description: str
    values: list[str] = Field(default_factory=list)
    citations: list[SourceCitation] = Field(default_factory=list)


class CaseFacts(BaseModel):
    patient_name: str | None = None
    incident_date: str | None = None

    injuries: list[Injury] = Field(default_factory=list)
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    providers: list[Provider] = Field(default_factory=list)
    treatments: list[TreatmentEvent] = Field(default_factory=list)
    pain_and_suffering: list[PainAndSuffering] = Field(default_factory=list)

    conflicts: list[Conflict] = Field(default_factory=list)


class DemandNarrative(BaseModel):
    narrative: str
    citations: list[SourceCitation] = Field(default_factory=list)


class CaseAnalysis(BaseModel):
    facts: CaseFacts
    demand_narrative: DemandNarrative | None = None