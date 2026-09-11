from longevity_atlas.geo.parser import parse_sample


def test_parse_sample():
    data = {
        "accession": "GSM2539397",
        "title": "left atrium_4015",
        "sample_type": "RNA",
        "source_name": "left atrium",
        "organism": "Homo sapiens",
        "characteristics": "Sex: male\nage: 19 years\ntissue: left atrium",
    }

    sample = parse_sample(data)

    assert sample.accession == "GSM2539397"
    assert sample.organism == "Homo sapiens"
    assert sample.sex == "male"
    assert sample.age_years == 19
    assert sample.tissue == "left atrium"