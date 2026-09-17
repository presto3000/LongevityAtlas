import re

from longevity_atlas.geo.models import GEOExpression, GEOSample, GEOSeries


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

        if "\t" in line:
            key, _, value = line.partition("\t")
        elif " = " in line:
            key, _, value = line.partition(" = ")
        else:
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
        if key == "characteristics":
            if "characteristics" in data:
                data["characteristics"] += "\n" + value
            else:
                data["characteristics"] = value
        else:
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

        if not in_table or not line:
            continue
        
        parts = line.split()

        if parts == ["ID_REF", "VALUE"]:
            continue

        parts = line.split()
        
        if len(parts) != 2:
            continue
        
        probe_id, value = parts
        
        expressions.append(
            GEOExpression(
                probe_id=probe_id,
                value=float(value),
            )
        )

    return expressions

def parse_sample_response(raw: str) -> GEOSample:
    data = parse_raw_sample(raw)
    expression = parse_expression_table(raw)

    sample = parse_sample(data)

    return GEOSample(
        accession=sample.accession,
        title=sample.title,
        sample_type=sample.sample_type,
        source_name=sample.source_name,
        organism=sample.organism,
        sex=sample.sex,
        age_years=sample.age_years,
        tissue=sample.tissue,
        expression=tuple(expression),
    )

def parse_series_response(raw: str) -> GEOSeries:
    data: dict[str, str] = {}
    sample_accessions: list[str] = []

    for line in raw.splitlines():
        if not line.startswith("!Series_"):
            continue

        if " = " not in line:
            continue

        key, _, value = line.partition(" = ")

        if key == "!Series_geo_accession":
            data["accession"] = value

        elif key == "!Series_title":
            data["title"] = value

        elif key == "!Series_sample_id":
            sample_accessions.append(value)

    return GEOSeries(
        accession=data["accession"],
        title=data["title"],
        sample_accessions=tuple(sample_accessions),
    )