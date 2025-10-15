#!/usr/bin/env python3
"""
This script orchestrates the comparison process by:
1. Creating a ContentModelComparator instance
2. Fetching and comparing the content models
3. Generating reports and exports
4. Displaying summary statistics
"""

from typing import List
from content_model_reader import ContentfulModelReader, ContentType
from diff_page_builder import DiffPageBuilder


def main():
    print("🚀 Starting Contentful Content Model Comparison")
    print("=" * 50)
    
    try:
        print("\n=== Fetching content models ===")
        reader1 = ContentfulModelReader('CONTENTFUL_SPACE_ID', 'CONTENTFUL_ENVIRONMENT_ID')
        reader2 = ContentfulModelReader('CONTENTFUL_SPACE_ID_2', 'CONTENTFUL_ENVIRONMENT_ID_2')
        
        print(f"Space 1: {reader1.space_id} / {reader1.environment_id}")
        model1: List[ContentType] = reader1.fetch_content_model()
        
        print(f"Space 2: {reader2.space_id} / {reader2.environment_id}")
        model2: List[ContentType] = reader2.fetch_content_model()

        # Generate HTML diff page
        diff_builder = DiffPageBuilder(model1, model2, reader1.space_id, reader2.space_id)
        html_file = diff_builder.create_html_diff()

    except Exception as e:
        print(f"\n❌ Error during comparison: {str(e)}")
        print("\nPlease check:")
        print("  1. Your .env file has correct credentials")
        print("  2. Your management token has access to both spaces")
        print("  3. The space IDs and environment IDs are correct")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
