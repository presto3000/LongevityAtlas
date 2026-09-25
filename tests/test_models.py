from longevity_atlas.geo.models import GEODataset, GEOSample


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