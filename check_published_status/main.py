#!/usr/bin/env python3
"""
This script checks the published status of Contentful page entries.
It reads page IDs from a file and generates two CSV reports:
- published_pages.csv: Pages that are published
- unpublished_pages.csv: Pages that are not published
"""

from published_checker import PublishedChecker


def main():
    print("📋 Starting Published Status Checker")
    print("=" * 50)
    
    try:
        # Initialize the checker with environment variable names
        checker = PublishedChecker(
            'CONTENTFUL_SPACE_ID',
            'CONTENTFUL_ENVIRONMENT_ID',
            'CONTENTFUL_MANAGEMENT_TOKEN'
        )
        
        # Read page IDs from file
        page_ids = checker.read_page_ids('page_ids.txt')
        
        # Check all pages
        published, unpublished = checker.check_all_pages(page_ids)
        
        # Generate CSV reports
        checker.generate_csv_reports(published, unpublished)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   Total pages checked: {len(page_ids)}")
        print(f"   Published: {len(published)}")
        print(f"   Unpublished: {len(unpublished)}")
        
        print("\n✅ Done!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check:")
        print("  1. Your .env file has correct credentials")
        print("  2. CONTENTFUL_SPACE_ID is set")
        print("  3. CONTENTFUL_ENVIRONMENT_ID is set")
        print("  4. CONTENTFUL_MANAGEMENT_TOKEN is set")
        print("  5. page_ids.txt exists and contains valid page IDs")
        return 1


if __name__ == "__main__":
    exit(main())

