#!/usr/bin/env python3
"""
ContentModelComparator - A class for comparing Contentful content models between spaces.

This module provides functionality to:
- Compare content types between two Contentful spaces/environments
- Identify missing content types and fields
- Detect differences in field definitions
- Export comparison results to CSV format
"""

import os
import csv
import json
from typing import Dict, List, Any, Set, Tuple
from dotenv import load_dotenv
from content_model_reader import ContentfulModelReader


class ContentModelComparator:
    """
    A class to compare content models between two Contentful spaces/environments.
    """
    
    def __init__(self):
        """
        Initialize the ContentModelComparator by loading environment variables
        and setting up readers for both spaces.
        """
        # Load environment variables from contentful.env
        load_dotenv('contentful.env')
        
        # Setup first space reader
        self.reader1 = ContentfulModelReader(
            space_id=os.getenv('CONTENTFUL_SPACE_ID'),
            environment_id=os.getenv('CONTENTFUL_ENVIRONMENT_ID'),
            management_token=os.getenv('CONTENTFUL_MANAGEMENT_TOKEN')
        )
        
        # Setup second space reader
        self.reader2 = ContentfulModelReader(
            space_id=os.getenv('CONTENTFUL_SPACE_ID_2'),
            environment_id=os.getenv('CONTENTFUL_ENVIRONMENT_ID_2'),
            management_token=os.getenv('CONTENTFUL_MANAGEMENT_TOKEN')
        )
        
        self.model1 = None
        self.model2 = None
        self.differences = {
            'missing_types': {'space1': [], 'space2': []},
            'field_differences': {},
            'definition_differences': {}
        }
    
    def fetch_models(self) -> None:
        """
        Fetch content models from both spaces.
        """
        print("\n=== Fetching content models ===")
        print(f"Space 1: {self.reader1.space_id} / {self.reader1.environment_id}")
        self.model1 = self.reader1.fetch_content_model()
        
        print(f"Space 2: {self.reader2.space_id} / {self.reader2.environment_id}")
        self.model2 = self.reader2.fetch_content_model()
    
    def _serialize_validation(self, validation) -> Dict[str, Any]:
        """
        Convert a validation object to a comparable dictionary.
        """
        if hasattr(validation, 'raw'):
            # If the object has a raw attribute, use it
            return validation.raw
        elif hasattr(validation, '__dict__'):
            # Try to get the object's attributes as a dict
            result = {}
            for key, value in validation.__dict__.items():
                if not key.startswith('_'):  # Skip private attributes
                    result[key] = value
            return result
        else:
            # Fallback to string representation
            return str(validation)
    
    def _get_field_definition(self, field) -> Dict[str, Any]:
        """
        Extract relevant field definition properties for comparison.
        """
        definition = {
            'type': getattr(field, 'type', None),
            'required': getattr(field, 'required', False),
            'localized': getattr(field, 'localized', False),
            'disabled': getattr(field, 'disabled', False),
            'omitted': getattr(field, 'omitted', False)
        }
        
        # Handle name field
        name = getattr(field, 'name', None)
        if name:
            definition['name'] = name
        
        # Add type-specific properties
        if getattr(field, 'type', None) == 'Link':
            definition['linkType'] = getattr(field, 'link_type', None)
            validations = getattr(field, 'validations', None)
            if validations:
                serialized_validations = []
                for validation in validations:
                    if isinstance(validation, dict):
                        serialized_validations.append(validation)
                    else:
                        serialized_validations.append(self._serialize_validation(validation))
                if serialized_validations:
                    definition['validations'] = serialized_validations
        
        if getattr(field, 'type', None) == 'Array':
            items = getattr(field, 'items', None)
            if items:
                if hasattr(items, 'raw'):
                    definition['items'] = items.raw
                elif hasattr(items, '__dict__'):
                    definition['items'] = {k: v for k, v in items.__dict__.items() if not k.startswith('_')}
                else:
                    definition['items'] = str(items)
        
        # Handle validations for all field types
        validations = getattr(field, 'validations', None)
        if validations and 'validations' not in definition:
            serialized_validations = []
            for validation in validations:
                if isinstance(validation, dict):
                    serialized_validations.append(validation)
                else:
                    serialized_validations.append(self._serialize_validation(validation))
            if serialized_validations:
                definition['validations'] = serialized_validations
            
        return definition
    
    def compare_models(self) -> Dict[str, Any]:
        """
        Compare the two content models and identify differences.
        
        Returns:
            Dictionary containing all differences found
        """
        if not self.model1 or not self.model2:
            self.fetch_models()
        
        print("\n=== Comparing content models ===")
        
        # Create dictionaries for easier lookup
        types1 = {ct.id: ct for ct in self.model1}
        types2 = {ct.id: ct for ct in self.model2}
        
        # Find missing content types
        types1_ids = set(types1.keys())
        types2_ids = set(types2.keys())
        
        missing_in_space2 = types1_ids - types2_ids
        missing_in_space1 = types2_ids - types1_ids
        
        if missing_in_space2:
            self.differences['missing_types']['space2'] = list(missing_in_space2)
        if missing_in_space1:
            self.differences['missing_types']['space1'] = list(missing_in_space1)
        
        # Compare common content types
        common_types = types1_ids & types2_ids
        
        for type_id in common_types:
            ct1 = types1[type_id]
            ct2 = types2[type_id]
            
            # Get fields as dictionaries
            fields1 = {f.id: f for f in ct1.fields}
            fields2 = {f.id: f for f in ct2.fields}
            
            fields1_ids = set(fields1.keys())
            fields2_ids = set(fields2.keys())
            
            # Check for missing fields
            missing_fields_in_space2 = fields1_ids - fields2_ids
            missing_fields_in_space1 = fields2_ids - fields1_ids
            
            if missing_fields_in_space2 or missing_fields_in_space1:
                if type_id not in self.differences['field_differences']:
                    self.differences['field_differences'][type_id] = {
                        'missing_in_space1': [],
                        'missing_in_space2': []
                    }
                
                if missing_fields_in_space2:
                    self.differences['field_differences'][type_id]['missing_in_space2'] = list(missing_fields_in_space2)
                if missing_fields_in_space1:
                    self.differences['field_differences'][type_id]['missing_in_space1'] = list(missing_fields_in_space1)
            
            # Compare common fields
            common_fields = fields1_ids & fields2_ids
            
            for field_id in common_fields:
                field1 = fields1[field_id]
                field2 = fields2[field_id]
                
                def1 = self._get_field_definition(field1)
                def2 = self._get_field_definition(field2)
                
                if def1 != def2:
                    if type_id not in self.differences['definition_differences']:
                        self.differences['definition_differences'][type_id] = {}
                    
                    self.differences['definition_differences'][type_id][field_id] = {
                        'space1': def1,
                        'space2': def2
                    }
        
        return self.differences
    
    def print_differences(self) -> None:
        """
        Print a formatted report of all differences found.
        """
        print("\n" + "="*60)
        print("CONTENT MODEL COMPARISON REPORT")
        print("="*60)
        
        # Check if there are any differences
        has_differences = False
        
        # Missing content types
        if self.differences['missing_types']['space1']:
            has_differences = True
            print(f"\n📦 Content Types missing in Space 1 ({self.reader1.space_id}):")
            for ct in self.differences['missing_types']['space1']:
                print(f"  - {ct}")
        
        if self.differences['missing_types']['space2']:
            has_differences = True
            print(f"\n📦 Content Types missing in Space 2 ({self.reader2.space_id}):")
            for ct in self.differences['missing_types']['space2']:
                print(f"  - {ct}")
        
        # Field differences
        if self.differences['field_differences']:
            has_differences = True
            print("\n📝 Field Differences:")
            for type_id, field_diffs in self.differences['field_differences'].items():
                print(f"\n  Content Type: {type_id}")
                if field_diffs['missing_in_space1']:
                    print(f"    Missing in Space 1:")
                    for field in field_diffs['missing_in_space1']:
                        print(f"      - {field}")
                if field_diffs['missing_in_space2']:
                    print(f"    Missing in Space 2:")
                    for field in field_diffs['missing_in_space2']:
                        print(f"      - {field}")
        
        # Definition differences
        if self.differences['definition_differences']:
            has_differences = True
            print("\n⚙️  Field Definition Differences:")
            for type_id, fields in self.differences['definition_differences'].items():
                print(f"\n  Content Type: {type_id}")
                for field_id, defs in fields.items():
                    print(f"    Field: {field_id}")
                    
                    # Find what's different
                    def1 = defs['space1']
                    def2 = defs['space2']
                    
                    for key in set(def1.keys()) | set(def2.keys()):
                        val1 = def1.get(key)
                        val2 = def2.get(key)
                        if val1 != val2:
                            print(f"      {key}:")
                            print(f"        Space 1: {val1}")
                            print(f"        Space 2: {val2}")
        
        if not has_differences:
            print("\n✅ No differences found! Both content models are identical.")
        else:
            print("\n" + "="*60)
            print("END OF REPORT")
            print("="*60)
    
    def get_differences_summary(self) -> Dict[str, int]:
        """
        Get a summary count of differences.
        
        Returns:
            Dictionary with counts of different types of differences
        """
        summary = {
            'missing_types_space1': len(self.differences['missing_types']['space1']),
            'missing_types_space2': len(self.differences['missing_types']['space2']),
            'types_with_field_differences': len(self.differences['field_differences']),
            'types_with_definition_differences': len(self.differences['definition_differences'])
        }
        
        # Count total missing fields
        total_missing_fields_space1 = 0
        total_missing_fields_space2 = 0
        for field_diffs in self.differences['field_differences'].values():
            total_missing_fields_space1 += len(field_diffs['missing_in_space1'])
            total_missing_fields_space2 += len(field_diffs['missing_in_space2'])
        
        summary['total_missing_fields_space1'] = total_missing_fields_space1
        summary['total_missing_fields_space2'] = total_missing_fields_space2
        
        # Count total definition differences
        total_definition_differences = 0
        for fields in self.differences['definition_differences'].values():
            total_definition_differences += len(fields)
        
        summary['total_definition_differences'] = total_definition_differences
        
        return summary
    
    def export_to_csv(self, filename: str = 'content_model_differences.csv') -> str:
        """
        Export the differences to a CSV file in the generated directory.
        
        Args:
            filename: Name of the CSV file to create
            
        Returns:
            Path to the created CSV file
        """
        # Ensure generated directory exists
        generated_dir = 'generated'
        if not os.path.exists(generated_dir):
            os.makedirs(generated_dir)
        
        # Create full path to file in generated directory
        filepath = os.path.join(generated_dir, filename)
        rows = []
        
        # Add missing content types
        for ct in self.differences['missing_types']['space1']:
            rows.append({
                'Difference Type': 'Missing Content Type',
                'Content Type': ct,
                'Field': '',
                'Property': '',
                'Space 1 Value': 'Missing',
                'Space 2 Value': 'Present',
                'Space 1 ID': self.reader1.space_id,
                'Space 2 ID': self.reader2.space_id
            })
        
        for ct in self.differences['missing_types']['space2']:
            rows.append({
                'Difference Type': 'Missing Content Type',
                'Content Type': ct,
                'Field': '',
                'Property': '',
                'Space 1 Value': 'Present',
                'Space 2 Value': 'Missing',
                'Space 1 ID': self.reader1.space_id,
                'Space 2 ID': self.reader2.space_id
            })
        
        # Add missing fields
        for type_id, field_diffs in self.differences['field_differences'].items():
            for field in field_diffs['missing_in_space1']:
                rows.append({
                    'Difference Type': 'Missing Field',
                    'Content Type': type_id,
                    'Field': field,
                    'Property': '',
                    'Space 1 Value': 'Missing',
                    'Space 2 Value': 'Present',
                    'Space 1 ID': self.reader1.space_id,
                    'Space 2 ID': self.reader2.space_id
                })
            
            for field in field_diffs['missing_in_space2']:
                rows.append({
                    'Difference Type': 'Missing Field',
                    'Content Type': type_id,
                    'Field': field,
                    'Property': '',
                    'Space 1 Value': 'Present',
                    'Space 2 Value': 'Missing',
                    'Space 1 ID': self.reader1.space_id,
                    'Space 2 ID': self.reader2.space_id
                })
        
        # Add field definition differences
        for type_id, fields in self.differences['definition_differences'].items():
            for field_id, defs in fields.items():
                def1 = defs['space1']
                def2 = defs['space2']
                
                # Find all properties that differ
                all_keys = set(def1.keys()) | set(def2.keys())
                for key in all_keys:
                    val1 = def1.get(key)
                    val2 = def2.get(key)
                    if val1 != val2:
                        # Convert complex values to JSON strings for CSV
                        val1_str = json.dumps(val1) if isinstance(val1, (dict, list)) else str(val1)
                        val2_str = json.dumps(val2) if isinstance(val2, (dict, list)) else str(val2)
                        
                        rows.append({
                            'Difference Type': 'Field Definition',
                            'Content Type': type_id,
                            'Field': field_id,
                            'Property': key,
                            'Space 1 Value': val1_str,
                            'Space 2 Value': val2_str,
                            'Space 1 ID': self.reader1.space_id,
                            'Space 2 ID': self.reader2.space_id
                        })
        
        # Write to CSV
        if rows:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Difference Type', 'Content Type', 'Field', 'Property', 
                             'Space 1 Value', 'Space 2 Value', 'Space 1 ID', 'Space 2 ID']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"\n✅ Differences exported to: {filepath}")
            print(f"   Total differences: {len(rows)}")
        else:
            # Create empty CSV with just headers
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Difference Type', 'Content Type', 'Field', 'Property', 
                             'Space 1 Value', 'Space 2 Value', 'Space 1 ID', 'Space 2 ID']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            
            print(f"\n✅ No differences found! Empty CSV created: {filepath}")
        
        return filepath


