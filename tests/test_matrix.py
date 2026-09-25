import numpy as np
import pytest

from longevity_atlas.geo.matrix import ExpressionMatrix, dataset_to_matrix
from longevity_atlas.geo.models import GEODataset, GEOExpression, GEOSample


def make_dataset() -> GEODataset:
    samples = (
        GEOSample(
            accession="GSM1",
            title="Sample 1",
            sample_type="RNA",
            source_name="heart",
            organism="Homo sapiens",
            sex="male",
            age_years=20,
            tissue="left atrium",
            expression=(
                GEOExpression("probe1", 1.0),
                GEOExpression("probe2", 2.0),
                GEOExpression("probe3", 3.0),
            ),
        ),
        GEOSample(
            accession="GSM2",
            title="Sample 2",
            sample_type="RNA",
            source_name="heart",
            organism="Homo sapiens",
            sex="female",
            age_years=40,
            tissue="left atrium",
            expression=(
                GEOExpression("probe1", 4.0),
                GEOExpression("probe2", 5.0),
                GEOExpression("probe3", 6.0),
            ),
        ),
    )

    return GEODataset(
        series_accession="GSE_TEST",
        samples=samples,
    )


def test_dataset_to_matrix():
    dataset = make_dataset()

    matrix = dataset_to_matrix(dataset)

    assert isinstance(matrix, ExpressionMatrix)

    assert matrix.sample_accessions == ("GSM1", "GSM2")
    assert matrix.probe_ids == ("probe1", "probe2", "probe3")

    assert matrix.values.shape == (2, 3)

    np.testing.assert_array_equal(
        matrix.values,
        np.array(
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
            ]
        ),
    )


def test_empty_dataset():
    dataset = GEODataset(
        series_accession="GSE_EMPTY",
        samples=(),
    )

    matrix = dataset_to_matrix(dataset)

    assert matrix.sample_count == 0
    assert matrix.feature_count == 0
    assert matrix.values.shape == (0, 0)


def test_inconsistent_probes_raise():
    dataset = make_dataset()

    broken_sample = GEOSample(
        accession="GSM3",
        title="Sample 3",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="male",
        age_years=30,
        tissue="left atrium",
        expression=(
            GEOExpression("probe1", 7.0),
            GEOExpression("different_probe", 8.0),
            GEOExpression("probe3", 9.0),
        ),
    )

    broken_dataset = GEODataset(
        series_accession="GSE_TEST",
        samples=dataset.samples + (broken_sample,),
    )

    with pytest.raises(ValueError, match="inconsistent probe"):
        dataset_to_matrix(broken_dataset)


def test_sample_index():
    dataset = make_dataset()
    matrix = dataset_to_matrix(dataset)

    assert matrix.sample_index("GSM1") == 0
    assert matrix.sample_index("GSM2") == 1


def test_sample_index_unknown_sample():
    dataset = make_dataset()
    matrix = dataset_to_matrix(dataset)

    with pytest.raises(KeyError, match="Unknown sample accession"):
        matrix.sample_index("GSM999")