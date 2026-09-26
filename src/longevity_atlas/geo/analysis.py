from dataclasses import dataclass

import numpy as np

from longevity_atlas.geo.matrix import ExpressionMatrix
from longevity_atlas.geo.models import SampleMetadata


@dataclass(frozen=True)
class AnalysisDataset:
    matrix: ExpressionMatrix
    metadata: tuple[SampleMetadata, ...]

    def __post_init__(self) -> None:
        if self.matrix.sample_count != len(self.metadata):
            raise ValueError(
                "Matrix sample count does not match metadata count"
            )

        matrix_accessions = self.matrix.sample_accessions
        metadata_accessions = tuple(item.accession for item in self.metadata)

        if matrix_accessions != metadata_accessions:
            raise ValueError(
                "Matrix sample order does not match metadata order"
            )

    @property
    def sample_count(self) -> int:
        return self.matrix.sample_count

    @property
    def feature_count(self) -> int:
        return self.matrix.feature_count

    def ages(self) -> np.ndarray:
        if any(item.age_years is None for item in self.metadata):
            raise ValueError("Not all samples have age information")

        return np.array(
            [item.age_years for item in self.metadata],
            dtype=float,
        )

def build_analysis_dataset(matrix: ExpressionMatrix,  metadata: tuple[SampleMetadata, ...],
                           ) -> AnalysisDataset:
    return AnalysisDataset(matrix=matrix, metadata=metadata,  )