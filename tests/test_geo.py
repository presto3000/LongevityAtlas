
import httpx
import pytest
import respx

from longevity_atlas.geo.client import GEOClient
from longevity_atlas.geo.models import GEOSample


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

    assert isinstance(result, GEOSample)
    assert result.accession == "GSM2539397"
    assert result.title == "left atrium_4015"

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
        sample = client.get_sample("GSM2539397")

    assert sample.accession == "GSM2539397"
    assert sample.organism == "Homo sapiens"
    assert sample.sex == "male"
    assert sample.age_years == 19
    assert sample.tissue == "left atrium"
    assert len(sample.expression) == 3
    assert sample.expression[0].probe_id == "1"
    assert sample.expression[0].value == 0.249459841

    assert sample.expression[-1].probe_id == "3"
    assert sample.expression[-1].value == -0.678952084

@respx.mock
def test_get_sample_not_found():
    geo_url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

    respx.get(geo_url).respond(
        status_code=404,
        text="Not Found",
    )

    with GEOClient() as client:
        with pytest.raises(httpx.HTTPStatusError):
            client.get_sample("GSM_DOES_NOT_EXIST")

def test_get_series():
    raw = (
        "^SERIES = GSE96752\n"
        "!Series_title = Gene expression profile of human cardiac aging\n"
        "!Series_geo_accession = GSE96752\n"
        "!Series_sample_id = GSM2539397\n"
        "!Series_sample_id = GSM2539398\n"
        "!Series_sample_id = GSM2539399\n"
    )

    geo_url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

    with respx.mock:
        respx.get(geo_url).respond(
            status_code=200,
            text=raw,
        )

        with GEOClient() as client:
            result = client.get_series("GSE96752")

    assert result.accession == "GSE96752"
    assert result.title == "Gene expression profile of human cardiac aging"
    assert result.sample_accessions == (
        "GSM2539397",
        "GSM2539398",
        "GSM2539399",
    )

@respx.mock
def test_get_series_samples():
    geo_url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

    series_raw = (
        "^SERIES = GSE96752\n"
        "!Series_title = Gene expression profile of human cardiac aging\n"
        "!Series_geo_accession = GSE96752\n"
        "!Series_sample_id = GSM2539397\n"
        "!Series_sample_id = GSM2539398\n"
        "!Series_sample_id = GSM2539399\n"
    )

    sample_raw = {
        "GSM2539397": (
            "^SAMPLE = GSM2539397\n"
            "!Sample_title = left atrium_4015\n"
            "!Sample_geo_accession = GSM2539397\n"
            "!Sample_type = RNA\n"
            "!Sample_source_name_ch1 = left atrium\n"
            "!Sample_organism_ch1 = Homo sapiens\n"
            "!Sample_characteristics_ch1 = Sex: male\n"
            "!Sample_characteristics_ch1 = age: 19 years\n"
            "!Sample_characteristics_ch1 = tissue: left atrium\n"
        ),
        "GSM2539398": (
            "^SAMPLE = GSM2539398\n"
            "!Sample_title = left atrium_4016\n"
            "!Sample_geo_accession = GSM2539398\n"
            "!Sample_type = RNA\n"
            "!Sample_source_name_ch1 = left atrium\n"
            "!Sample_organism_ch1 = Homo sapiens\n"
            "!Sample_characteristics_ch1 = Sex: female\n"
            "!Sample_characteristics_ch1 = age: 21 years\n"
            "!Sample_characteristics_ch1 = tissue: left atrium\n"
        ),
        "GSM2539399": (
            "^SAMPLE = GSM2539399\n"
            "!Sample_title = left atrium_4017\n"
            "!Sample_geo_accession = GSM2539399\n"
            "!Sample_type = RNA\n"
            "!Sample_source_name_ch1 = left atrium\n"
            "!Sample_organism_ch1 = Homo sapiens\n"
            "!Sample_characteristics_ch1 = Sex: male\n"
            "!Sample_characteristics_ch1 = age: 25 years\n"
            "!Sample_characteristics_ch1 = tissue: left atrium\n"
        ),
    }

    respx.get(
        geo_url,
        params={
            "acc": "GSE96752",
            "targ": "self",
            "view": "full",
            "form": "text",
        },
    ).respond(
        status_code=200,
        text=series_raw,
    )

    for accession, raw in sample_raw.items():
        respx.get(
            geo_url,
            params={
                "acc": accession,
                "targ": "self",
                "view": "full",
                "form": "text",
            },
        ).respond(
            status_code=200,
            text=raw,
        )

    with GEOClient() as client:
        samples = client.get_series_samples("GSE96752")

    assert len(samples) == 3

    assert samples[0].accession == "GSM2539397"
    assert samples[0].age_years == 19
    assert samples[0].sex == "male"

    assert samples[1].accession == "GSM2539398"
    assert samples[1].age_years == 21
    assert samples[1].sex == "female"

    assert samples[2].accession == "GSM2539399"
    assert samples[2].age_years == 25
    assert samples[2].sex == "male"

@respx.mock
def test_get_series_samples_limit():
    geo_url = "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi"

    series_raw = (
        "^SERIES = GSE96752\n"
        "!Series_title = Gene expression profile of human cardiac aging\n"
        "!Series_geo_accession = GSE96752\n"
        "!Series_sample_id = GSM2539397\n"
        "!Series_sample_id = GSM2539398\n"
        "!Series_sample_id = GSM2539399\n"
    )

    sample_template = (
        "^SAMPLE = {accession}\n"
        "!Sample_title = test sample\n"
        "!Sample_geo_accession = {accession}\n"
        "!Sample_type = RNA\n"
        "!Sample_source_name_ch1 = left atrium\n"
        "!Sample_organism_ch1 = Homo sapiens\n"
        "!Sample_characteristics_ch1 = Sex: male\n"
        "!Sample_characteristics_ch1 = age: 50 years\n"
        "!Sample_characteristics_ch1 = tissue: left atrium\n"
        "!sample_table_begin\n"
        "ID_REF     VALUE\n"
        "1  0.1\n"
        "2  0.2\n"
        "3  0.3\n"
        "!sample_table_end\n"
    )

    respx.get(
        geo_url,
        params={
            "acc": "GSE96752",
            "targ": "self",
            "view": "full",
            "form": "text",
        },
    ).respond(status_code=200, text=series_raw)

    for accession in (
        "GSM2539397",
        "GSM2539398",
        "GSM2539399",
    ):
        respx.get(
            geo_url,
            params={
                "acc": accession,
                "targ": "self",
                "view": "full",
                "form": "text",
            },
        ).respond(
            status_code=200,
            text=sample_template.format(accession=accession),
        )

    with GEOClient() as client:
        samples = client.get_series_samples("GSE96752", limit=2)

    assert len(samples) == 2
    assert all(len(sample.expression) == 3 for sample in samples)