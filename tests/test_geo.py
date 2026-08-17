import respx

from longevity_atlas.geo.client import GEOClient


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