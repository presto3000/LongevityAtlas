import respx

from longevity_atlas.geo.client import GEOClient
from longevity_atlas.geo.parser import parse_raw_sample, parse_sample


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
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    respx.get(search_url).respond(
        status_code=200,
        json={
            "esearchresult": {
                "idlist": ["123456"],
            }
        },
    )

    respx.get(fetch_url).respond(
        status_code=200,
        text="!Sample_geo_accession\tGSM2539397\n"
        "!Sample_title\tleft atrium_4015",
    )

    with GEOClient() as client:
        result = client.get_sample("GSM2539397")

    assert "GSM2539397" in result
    assert "left atrium_4015" in result

@respx.mock
def test_get_and_parse_sample():
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    fetch_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    respx.get(search_url).respond(
        status_code=200,
        json={
            "esearchresult": {
                "idlist": ["123456"],
            }
        },
    )

    respx.get(fetch_url).respond(
        status_code=200,
        text=(
                "!Sample_geo_accession\tGSM2539397\n"
                "!Sample_title\tleft atrium_4015\n"
                "!Sample_type\tRNA\n"
                "!Sample_source_name_ch1\tleft atrium\n"
                "!Sample_organism_ch1\tHomo sapiens\n"
                "!Sample_characteristics_ch1\tSex: male; age: 19 years; tissue: left atrium"
        ),
    )

    with GEOClient() as client:
        raw = client.get_sample("GSM2539397")
    
    data = parse_raw_sample(raw)
    sample = parse_sample(data)

    assert sample.accession == "GSM2539397"
    assert sample.organism == "Homo sapiens"
    assert sample.sex == "male"
    assert sample.age_years == 19
    assert sample.tissue == "left atrium"
