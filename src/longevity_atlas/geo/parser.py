import re

from longevity_atlas.geo.models import GEOSample


def parse_age(value: str | None) -> float | None:
    if value is None:
        return None

    match = re.search(r"(\d+(?:\.\d+)?)", value)

    if match is None:
        return None

    return float(match.group(1))


def parse_sample(data: dict[str, str]) -> GEOSample:
    characteristics = data.get("characteristics", "")

    sex = None
    tissue = None
    age_years = None

    for item in characteristics.split("\n"):
        key, separator, value = item.partition(":")

        if not separator:
            continue

        key = key.strip().lower()
        value = value.strip()

        if key == "sex":
            sex = value
        elif key == "tissue":
            tissue = value
        elif key == "age":
            age_years = parse_age(value)

    return GEOSample(
        accession=data["accession"],
        title=data["title"],
        sample_type=data.get("sample_type"),
        source_name=data.get("source_name"),
        organism=data.get("organism"),
        sex=sex,
        age_years=age_years,
        tissue=tissue,
    )