
import httpx


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