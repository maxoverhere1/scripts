#!/usr/bin/env python3
"""
PageTitleFinder - A class for finding pages with duplicate titles in Contentful.

This module provides functionality to:
- Connect to Contentful Delivery API
- Fetch all pages and their linked content
- Identify pages where the page heading matches the article's first text
- Generate a CSV report of matching pages
"""

import contentful
import os
import csv
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv


class PageTitleFinder:

    def __init__(self, space_id_env: str, environment_id_env: str, access_token_env: str):
        load_dotenv('.env')
        self.space_id = os.getenv(space_id_env)
        self.environment_id = os.getenv(environment_id_env)
        self.access_token = os.getenv(access_token_env)
        
        # Initialize Contentful client
        self.client = contentful.Client(
            self.space_id,
            self.access_token,
            environment=self.environment_id
        )
    
    def fetch_all_pages(self) -> List[Dict[str, Any]]:
        """Fetch all entries of content type 'page' as raw data"""
        try:
            pages = []
            skip = 0
            limit = 100
            
            while True:
                # Fetch without resolving any links to avoid recursion
                response = self.client.entries({
                    'content_type': 'page',
                    'include': 0,  # Don't resolve any references
                    'limit': limit,
                    'skip': skip
                })
                
                if not response:
                    break
                
                # Convert to raw dict to avoid SDK's lazy loading
                for entry in response:
                    pages.append({
                        'id': entry.sys.get('id'),
                        'fields': entry.raw.get('fields', {}),
                        'content_link_id': None
                    })
                
                if len(response) < limit:
                    break
                
                skip += limit
            
            print(f"✅ Fetched {len(pages)} pages from {self.space_id}/{self.environment_id}")
            return pages
            
        except Exception as e:
            print(f"❌ Error fetching pages: {str(e)}")
            raise
    
    def extract_first_text_from_richtext(self, richtext_content: Dict[str, Any]) -> Optional[str]:
        """Extract the first text content from a RichText field"""
        if not richtext_content or 'content' not in richtext_content:
            return None
        
        def get_first_text(nodes):
            """Recursively search for the first text node"""
            for node in nodes:
                # Check if this node has text value
                if node.get('nodeType') == 'text' and node.get('value'):
                    text = node.get('value', '').strip()
                    if text:
                        return text
                
                # Check if this node is a heading or paragraph with content
                if node.get('nodeType') in ['heading-1', 'heading-2', 'heading-3', 
                                            'heading-4', 'heading-5', 'heading-6', 
                                            'paragraph']:
                    if 'content' in node:
                        result = get_first_text(node['content'])
                        if result:
                            return result
                
                # Recursively search in content
                if 'content' in node:
                    result = get_first_text(node['content'])
                    if result:
                        return result
            
            return None
        
        return get_first_text(richtext_content['content'])
    
    def fetch_article_content(self, article_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a single article entry"""
        try:
            article = self.client.entry(article_id)
            return article.raw.get('fields', {})
        except Exception as e:
            print(f"  ⚠️  Error fetching article {article_id}: {str(e)}")
            return None
    
    def check_duplicate_titles(self, pages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Check which pages have titles matching their article's first text"""
        duplicates = []
        processed = 0
        skipped = 0
        
        for page in pages:
            try:
                page_id = page.get('id', '')
                fields = page.get('fields', {})
                
                # Get slug - might be direct string or in locale dict
                slug_data = fields.get('slug')
                if isinstance(slug_data, str):
                    slug = slug_data
                elif isinstance(slug_data, dict):
                    slug = slug_data.get('en-US') or slug_data.get('en') or next(iter(slug_data.values()), None)
                else:
                    slug = None
                
                if not slug:
                    skipped += 1
                    continue
                
                # Get heading - might be direct string or in locale dict
                heading_data = fields.get('heading')
                if isinstance(heading_data, str):
                    heading = heading_data
                elif isinstance(heading_data, dict):
                    heading = heading_data.get('en-US') or heading_data.get('en') or next(iter(heading_data.values()), None)
                else:
                    heading = None
                
                if not heading:
                    skipped += 1
                    continue
                
                # Get linked content reference
                content_ref = fields.get('content')
                if isinstance(content_ref, dict) and 'sys' in content_ref:
                    # Direct link object
                    content_link = content_ref
                elif isinstance(content_ref, dict):
                    # Localized link
                    content_link = content_ref.get('en-US') or content_ref.get('en') or next(iter(content_ref.values()), None)
                else:
                    content_link = None
                
                if not content_link or not isinstance(content_link, dict):
                    skipped += 1
                    continue
                
                # Extract the article ID from the link
                article_id = content_link.get('sys', {}).get('id')
                if not article_id:
                    skipped += 1
                    continue
                
                # Fetch the article to check its type and content
                article_fields = self.fetch_article_content(article_id)
                if not article_fields:
                    skipped += 1
                    continue
                
                # Get the article's content (RichText field)
                article_content_data = article_fields.get('content')
                # Handle different formats
                if isinstance(article_content_data, dict) and 'nodeType' in article_content_data:
                    # Direct RichText object
                    article_content = article_content_data
                elif isinstance(article_content_data, dict):
                    # Localized RichText
                    article_content = article_content_data.get('en-US') or article_content_data.get('en') or next(iter(article_content_data.values()), None)
                else:
                    article_content = None
                
                if not isinstance(article_content, dict):
                    skipped += 1
                    continue
                
                # Extract first text from article
                first_text = self.extract_first_text_from_richtext(article_content)
                
                if first_text and heading.strip().lower() == first_text.strip().lower():
                    duplicates.append({
                        'slug': slug,
                        'page_id': page_id,
                        'title': heading.strip()
                    })
                    print(f"  ✓ Found duplicate: {slug} - '{heading}'")
                
                processed += 1
                    
            except Exception as e:
                # Try to get slug for error message
                try:
                    slug_data = page.get('fields', {}).get('slug')
                    if isinstance(slug_data, str):
                        slug_name = slug_data
                    elif isinstance(slug_data, dict):
                        slug_name = slug_data.get('en-US') or slug_data.get('en') or 'unknown'
                    else:
                        slug_name = 'unknown'
                except:
                    slug_name = 'unknown'
                print(f"  ⚠️  Error processing page '{slug_name}': {str(e)}")
                skipped += 1
                continue
        
        print(f"\n  Processed: {processed} pages")
        print(f"  Skipped: {skipped} pages")
        
        return duplicates
    
    def generate_csv_report(self, duplicates: List[Dict[str, str]], filename: str = 'duplicate_titles.csv'):
        """Generate a CSV report of pages with duplicate titles"""
        generated_dir = 'generated'
        if not os.path.exists(generated_dir):
            os.makedirs(generated_dir)
        
        filepath = os.path.join(generated_dir, filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['slug', 'page_id', 'title']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for duplicate in duplicates:
                writer.writerow(duplicate)
        
        print(f"\n✅ CSV report generated: {filepath}")
        return filepath

