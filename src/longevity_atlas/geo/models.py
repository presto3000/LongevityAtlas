from dataclasses import dataclass


@dataclass(frozen=True)
class GEOExpression:
    probe_id: str
    value: float


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
    expression: tuple[GEOExpression, ...] = ()

@dataclass(frozen=True)
class GEOSeries:
    accession: str
    title: str
    sample_accessions: tuple[str, ...]

@dataclass(frozen=True)
class GEODataset:
    series_accession: str
    samples: tuple[GEOSample, ...]

    @property
    def sample_count(self) -> int:
        return len(self.samples)

    @property
    def feature_count(self) -> int:
        if not self.samples:
            return 0

        return len(self.samples[0].expression)