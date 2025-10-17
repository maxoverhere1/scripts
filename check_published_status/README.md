# Check Published Status

This script checks the published status of Contentful page entries and generates CSV reports.

## Purpose

Checks a list of page IDs to determine which are published and which are unpublished, generating two separate CSV files for easy reference.

## Setup

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Configure environment:
   ```bash
   cp env.example .env
   # Edit .env with your Contentful credentials
   ```

3. Add page IDs:
   - Edit `page_ids.txt` and add one page ID per line
   - Or replace with your own list

## Usage

Run the script:
```bash
python3 main.py
```

## Input

**page_ids.txt** - Text file containing page IDs, one per line:
```
NVTp8FzuxSed3FgZUhqwr
5pl43WVxHmJhiSqvRDF8Pq
5WeSOeKkJu5K8tcjllUqOM
...
```

## Output

The script generates two CSV files in the `generated/` directory:

### published_pages.csv
Contains pages that are currently published:
- `page_id` - The Contentful entry ID
- `slug` - The page URL slug

### unpublished_pages.csv
Contains pages that are not published:
- `page_id` - The Contentful entry ID
- `slug` - The page URL slug

## Example Output

```
📋 Starting Published Status Checker
==================================================
✅ Read 18 page IDs from page_ids.txt

=== Checking page status ===
  [1/18] Checking NVTp8FzuxSed3FgZUhqwr... ✓ Published
  [2/18] Checking 5pl43WVxHmJhiSqvRDF8Pq... ✗ Unpublished
  [3/18] Checking 5WeSOeKkJu5K8tcjllUqOM... ✓ Published
  ...

✅ Published pages CSV: generated/published_pages.csv
   (15 pages)
✅ Unpublished pages CSV: generated/unpublished_pages.csv
   (3 pages)

📊 Summary:
   Total pages checked: 18
   Published: 15
   Unpublished: 3

✅ Done!
```

## Notes

- Uses the Contentful Delivery API (read-only)
- Pages are considered published if they have a `publishedVersion` in their sys metadata
- If a page ID doesn't exist or causes an error, it will be marked as unpublished with slug 'ERROR'
- Both published and unpublished CSVs include the slug for easy identification

