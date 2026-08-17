from dataclasses import dataclass


@dataclass(frozen=True)
class GEOSample:
    accession: str