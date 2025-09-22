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

    def __init__(self, model1: List[Any], model2: List[Any], space1_id: str, space2_id: str):
        self.model1 = model1
        self.model2 = model2
        self.space1_id = space1_id
        self.space2_id = space2_id
    
    def _serialize_validation(self, validation) -> Dict[str, Any]:
        if hasattr(validation, 'raw'):
            return validation.raw
        elif hasattr(validation, '__dict__'):
            result = {}
            for key, value in validation.__dict__.items():
                if not key.startswith('_'):
                    result[key] = value
            return result
        else:
            return str(validation)
    
    def _get_field_definition(self, field) -> Dict[str, Any]:
        definition = {
            'type': getattr(field, 'type', None),
            'required': getattr(field, 'required', False),
            'localized': getattr(field, 'localized', False),
            'disabled': getattr(field, 'disabled', False),
            'omitted': getattr(field, 'omitted', False)
        }
        
        name = getattr(field, 'name', None)
        if name:
            definition['name'] = name
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
        print("\n📊 Running comparison...")
        print("\n=== Comparing content models ===")
        
        differences = {
            'missing_types': {'space1': [], 'space2': []},
            'field_differences': {},
            'definition_differences': {}
        }
        
        types1 = {ct.id: ct for ct in self.model1}
        types2 = {ct.id: ct for ct in self.model2}
        
        types1_ids = set(types1.keys())
        types2_ids = set(types2.keys())
        
        missing_in_space2 = types1_ids - types2_ids
        missing_in_space1 = types2_ids - types1_ids
        
        if missing_in_space2:
            differences['missing_types']['space2'] = list(missing_in_space2)
        if missing_in_space1:
            differences['missing_types']['space1'] = list(missing_in_space1)
        
        common_types = types1_ids & types2_ids
        
        for type_id in common_types:
            ct1 = types1[type_id]
            ct2 = types2[type_id]
            
            fields1 = {f.id: f for f in ct1.fields}
            fields2 = {f.id: f for f in ct2.fields}
            
            fields1_ids = set(fields1.keys())
            fields2_ids = set(fields2.keys())
            
            missing_fields_in_space2 = fields1_ids - fields2_ids
            missing_fields_in_space1 = fields2_ids - fields1_ids
            
            if missing_fields_in_space2 or missing_fields_in_space1:
                if type_id not in differences['field_differences']:
                    differences['field_differences'][type_id] = {
                        'missing_in_space1': [],
                        'missing_in_space2': []
                    }
                
                if missing_fields_in_space2:
                    differences['field_differences'][type_id]['missing_in_space2'] = list(missing_fields_in_space2)
                if missing_fields_in_space1:
                    differences['field_differences'][type_id]['missing_in_space1'] = list(missing_fields_in_space1)
            
            common_fields = fields1_ids & fields2_ids
            
            for field_id in common_fields:
                field1 = fields1[field_id]
                field2 = fields2[field_id]
                
                def1 = self._get_field_definition(field1)
                def2 = self._get_field_definition(field2)
                
                if def1 != def2:
                    if type_id not in differences['definition_differences']:
                        differences['definition_differences'][type_id] = {}
                    
                    differences['definition_differences'][type_id][field_id] = {
                        'space1': def1,
                        'space2': def2
                    }
        
        return differences
    
    def print_differences(self, differences: Dict[str, Any]) -> None:
        print("\n" + "="*60)
        print("CONTENT MODEL COMPARISON REPORT")
        print("="*60)
        
        has_differences = False
        if differences['missing_types']['space1']:
            has_differences = True
            print(f"\n📦 Content Types missing in Space 1 ({self.space1_id}):")
            for ct in differences['missing_types']['space1']:
                print(f"  - {ct}")
        
        if differences['missing_types']['space2']:
            has_differences = True
            print(f"\n📦 Content Types missing in Space 2 ({self.space2_id}):")
            for ct in differences['missing_types']['space2']:
                print(f"  - {ct}")
        
        if differences['field_differences']:
            has_differences = True
            print("\n📝 Field Differences:")
            for type_id, field_diffs in differences['field_differences'].items():
                print(f"\n  Content Type: {type_id}")
                if field_diffs['missing_in_space1']:
                    print(f"    Missing in Space 1:")
                    for field in field_diffs['missing_in_space1']:
                        print(f"      - {field}")
                if field_diffs['missing_in_space2']:
                    print(f"    Missing in Space 2:")
                    for field in field_diffs['missing_in_space2']:
                        print(f"      - {field}")
        
        if differences['definition_differences']:
            has_differences = True
            print("\n⚙️  Field Definition Differences:")
            for type_id, fields in differences['definition_differences'].items():
                print(f"\n  Content Type: {type_id}")
                for field_id, defs in fields.items():
                    print(f"    Field: {field_id}")
                    
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
    
    def get_differences_summary(self, differences: Dict[str, Any]) -> Dict[str, int]:
        summary = {
            'missing_types_space1': len(differences['missing_types']['space1']),
            'missing_types_space2': len(differences['missing_types']['space2']),
            'types_with_field_differences': len(differences['field_differences']),
            'types_with_definition_differences': len(differences['definition_differences'])
        }
        
        total_missing_fields_space1 = 0
        total_missing_fields_space2 = 0
        for field_diffs in differences['field_differences'].values():
            total_missing_fields_space1 += len(field_diffs['missing_in_space1'])
            total_missing_fields_space2 += len(field_diffs['missing_in_space2'])
        
        summary['total_missing_fields_space1'] = total_missing_fields_space1
        summary['total_missing_fields_space2'] = total_missing_fields_space2
        
        total_definition_differences = 0
        for fields in differences['definition_differences'].values():
            total_definition_differences += len(fields)
        
        summary['total_definition_differences'] = total_definition_differences
        
        return summary
    
    def print_summary(self, differences: Dict[str, Any]):
        summary = self.get_differences_summary(differences)
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
            print(f"\n📄 Detailed report will be exported to CSV")
            print("\n🔍 For detailed console output, you can also call:")
            print("    comparator.print_differences()")
        else:
            print("\n✅ Content models are identical!")
        
        return total_differences
    
    def export_to_csv(self, differences: Dict[str, Any], filename: str = 'content_model_differences.csv') -> str:
        print("\n💾 Exporting results...")
        generated_dir = 'generated'
        if not os.path.exists(generated_dir):
            os.makedirs(generated_dir)
        
        filepath = os.path.join(generated_dir, filename)
        rows = []
        
        for ct in differences['missing_types']['space1']:
            rows.append({
                'Difference Type': 'Missing Content Type',
                'Content Type': ct,
                'Field': '',
                'Property': '',
                'Space 1 Value': 'Missing',
                'Space 2 Value': 'Present',
                'Space 1 ID': self.space1_id,
                'Space 2 ID': self.space2_id
            })
        
        for ct in differences['missing_types']['space2']:
            rows.append({
                'Difference Type': 'Missing Content Type',
                'Content Type': ct,
                'Field': '',
                'Property': '',
                'Space 1 Value': 'Present',
                'Space 2 Value': 'Missing',
                'Space 1 ID': self.space1_id,
                'Space 2 ID': self.space2_id
            })
        
        for type_id, field_diffs in differences['field_differences'].items():
            for field in field_diffs['missing_in_space1']:
                rows.append({
                    'Difference Type': 'Missing Field',
                    'Content Type': type_id,
                    'Field': field,
                    'Property': '',
                    'Space 1 Value': 'Missing',
                    'Space 2 Value': 'Present',
                    'Space 1 ID': self.space1_id,
                    'Space 2 ID': self.space2_id
                })
            
            for field in field_diffs['missing_in_space2']:
                rows.append({
                    'Difference Type': 'Missing Field',
                    'Content Type': type_id,
                    'Field': field,
                    'Property': '',
                    'Space 1 Value': 'Present',
                    'Space 2 Value': 'Missing',
                    'Space 1 ID': self.space1_id,
                    'Space 2 ID': self.space2_id
                })
        
        for type_id, fields in differences['definition_differences'].items():
            for field_id, defs in fields.items():
                def1 = defs['space1']
                def2 = defs['space2']
                
                all_keys = set(def1.keys()) | set(def2.keys())
                for key in all_keys:
                    val1 = def1.get(key)
                    val2 = def2.get(key)
                    if val1 != val2:
                        val1_str = json.dumps(val1) if isinstance(val1, (dict, list)) else str(val1)
                        val2_str = json.dumps(val2) if isinstance(val2, (dict, list)) else str(val2)
                        
                        rows.append({
                            'Difference Type': 'Field Definition',
                            'Content Type': type_id,
                            'Field': field_id,
                            'Property': key,
                            'Space 1 Value': val1_str,
                            'Space 2 Value': val2_str,
                            'Space 1 ID': self.space1_id,
                            'Space 2 ID': self.space2_id
                        })
        
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
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['Difference Type', 'Content Type', 'Field', 'Property', 
                             'Space 1 Value', 'Space 2 Value', 'Space 1 ID', 'Space 2 ID']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            
            print(f"\n✅ No differences found! Empty CSV created: {filepath}")
        
        return filepath


