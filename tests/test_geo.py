import respx

from longevity_atlas.geo.client import GEOClient
from longevity_atlas.geo.parser import parse_raw_sample, parse_sample_response


@respx.mock
def test_get():
    url = "https://example.com/test"
    respx.get(url).respond(
        status_code=200,
        text="hello from test",
    )

    client = GEOClient()

    result = client.get(url)

    assert result == "hello from test"

@respx.mock
def test_search_ids():
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

    respx.get(url).respond(
        status_code=200,
        json={
            "esearchresult": {
                "idlist": ["123456", "789012"],
            }
        },
    )

    with GEOClient() as client:
        ids = client.search_ids("GSE96752")

    assert ids == ["123456", "789012"]

@respx.mock
def test_fetch():
    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    respx.get(url).respond(
        status_code=200,
        text="!Sample_title\tSample 1\n!Sample_geo_accession\tGSM123",
    )

    with GEOClient() as client:
        result = client.fetch("123456")

    assert "!Sample_geo_accession" in result
    assert "GSM123" in result

@respx.mock
def test_get_sample():
    geo_url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

    respx.get(geo_url).respond(
        status_code=200,
        text=(
            "^SAMPLE = GSM2539397\n"
            "!Sample_title = left atrium_4015\n"
            "!Sample_geo_accession = GSM2539397\n"
        ),
    )

    with GEOClient() as client:
        result = client.get_sample("GSM2539397")

    assert "GSM2539397" in result
    assert "left atrium_4015" in result

@respx.mock
def test_get_and_parse_sample():
    geo_url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

    respx.get(geo_url).respond(
        status_code=200,
        text=(
            "^SAMPLE = GSM2539397\n"
            "!Sample_title = left atrium_4015\n"
            "!Sample_geo_accession = GSM2539397\n"
            "!Sample_type = RNA\n"
            "!Sample_source_name_ch1 = left atrium\n"
            "!Sample_organism_ch1 = Homo sapiens\n"
            "!Sample_characteristics_ch1 = Sex: male\n"
            "!Sample_characteristics_ch1 = age: 19 years\n"
            "!Sample_characteristics_ch1 = tissue: left atrium\n"
            "!sample_table_begin\n"
            "ID_REF     VALUE\n"
            "1  0.249459841\n"
            "2  0.108114464\n"
            "3  -0.678952084\n"
            "!sample_table_end\n"
        ),
    )

    with GEOClient() as client:
        raw = client.get_sample("GSM2539397")

    data = parse_raw_sample(raw)
    sample = parse_sample_response(raw)

    assert data["accession"] == "GSM2539397"
    assert sample.accession == "GSM2539397"
    assert sample.organism == "Homo sapiens"
    assert sample.sex == "male"
    assert sample.age_years == 19
    assert sample.tissue == "left atrium"
    assert len(sample.expression) == 3
