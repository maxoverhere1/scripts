# Find Double Title

This script identifies pages in Contentful where the page heading matches the article's first text content.

## Purpose

Finds instances where:
- The content type is "page"
- The page links to an "article" content type
- The page's `heading` field is identical to the first text in the article's `content` field

This helps identify potential duplicate titles that could be simplified.

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

3. Required environment variables in `.env`:
   - `CONTENTFUL_SPACE_ID` - Your Contentful space ID
   - `CONTENTFUL_ENVIRONMENT_ID` - Environment (e.g., master, staging)
   - `CONTENTFUL_DELIVERY_TOKEN` - Content Delivery API token

## Usage

Run the script:
```bash
python3 main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

## Output

The script generates a CSV file in the `generated/` directory:
- **File name**: `duplicate_titles.csv`
- **Columns**: 
  - `slug` - Page URL slug
  - `page_id` - Contentful page entry ID
  - `title` - The duplicate title text

## Example Output

```
🔍 Starting Duplicate Title Finder
==================================================

=== Fetching pages ===
✅ Fetched 150 pages from 3p2fxa94bzao/master

=== Checking for duplicate titles ===
  Found duplicate: getting-started - 'Getting Started'
  Found duplicate: account-settings - 'Account Settings'

📊 Found 2 pages with duplicate titles

✅ CSV report generated: generated/duplicate_titles.csv

✅ Done!
```

## How It Works

1. **Fetch Pages**: Retrieves all "page" content types from Contentful using the Delivery API
2. **Resolve Links**: Includes linked content (up to 2 levels deep)
3. **Check Articles**: For each page linking to an article, extracts the first text from the article's RichText content
4. **Compare**: Compares the page heading with the article's first text (case-insensitive)
5. **Report**: Generates a CSV with all matches

## Notes

- The script handles localized content (tries en, en-US, en-GB locales)
- Only checks pages linked to "article" content types (not category, subCategory, or form)
- Comparison is case-insensitive
- Requires read-only Delivery API access (not Management API)


