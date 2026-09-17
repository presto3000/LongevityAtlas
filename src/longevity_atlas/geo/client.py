

import httpx

from longevity_atlas.geo.models import GEOSample, GEOSeries
from longevity_atlas.geo.parser import parse_sample_response, parse_series_response


class GEOClient:
    """Client for retrieving data from NCBI GEO."""

    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def __init__(self) -> None:
        self.client = httpx.Client(timeout=30.0)

    def __enter__(self) -> "GEOClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()

    def close(self) -> None:
        self.client.close()

    def get(self, url: str) -> str:
        response = self.client.get(url)
        response.raise_for_status()
        return response.text

    def search(self, term: str) -> dict:
        response = self.client.get(
            f"{self.BASE_URL}/esearch.fcgi",
            params={
                "db": "gds",
                "term": term,
                "retmode": "json",
            },
        )
        response.raise_for_status()
        return response.json()
    
    def search_ids(self, term: str) -> list[str]:
        data = self.search(term)
        return data["esearchresult"]["idlist"]

    def fetch(self, ncbi_id: str) -> str:
        response = self.client.get(
            f"{self.BASE_URL}/efetch.fcgi",
            params={
                "db": "gds",
                "id": ncbi_id,
                "retmode": "text",
            },
        )
        response.raise_for_status()
        return response.text


    def get_sample(self, accession: str) -> GEOSample:
        response = self.client.get(
            "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi",
            params={
                "acc": accession,
                "targ": "self",
                "view": "full",
                "form": "text",
            },
        )
        response.raise_for_status()
    
        return parse_sample_response(response.text)

    def search_series_samples(self, accession: str) -> list[str]:
        response = self.client.get(
            f"{self.BASE_URL}/esearch.fcgi",
            params={
                "db": "gds",
                "term": f"{accession}[Accession]",
                "retmode": "json",
            },
        )
        response.raise_for_status()

        data = response.json()

        return data["esearchresult"]["idlist"]

    def get_series(self, accession: str) -> GEOSeries:
        response = self.client.get(
            "https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi",
            params={
                "acc": accession,
                "targ": "self",
                "view": "full",
                "form": "text",
            },
        )
        response.raise_for_status()

        return parse_series_response(response.text)


    def get_series_samples(
        self,
        accession: str,
        limit: int | None = None,
) ->     list[GEOSample]:
        series = self.get_series(accession)
    
        sample_accessions = series.sample_accessions
    
        if limit is not None:
            sample_accessions = sample_accessions[:limit]
    
        return [
            self.get_sample(sample_accession)
            for sample_accession in sample_accessions
        ]