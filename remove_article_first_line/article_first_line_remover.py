#!/usr/bin/env python3
"""
ArticleFirstLineRemover - Remove the first heading/text from articles in Contentful.

This module provides functionality to:
- Read page IDs from the duplicate_titles.csv file
- Fetch the linked article for each page
- Remove the first text node from the article's RichText content
- Update the article in Contentful
"""

from contentful_management import Client
import os
import csv
import copy
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv


class ArticleFirstLineRemover:

    def __init__(self, space_id_env: str, environment_id_env: str, management_token_env: str):
        load_dotenv('.env')
        self.space_id = os.getenv(space_id_env)
        self.environment_id = os.getenv(environment_id_env)
        self.management_token = os.getenv(management_token_env)
        
        # Initialize Contentful Management API client
        self.client = Client(self.management_token)
        self.space = self.client.spaces().find(self.space_id)
        self.environment = self.space.environments().find(self.environment_id)
    
    def read_csv(self, filename: str) -> List[Dict[str, str]]:
        """Read page IDs and slugs from CSV file"""
        try:
            pages = []
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    pages.append({
                        'slug': row['slug'],
                        'page_id': row['page_id'],
                        'title': row.get('title', '')
                    })
            print(f"✅ Read {len(pages)} pages from {filename}")
            return pages
        except Exception as e:
            print(f"❌ Error reading CSV {filename}: {str(e)}")
            raise
    
    def get_article_id_from_page(self, page_id: str) -> Optional[str]:
        """Get the linked article ID from a page entry"""
        try:
            page_entry = self.environment.entries().find(page_id)
            page_json = page_entry.to_json()
            fields = page_json.get('fields', {})
            
            # Get the content reference
            content_ref = fields.get('content', {})
            # Get the link from the first available locale
            content_link = content_ref.get('en-US') or content_ref.get('en') or next(iter(content_ref.values()), None)
            
            if content_link and isinstance(content_link, dict):
                article_id = content_link.get('sys', {}).get('id')
                return article_id
            
            return None
        except Exception as e:
            print(f"  ⚠️  Error fetching page {page_id}: {str(e)}")
            return None
    
    def remove_first_text_node(self, richtext_content: Dict[str, Any]) -> Dict[str, Any]:
        """Remove the first text content from a RichText field"""
        if not richtext_content or 'content' not in richtext_content:
            return richtext_content
        
        content_nodes = richtext_content.get('content', [])
        if not content_nodes:
            return richtext_content
        
        # Make a deep copy to avoid modifying the original
        new_richtext = copy.deepcopy(richtext_content)
        new_content = new_richtext.get('content', [])
        
        # Find and remove the first node that contains text
        removed = False
        for i, node in enumerate(new_content):
            node_type = node.get('nodeType', '')
            
            # Check if this is a heading or paragraph with text
            if node_type in ['heading-1']:
                # Check if it has actual text content
                if self._has_text_content(node):
                    print(f"    Removing node type: {node_type}")
                    new_content.pop(i)
                    removed = True
                    break
        
        if not removed:
            print(f"    No text node found to remove")
            return richtext_content
        
        # Update the content in the new richtext structure
        new_richtext['content'] = new_content
        return new_richtext
    
    def _has_text_content(self, node: Dict[str, Any]) -> bool:
        """Check if a node contains actual text"""
        if 'content' not in node:
            return False
        
        for child in node['content']:
            if child.get('nodeType') == 'text' and child.get('value', '').strip():
                return True
            # Recursively check nested content
            if 'content' in child and self._has_text_content(child):
                return True
        
        return False
    
    def update_article(self, article_id: str, dry_run: bool = True) -> bool:
        """Update an article to remove the first text node"""
        try:
            # Fetch the article
            article_entry = self.environment.entries().find(article_id)
            article_json = article_entry.to_json()
            fields = article_json.get('fields', {})
            
            # Get the content field for all locales
            content_field = fields.get('content', {})
            if not content_field:
                print(f"    No content field found")
                return False
            
            # Track if we modified anything
            modified = False
            updated_content = {}
            
            # Process each locale
            for locale, richtext_content in content_field.items():
                if isinstance(richtext_content, dict) and 'nodeType' in richtext_content:
                    print(f"    Processing locale: {locale}")
                    new_content = self.remove_first_text_node(richtext_content)
                    
                    if new_content != richtext_content:
                        updated_content[locale] = new_content
                        modified = True
                    else:
                        # Keep the original content for this locale
                        updated_content[locale] = richtext_content
                else:
                    # Keep non-richtext content as-is
                    updated_content[locale] = richtext_content
            
            if modified and not dry_run:
                # Update using the SDK's proper field update mechanism
                try:
                    # Build the fields dict for update
                    updated_fields = article_entry.to_json().get('fields', {})
                    updated_fields['content'] = updated_content
                    
                    # Create attributes dict with all fields
                    attributes = {'fields': updated_fields}
                    
                    # Use the update method which properly handles field changes
                    article_entry.update(attributes)
                    
                    print(f"    ✅ Article updated and saved")
                    return True
                except Exception as save_error:
                    print(f"    ❌ Save error: {str(save_error)}")
                    print(f"    Details: {repr(save_error)}")
                    return False
            elif modified:
                print(f"    ℹ️  Would update article (dry run)")
                return True
            else:
                print(f"    No changes needed")
                return False
                
        except Exception as e:
            print(f"    ❌ Error updating article {article_id}: {str(e)}")
            return False
    
    def process_pages(self, pages: List[Dict[str, str]], dry_run: bool = True):
        """Process all pages and update their articles"""
        print(f"\n{'='*60}")
        print(f"Mode: {'DRY RUN (no changes will be saved)' if dry_run else 'LIVE MODE (changes will be saved)'}")
        print(f"{'='*60}\n")
        
        total = len(pages)
        updated = 0
        skipped = 0
        errors = 0
        
        for i, page in enumerate(pages, 1):
            page_id = page['page_id']
            slug = page['slug']
            title = page.get('title', 'N/A')
            
            print(f"[{i}/{total}] Processing: {slug}")
            print(f"  Page ID: {page_id}")
            print(f"  Title: {title}")
            
            # Get the article ID
            article_id = self.get_article_id_from_page(page_id)
            if not article_id:
                print(f"  ⚠️  No article found for this page")
                skipped += 1
                continue
            
            print(f"  Article ID: {article_id}")
            
            # Update the article
            success = self.update_article(article_id, dry_run)
            
            if success:
                updated += 1
            else:
                errors += 1
            
            print()
        
        # Summary
        print(f"\n{'='*60}")
        print(f"📊 Summary:")
        print(f"  Total pages: {total}")
        print(f"  Updated: {updated}")
        print(f"  Skipped: {skipped}")
        print(f"  Errors: {errors}")
        print(f"{'='*60}\n")

