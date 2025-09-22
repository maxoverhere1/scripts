#!/usr/bin/env python3
"""
This script orchestrates the comparison process by:
1. Creating a ContentModelComparator instance
2. Fetching and comparing the content models
3. Generating reports and exports
4. Displaying summary statistics
"""

from content_model_comparator import ContentModelComparator
from content_model_reader import ContentfulModelReader


def main():
    print("🚀 Starting Contentful Content Model Comparison")
    print("=" * 50)
    
    try:
        print("\n=== Fetching content models ===")
        reader1 = ContentfulModelReader('CONTENTFUL_SPACE_ID', 'CONTENTFUL_ENVIRONMENT_ID')
        reader2 = ContentfulModelReader('CONTENTFUL_SPACE_ID_2', 'CONTENTFUL_ENVIRONMENT_ID_2')
        
        print(f"Space 1: {reader1.space_id} / {reader1.environment_id}")
        model1 = reader1.fetch_content_model()
        
        print(f"Space 2: {reader2.space_id} / {reader2.environment_id}")
        model2 = reader2.fetch_content_model()

        comparator = ContentModelComparator(model1, model2, reader1.space_id, reader2.space_id)

        # differences = comparator.compare_models()
        # comparator.export_to_csv(differences)
        # comparator.print_summary(differences)

    except Exception as e:
        print(f"\n❌ Error during comparison: {str(e)}")
        print("\nPlease check:")
        print("  1. Your .contentful.env file has correct credentials")
        print("  2. Your management token has access to both spaces")
        print("  3. The space IDs and environment IDs are correct")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
