
import math
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

    def probe_ids(self) -> tuple[str, ...]:
        if not self.samples:
            return ()
        return tuple(
            expression.probe_id
            for expression in self.samples[0].expression
    )

    def has_consistent_probes(self) -> bool:
        expected = self.probe_ids()

        return all(
            tuple(expression.probe_id for expression in sample.expression) == expected
            for sample in self.samples
        )

    def has_valid_values(self) -> bool:
        return all(
            math.isfinite(expression.value)
            for sample in self.samples
            for expression in sample.expression
        )