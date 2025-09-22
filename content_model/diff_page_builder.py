#!/usr/bin/env python3
"""
DiffPageBuilder - A class for creating HTML diff pages of Contentful content models.

This module provides functionality to:
- Compare content models from two JSON files
- Generate HTML diff pages with visual highlighting
- Match elements by name for accurate comparison
- Export results to HTML files
"""

import json
import os
from typing import Dict, List, Any, Set, Tuple
from datetime import datetime
from contentful_management import ContentType


class DiffPageBuilder:
    
    def __init__(self, model1: List[ContentType], model2: List[ContentType], space1_id: str, space2_id: str):
        self.model1: List[ContentType] = model1
        self.model2: List[ContentType] = model2
        self.space1_id: str = space1_id
        self.space2_id: str = space2_id
    
    def create_html_diff(self) -> str:
        """Create HTML diff page and return the file path."""
        print("\n🎨 Building HTML diff page...")
        
        # Create dictionaries for easier lookup by name
        types1: Dict[str, ContentType] = {ct.name: ct for ct in self.model1}
        types2: Dict[str, ContentType] = {ct.name: ct for ct in self.model2}
        
        names1 = set(types1.keys())
        names2 = set(types2.keys())
        
        # Find differences
        missing_in_space2 = names1 - names2
        missing_in_space1 = names2 - names1
        common_names = names1 & names2
        
        # Generate HTML
        html_content = self._generate_html_header()
        html_content += self._generate_summary_section(missing_in_space1, missing_in_space2, common_names)
        html_content += self._generate_content_types_section(types1, types2, missing_in_space1, missing_in_space2, common_names)
        html_content += self._generate_html_footer()
        
        # Save to file
        generated_dir = 'generated'
        if not os.path.exists(generated_dir):
            os.makedirs(generated_dir)
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"content_model_diff_{timestamp}.html"
        filepath = os.path.join(generated_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"HTML diff page created: {filepath}")
        return filepath
    
    def _generate_html_header(self) -> str:
        """Generate HTML header with CSS styles."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Model Diff: {self.space1_id} vs {self.space2_id}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e9ecef;
        }}
        h2 {{
            color: #495057;
            margin-top: 40px;
            margin-bottom: 20px;
            padding-left: 10px;
            border-left: 4px solid #007bff;
        }}
        h3 {{
            color: #6c757d;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        .summary {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            margin-bottom: 30px;
        }}
        .summary-item {{
            margin: 10px 0;
            padding: 8px 12px;
            border-radius: 4px;
        }}
        .added {{
            background-color: #d4edda;
            color: #155724;
            border-left: 4px solid #28a745;
        }}
        .removed {{
            background-color: #f8d7da;
            color: #721c24;
            border-left: 4px solid #dc3545;
        }}
        .modified {{
            background-color: #fff3cd;
            color: #856404;
            border-left: 4px solid #ffc107;
        }}
        .unchanged {{
            background-color: #e9ecef;
            color: #495057;
            border-left: 4px solid #6c757d;
        }}
        .content-type {{
            margin: 20px 0;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            overflow: hidden;
        }}
        .content-type-header {{
            padding: 15px 20px;
            font-weight: 600;
            font-size: 18px;
        }}
        .content-type-body {{
            padding: 20px;
        }}
        .field-comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 15px 0;
        }}
        .field-side {{
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 15px;
        }}
        .field-side h4 {{
            margin: 0 0 10px 0;
            color: #495057;
        }}
        .field-property {{
            margin: 5px 0;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 14px;
        }}
        .property-name {{
            font-weight: 600;
            color: #6f42c1;
        }}
        .property-value {{
            color: #28a745;
        }}
        .no-differences {{
            text-align: center;
            color: #28a745;
            font-size: 18px;
            margin: 40px 0;
            padding: 20px;
            background: #d4edda;
            border-radius: 6px;
        }}
        .space-label {{
            font-size: 14px;
            color: #6c757d;
            font-weight: normal;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Content Model Comparison</h1>
        <div style="text-align: center; margin-bottom: 30px;">
            <strong>Space 1:</strong> {self.space1_id} &nbsp;&nbsp;&nbsp; <strong>Space 2:</strong> {self.space2_id}
        </div>
"""
    
    def _generate_summary_section(self, missing_in_space1: Set[str], missing_in_space2: Set[str], common_names: Set[str]) -> str:
        """Generate summary section of the diff."""
        total_types = len(missing_in_space1) + len(missing_in_space2) + len(common_names)
        
        html = '<div class="summary">\n'
        html += '<h2>📊 Summary</h2>\n'
        html += f'<div class="summary-item unchanged">Total Content Types: {total_types}</div>\n'
        
        if missing_in_space2:
            html += f'<div class="summary-item removed">Missing in Space 2: {len(missing_in_space2)} types</div>\n'
        
        if missing_in_space1:
            html += f'<div class="summary-item added">Missing in Space 1: {len(missing_in_space1)} types</div>\n'
            
        html += f'<div class="summary-item unchanged">Common Types: {len(common_names)} types</div>\n'
        html += '</div>\n'
        
        return html
    
    def _generate_content_types_section(self, types1: Dict[str, Any], types2: Dict[str, Any], 
                                      missing_in_space1: Set[str], missing_in_space2: Set[str], 
                                      common_names: Set[str]) -> str:
        """Generate content types comparison section."""
        html = '<h2>📋 Content Types</h2>\n'
        
        # Missing in space 2 (only in space 1)
        if missing_in_space2:
            html += '<h3>❌ Missing in Space 2</h3>\n'
            for name in sorted(missing_in_space2):
                ct = types1[name]
                html += f'<div class="content-type">\n'
                html += f'<div class="content-type-header removed">{name}</div>\n'
                html += f'<div class="content-type-body">{self._format_content_type_details(ct)}</div>\n'
                html += '</div>\n'
        
        # Missing in space 1 (only in space 2)
        if missing_in_space1:
            html += '<h3>✅ Missing in Space 1</h3>\n'
            for name in sorted(missing_in_space1):
                ct = types2[name]
                html += f'<div class="content-type">\n'
                html += f'<div class="content-type-header added">{name}</div>\n'
                html += f'<div class="content-type-body">{self._format_content_type_details(ct)}</div>\n'
                html += '</div>\n'
        
        # Common types (compare fields)
        if common_names:
            html += '<h3>🔄 Common Types</h3>\n'
            for name in sorted(common_names):
                ct1 = types1[name]
                ct2 = types2[name]
                differences = self._compare_content_types(ct1, ct2)
                
                if differences:
                    html += f'<div class="content-type">\n'
                    html += f'<div class="content-type-header modified">{name} <span class="space-label">(has differences)</span></div>\n'
                    html += f'<div class="content-type-body">{differences}</div>\n'
                    html += '</div>\n'
                else:
                    html += f'<div class="content-type">\n'
                    html += f'<div class="content-type-header unchanged">{name} <span class="space-label">(identical)</span></div>\n'
                    html += '</div>\n'
        
        if not missing_in_space1 and not missing_in_space2 and not any(self._compare_content_types(types1[name], types2[name]) for name in common_names):
            html += '<div class="no-differences">🎉 No differences found! Content models are identical.</div>\n'
        
        return html
    
    def _format_content_type_details(self, content_type: Dict[str, Any]) -> str:
        """Format content type details for display."""
        html = f'<div class="field-property"><span class="property-name">ID:</span> <span class="property-value">{content_type.get("sys", {}).get("id", "")}</span></div>\n'
        if content_type.get('description'):
            html += f'<div class="field-property"><span class="property-name">Description:</span> <span class="property-value">{content_type.get("description")}</span></div>\n'
        html += f'<div class="field-property"><span class="property-name">Fields:</span> <span class="property-value">{len(content_type.get("fields", []))}</span></div>\n'
        return html
    
    def _compare_content_types(self, ct1: Dict[str, Any], ct2: Dict[str, Any]) -> str:
        """Compare two content types and return HTML showing differences."""
        fields1 = {f.get('id', ''): f for f in ct1.get('fields', [])}
        fields2 = {f.get('id', ''): f for f in ct2.get('fields', [])}
        
        field_ids1 = set(fields1.keys())
        field_ids2 = set(fields2.keys())
        
        missing_in_2 = field_ids1 - field_ids2
        missing_in_1 = field_ids2 - field_ids1
        common_fields = field_ids1 & field_ids2
        
        html = ''
        
        # Show missing fields
        if missing_in_2:
            html += f'<h4>Fields missing in Space 2:</h4>\n'
            for field_id in sorted(missing_in_2):
                field = fields1[field_id]
                html += f'<div class="removed" style="margin: 5px 0; padding: 8px;">{field.get("name", field_id)} ({field.get("type", "unknown")})</div>\n'
        
        if missing_in_1:
            html += f'<h4>Fields missing in Space 1:</h4>\n'
            for field_id in sorted(missing_in_1):
                field = fields2[field_id]
                html += f'<div class="added" style="margin: 5px 0; padding: 8px;">{field.get("name", field_id)} ({field.get("type", "unknown")})</div>\n'
        
        # Compare common fields
        modified_fields = []
        for field_id in common_fields:
            field1 = fields1[field_id]
            field2 = fields2[field_id]
            if self._fields_differ(field1, field2):
                modified_fields.append((field_id, field1, field2))
        
        if modified_fields:
            html += f'<h4>Modified fields:</h4>\n'
            for field_id, field1, field2 in modified_fields:
                html += f'<div class="field-comparison">\n'
                html += f'<div class="field-side">\n'
                html += f'<h4>Space 1: {field1.get("name", field_id)}</h4>\n'
                html += self._format_field_properties(field1)
                html += '</div>\n'
                html += f'<div class="field-side">\n'
                html += f'<h4>Space 2: {field2.get("name", field_id)}</h4>\n'
                html += self._format_field_properties(field2)
                html += '</div>\n'
                html += '</div>\n'
        
        return html
    
    def _fields_differ(self, field1: Dict[str, Any], field2: Dict[str, Any]) -> bool:
        """Check if two fields are different."""
        # Compare key properties
        props_to_compare = ['type', 'required', 'localized', 'disabled', 'omitted', 'name']
        
        for prop in props_to_compare:
            if field1.get(prop) != field2.get(prop):
                return True
                
        # Compare validations
        val1 = field1.get('validations', [])
        val2 = field2.get('validations', [])
        if val1 != val2:
            return True
            
        return False
    
    def _format_field_properties(self, field: Dict[str, Any]) -> str:
        """Format field properties for display."""
        html = ''
        html += f'<div class="field-property"><span class="property-name">Type:</span> <span class="property-value">{field.get("type", "")}</span></div>\n'
        html += f'<div class="field-property"><span class="property-name">Required:</span> <span class="property-value">{field.get("required", False)}</span></div>\n'
        html += f'<div class="field-property"><span class="property-name">Localized:</span> <span class="property-value">{field.get("localized", False)}</span></div>\n'
        
        if field.get('validations'):
            html += f'<div class="field-property"><span class="property-name">Validations:</span> <span class="property-value">{len(field.get("validations", []))}</span></div>\n'
            
        return html
    
    def _generate_html_footer(self) -> str:
        """Generate HTML footer."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
        <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center; color: #6c757d; font-size: 14px;">
            Generated on {timestamp}
        </div>
    </div>
</body>
</html>
"""
