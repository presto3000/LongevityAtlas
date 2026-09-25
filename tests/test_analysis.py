import numpy as np
import pytest

from longevity_atlas.geo.analysis import (
    AnalysisDataset,
    build_analysis_dataset,
)
from longevity_atlas.geo.matrix import ExpressionMatrix
from longevity_atlas.geo.models import SampleMetadata


def make_analysis_dataset() -> AnalysisDataset:
    matrix = ExpressionMatrix(
        sample_accessions=("GSM1", "GSM2"),
        probe_ids=("probe1", "probe2"),
        values=np.array(
            [
                [1.0, 2.0],
                [3.0, 4.0],
            ]
        ),
    )

    metadata = (
        SampleMetadata(
            accession="GSM1",
            age_years=20,
            sex="male",
            tissue="heart",
            organism="Homo sapiens",
        ),
        SampleMetadata(
            accession="GSM2",
            age_years=40,
            sex="female",
            tissue="heart",
            organism="Homo sapiens",
        ),
    )

    return build_analysis_dataset(matrix, metadata)


def test_analysis_dataset():
    dataset = make_analysis_dataset()

    assert dataset.sample_count == 2
    assert dataset.feature_count == 2


def test_ages():
    dataset = make_analysis_dataset()

    np.testing.assert_array_equal(
        dataset.ages(),
        np.array([20.0, 40.0]),
    )


def test_metadata_count_must_match():
    matrix = ExpressionMatrix(
        sample_accessions=("GSM1", "GSM2"),
        probe_ids=("probe1",),
        values=np.array([[1.0], [2.0]]),
    )

    metadata = (
        SampleMetadata(
            accession="GSM1",
            age_years=20,
            sex="male",
            tissue="heart",
            organism="Homo sapiens",
        ),
    )

    with pytest.raises(
        ValueError,
        match="sample count does not match metadata count",
    ):
        AnalysisDataset(matrix=matrix, metadata=metadata)


def test_metadata_order_must_match():
    matrix = ExpressionMatrix(
        sample_accessions=("GSM1", "GSM2"),
        probe_ids=("probe1",),
        values=np.array([[1.0], [2.0]]),
    )

    metadata = (
        SampleMetadata(
            accession="GSM2",
            age_years=40,
            sex="female",
            tissue="heart",
            organism="Homo sapiens",
        ),
        SampleMetadata(
            accession="GSM1",
            age_years=20,
            sex="male",
            tissue="heart",
            organism="Homo sapiens",
        ),
    )

    with pytest.raises(
        ValueError,
        match="sample order does not match metadata order",
    ):
        AnalysisDataset(matrix=matrix, metadata=metadata)


def test_missing_age_raises():
    matrix = ExpressionMatrix(
        sample_accessions=("GSM1",),
        probe_ids=("probe1",),
        values=np.array([[1.0]]),
    )

    metadata = (
        SampleMetadata(
            accession="GSM1",
            age_years=None,
            sex="male",
            tissue="heart",
            organism="Homo sapiens",
        ),
    )

    dataset = AnalysisDataset(matrix=matrix, metadata=metadata)

    with pytest.raises(ValueError, match="age information"):
        dataset.ages()