from dataclasses import dataclass


@dataclass(frozen=True)
class GEOSample:
    accession: str
    title: str
    sample_type: str | None
    source_name: str | None
    organism: str | None
    sex: str | None
    age_years: float | None
    tissue: str | None