

# Read production IDs
with open('prod_contentful_ids.txt', 'r') as f:
    prod_ids = set(line.strip() for line in f if line.strip())

# Read staging IDs
with open('staging_contentful_ids.txt', 'r') as f:
    staging_ids = set(line.strip() for line in f if line.strip())

# Find IDs in prod but not in staging
missing_in_staging = prod_ids - staging_ids

print(f"Total prod IDs: {len(prod_ids)}")
print(f"Total staging IDs: {len(staging_ids)}")
print(f"IDs in prod but not in staging: {len(missing_in_staging)}")
print("\nMissing IDs:")
for id in sorted(missing_in_staging):
    print(id)
