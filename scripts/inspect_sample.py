from longevity_atlas.geo.client import GEOClient

with GEOClient() as client:
    raw = client.get_sample("GSM2539397")

print("\n--- FIRST 80 LINES ---")

for i, line in enumerate(raw.splitlines()[:80]):
    print(f"{i:03}: {line}")

print("\n--- LAST 20 LINES ---")

for i, line in enumerate(raw.splitlines()[-20:], start=len(raw.splitlines()) - 20):
    print(f"{i:05}: {line}")