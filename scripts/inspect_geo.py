from longevity_atlas.geo.client import GEOClient

with GEOClient() as client:
    """
    ids = client.search_ids("GSE96752")

    print(f"Found {len(ids)} IDs")

    for ncbi_id in ids[:1]:
        print(f"\nFetching {ncbi_id}...\n")

        record = client.fetch(ncbi_id)

        print(f"Record length: {len(record)} characters")
        print(record) """

    ids = client.search_ids("GSE96752")

    print(f"Found {len(ids)} IDs")

    record = client.fetch(ids[0])

    print(record)