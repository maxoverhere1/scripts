#!/usr/bin/env python3
"""
This script orchestrates the comparison process by:
1. Creating a ContentModelComparator instance
2. Fetching and comparing the content models
3. Generating reports and exports
4. Displaying summary statistics
"""

from content_model_comparator import ContentModelComparator


def main():
    print("🚀 Starting Contentful Content Model Comparison")
    print("=" * 50)
    
    try:
        comparator = ContentModelComparator()
        
        print("\n📊 Running comparison...")
        differences = comparator.compare_models()
        
        print("\n💾 Exporting results...")
        csv_file = comparator.export_to_csv()
        
        summary = comparator.get_differences_summary()
        print("\n📈 Comparison Summary:")
        print("=" * 30)
        print(f"  Missing types in Space 1: {summary['missing_types_space1']}")
        print(f"  Missing types in Space 2: {summary['missing_types_space2']}")
        print(f"  Types with field differences: {summary['types_with_field_differences']}")
        print(f"  Types with definition differences: {summary['types_with_definition_differences']}")
        print(f"  Total missing fields in Space 1: {summary['total_missing_fields_space1']}")
        print(f"  Total missing fields in Space 2: {summary['total_missing_fields_space2']}")
        print(f"  Total field definition differences: {summary['total_definition_differences']}")
        
        total_differences = sum([
            summary['missing_types_space1'], 
            summary['missing_types_space2'],
            summary['types_with_field_differences'], 
            summary['types_with_definition_differences']
        ])
        
        if total_differences > 0:
            print(f"\n📄 Detailed report exported to: {csv_file}")
            print("\n🔍 For detailed console output, you can also call:")
            print("    comparator.print_differences()")
        else:
            print("\n✅ Content models are identical!")
        
        print("\n🎉 Comparison completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during comparison: {str(e)}")
        print("\nPlease check:")
        print("  1. Your contentful.env file has correct credentials")
        print("  2. Your management token has access to both spaces")
        print("  3. The space IDs and environment IDs are correct")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
