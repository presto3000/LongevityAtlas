from longevity_atlas.geo.models import GEODataset, GEOExpression, GEOSample


def test_geo_dataset_counts():
    sample = GEOSample(
        accession="GSM1",
        title="Sample 1",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="male",
        age_years=50,
        tissue="left atrium",
    )

    dataset = GEODataset(
        series_accession="GSE96752",
        samples=(sample,),
    )

    assert dataset.sample_count == 1
    assert dataset.feature_count == 0

def test_geo_dataset_has_consistent_probes():
    sample_1 = GEOSample(
        accession="GSM1",
        title="Sample 1",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="male",
        age_years=50,
        tissue="left atrium",
        expression=(
            GEOExpression("probe1", 0.1),
            GEOExpression("probe2", 0.2),
        ),
    )

    sample_2 = GEOSample(
        accession="GSM2",
        title="Sample 2",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="female",
        age_years=60,
        tissue="left atrium",
        expression=(
            GEOExpression("probe1", 0.3),
            GEOExpression("probe2", 0.4),
        ),
    )

    dataset = GEODataset(
        series_accession="GSE96752",
        samples=(sample_1, sample_2),
    )

    assert dataset.probe_ids() == ("probe1", "probe2")
    assert dataset.has_consistent_probes() is True

def test_geo_dataset_detects_inconsistent_probes():
    sample_1 = GEOSample(
        accession="GSM1",
        title="Sample 1",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="male",
        age_years=50,
        tissue="left atrium",
        expression=(
            GEOExpression("probe1", 0.1),
            GEOExpression("probe2", 0.2),
        ),
    )

    sample_2 = GEOSample(
        accession="GSM2",
        title="Sample 2",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="female",
        age_years=60,
        tissue="left atrium",
        expression=(
            GEOExpression("probe1", 0.3),
            GEOExpression("probe3", 0.4),
        ),
    )

    dataset = GEODataset(
        series_accession="GSE96752",
        samples=(sample_1, sample_2),
    )

    assert dataset.has_consistent_probes() is False

def test_geo_dataset_has_valid_values():
    sample = GEOSample(
        accession="GSM1",
        title="Sample 1",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="male",
        age_years=50,
        tissue="left atrium",
        expression=(
            GEOExpression("probe1", 0.1),
            GEOExpression("probe2", -0.2),
        ),
    )
    dataset = GEODataset(
        series_accession="GSE96752",
        samples=(sample,),
    )
    assert dataset.has_valid_values() is True

def test_geo_dataset_detects_invalid_values():
    sample = GEOSample(
        accession="GSM1",
        title="Sample 1",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="male",
        age_years=50,
        tissue="left atrium",
        expression=(
            GEOExpression("probe1", float("nan")),
            GEOExpression("probe2", 0.2),
        ),
    )
    dataset = GEODataset(
        series_accession="GSE96752",
        samples=(sample,),
    )
    assert dataset.has_valid_values() is False

def test_sample_metadata():
    sample = GEOSample(
        accession="GSM1",
        title="Sample 1",
        sample_type="RNA",
        source_name="heart",
        organism="Homo sapiens",
        sex="male",
        age_years=42,
        tissue="left atrium",
    )

    metadata = sample.metadata()

    assert metadata.accession == "GSM1"
    assert metadata.age_years == 42
    assert metadata.sex == "male"
    assert metadata.tissue == "left atrium"
    assert metadata.organism == "Homo sapiens"