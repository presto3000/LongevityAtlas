import re

from longevity_atlas.geo.models import GEOExpression, GEOSample


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

    for item in re.split(r"[;\n]", characteristics):
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

def parse_raw_sample(raw: str) -> dict[str, str]:
    data = {}

    for line in raw.splitlines():
        if not line.startswith("!Sample_"):
            continue

        key, separator, value = line.partition("\t")

        if not separator:
            continue

        key = key.removeprefix("!Sample_")

        key_mapping = {
            "geo_accession": "accession",
            "type": "sample_type",
            "source_name_ch1": "source_name",
            "organism_ch1": "organism",
            "characteristics_ch1": "characteristics",
        }

        key = key_mapping.get(key, key)
        data[key] = value

    return data

def parse_expression_table(raw: str) -> list[GEOExpression]:
    """Parse the expression table from a GEO sample response."""
    expressions = []
    in_table = False

    for line in raw.splitlines():
        line = line.strip()

        if line == "!sample_table_begin":
            in_table = True
            continue

        if line == "!sample_table_end":
            break

        if not in_table or not line or line == "ID_REF     VALUE":
            continue

        probe_id, value = line.split()

        expressions.append(
            GEOExpression(
                probe_id=probe_id,
                value=float(value),
            )
        )

    return expressions