from dataclasses import dataclass

import numpy as np

from longevity_atlas.geo.models import GEODataset


@dataclass(frozen=True)
class ExpressionMatrix:
    sample_accessions: tuple[str, ...] # "GSM123456"
    probe_ids: tuple[str, ...] # "probe1", "probe2", ...
    values: np.ndarray # 2D array of shape (num_samples, num_probes)

    @property
    def sample_count(self) -> int:
        return self.values.shape[0] # rows

    @property
    def feature_count(self) -> int:
        return self.values.shape[1] # columns


def dataset_to_matrix(dataset: GEODataset) -> ExpressionMatrix:
    if not dataset.samples:
        return ExpressionMatrix(
            sample_accessions=(),
            probe_ids=(),
            values=np.empty((0, 0)),
        )

    if not dataset.has_consistent_probes():
        raise ValueError("Dataset contains inconsistent probe IDs")

    if not dataset.has_valid_values():
        raise ValueError("Dataset contains invalid expression values")

    probe_ids = dataset.probe_ids()

    values = np.array(
        [
            [expression.value for expression in sample.expression]
            for sample in dataset.samples
        ],
        dtype=float,
    )

    sample_accessions = tuple(
        sample.accession
        for sample in dataset.samples
    )

    return ExpressionMatrix(
        sample_accessions=sample_accessions,
        probe_ids=probe_ids,
        values=values,
    )