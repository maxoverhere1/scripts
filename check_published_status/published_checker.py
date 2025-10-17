#!/usr/bin/env python3
"""
PublishedChecker - A class for checking the published status of Contentful entries.

This module provides functionality to:
- Connect to Contentful Delivery API
- Check if specific page entries are published
- Generate CSV reports for published and unpublished entries
"""

from contentful_management import Client
import os
import csv
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv


class PublishedChecker:

    def __init__(self, space_id_env: str, environment_id_env: str, management_token_env: str):
        load_dotenv('.env')
        self.space_id = os.getenv(space_id_env)
        self.environment_id = os.getenv(environment_id_env)
        self.management_token = os.getenv(management_token_env)
        
        # Initialize Contentful Management API client
        self.client = Client(self.management_token)
        self.space = self.client.spaces().find(self.space_id)
        self.environment = self.space.environments().find(self.environment_id)
    
    def read_page_ids(self, filename: str) -> List[str]:
        """Read page IDs from a text file"""
        try:
            with open(filename, 'r') as f:
                # Strip whitespace and filter empty lines
                page_ids = [line.strip() for line in f if line.strip()]
            print(f"✅ Read {len(page_ids)} page IDs from {filename}")
            return page_ids
        except Exception as e:
            print(f"❌ Error reading file {filename}: {str(e)}")
            raise
    
    def check_page_status(self, page_id: str) -> Optional[Dict[str, str]]:
        """Check if a page is published and get its slug"""
        try:
            # Fetch the entry using Management API (can see unpublished entries)
            entry = self.environment.entries().find(page_id)
            
            # Get slug from fields - Management API returns fields as a dict
            entry_json = entry.to_json()
            fields = entry_json.get('fields', {})
            slug = 'N/A'
            
            # Try to get slug field (it's typically in the 'en-US' locale)
            if 'slug' in fields:
                slug_data = fields['slug']
                # Management API returns fields as {'locale': 'value'}
                if isinstance(slug_data, dict):
                    slug = slug_data.get('en-US') or slug_data.get('en') or next(iter(slug_data.values()), 'N/A')
                else:
                    slug = slug_data or 'N/A'
            
            # Check if published using sys metadata
            try:
                published_version = entry.published_version
                is_published = published_version is not None and published_version > 0
            except AttributeError:
                # Some entries might not have published_version attribute
                # Check if it's in the sys data directly
                sys_data = entry.to_json().get('sys', {})
                published_version = sys_data.get('publishedVersion')
                is_published = published_version is not None and published_version > 0
            
            return {
                'page_id': page_id,
                'slug': slug,
                'published': is_published
            }
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error: {error_msg}")
            return {
                'page_id': page_id,
                'slug': 'NOT_FOUND',
                'published': False,
                'error': error_msg
            }
    
    def check_all_pages(self, page_ids: List[str]) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """Check all pages and separate into published and unpublished lists"""
        published = []
        unpublished = []
        
        print("\n=== Checking page status ===")
        for i, page_id in enumerate(page_ids, 1):
            print(f"  [{i}/{len(page_ids)}] Checking {page_id}...", end=' ')
            
            result = self.check_page_status(page_id)
            
            if result:
                if result['published']:
                    published.append({
                        'page_id': result['page_id'],
                        'slug': result['slug']
                    })
                    print("✓ Published")
                else:
                    unpublished.append({
                        'page_id': result['page_id'],
                        'slug': result['slug']
                    })
                    print("✗ Unpublished")
        
        return published, unpublished
    
    def generate_csv_reports(self, published: List[Dict[str, str]], unpublished: List[Dict[str, str]]):
        """Generate CSV reports for published and unpublished pages"""
        generated_dir = 'generated'
        if not os.path.exists(generated_dir):
            os.makedirs(generated_dir)
        
        # Published pages CSV
        published_file = os.path.join(generated_dir, 'published_pages.csv')
        with open(published_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['page_id', 'slug']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for page in published:
                writer.writerow(page)
        
        print(f"\n✅ Published pages CSV: {published_file}")
        print(f"   ({len(published)} pages)")
        
        # Unpublished pages CSV
        unpublished_file = os.path.join(generated_dir, 'unpublished_pages.csv')
        with open(unpublished_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['page_id', 'slug']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for page in unpublished:
                writer.writerow(page)
        
        print(f"✅ Unpublished pages CSV: {unpublished_file}")
        print(f"   ({len(unpublished)} pages)")

