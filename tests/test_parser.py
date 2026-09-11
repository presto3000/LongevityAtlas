from longevity_atlas.geo.models import GEOExpression
from longevity_atlas.geo.parser import parse_expression_table, parse_raw_sample, parse_sample


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


def test_parse_raw_sample():
    raw = (
        "!Sample_geo_accession\tGSM2539397\n"
        "!Sample_title\tleft atrium_4015\n"
        "!Sample_type\tRNA\n"
        "!Sample_source_name_ch1\tleft atrium\n"
        "!Sample_organism_ch1\tHomo sapiens\n"
        "!Sample_characteristics_ch1\tSex: male; age: 19 years; tissue: left atrium"
    )

    data = parse_raw_sample(raw)

    assert data["accession"] == "GSM2539397"
    assert data["title"] == "left atrium_4015"
    assert data["sample_type"] == "RNA"
    assert data["source_name"] == "left atrium"
    assert data["organism"] == "Homo sapiens"
    assert data["characteristics"] == (
        "Sex: male; age: 19 years; tissue: left atrium"
    )




def test_parse_expression_table():
    raw = (
        "!sample_table_begin\n"
        "ID_REF     VALUE\n"
        "1  0.249459841\n"
        "2  0.108114464\n"
        "3  -0.678952084\n"
        "!sample_table_end\n"
    )

    result = parse_expression_table(raw)

    assert result == [
        GEOExpression(probe_id="1", value=0.249459841),
        GEOExpression(probe_id="2", value=0.108114464),
        GEOExpression(probe_id="3", value=-0.678952084),
    ]