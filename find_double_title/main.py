#!/usr/bin/env python3
"""
This script finds pages where the page heading matches the article's first text.
It generates a CSV report with slug, page ID, and title.
"""

from page_title_finder import PageTitleFinder


def main():
    print("🔍 Starting Duplicate Title Finder")
    print("=" * 50)
    
    try:
        # Initialize the finder with environment variable names
        # You'll need to set these in your .env file:
        # CONTENTFUL_SPACE_ID=your_space_id
        # CONTENTFUL_ENVIRONMENT_ID=your_environment_id  
        # CONTENTFUL_DELIVERY_TOKEN=your_delivery_token
        
        finder = PageTitleFinder(
            'CONTENTFUL_SPACE_ID',
            'CONTENTFUL_ENVIRONMENT_ID',
            'CONTENTFUL_DELIVERY_TOKEN'
        )
        
        print("\n=== Fetching pages ===")
        pages = finder.fetch_all_pages()
        
        print("\n=== Checking for duplicate titles ===")
        duplicates = finder.check_duplicate_titles(pages)
        
        print(f"\n📊 Found {len(duplicates)} pages with duplicate titles")
        
        if duplicates:
            finder.generate_csv_report(duplicates)
        else:
            print("No duplicate titles found!")
        
        print("\n✅ Done!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nPlease check:")
        print("  1. Your .env file has correct credentials")
        print("  2. CONTENTFUL_SPACE_ID is set")
        print("  3. CONTENTFUL_ENVIRONMENT_ID is set")
        print("  4. CONTENTFUL_DELIVERY_TOKEN is set")
        return 1


if __name__ == "__main__":
    exit(main())


