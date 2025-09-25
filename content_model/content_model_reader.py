#!/usr/bin/env python3
"""
ContentfulModelReader - A class for reading content models from Contentful spaces.

This module provides functionality to:
- Connect to Contentful Management API
- Fetch content types from specified spaces and environments
- Handle authentication and error management
"""

from contentful_management import ContentType, Space, Client
import os
import json
from typing import List, Any, Dict, Optional
from dotenv import load_dotenv


class ContentfulModelReader:

    def __init__(self, space_id_env: str, environment_id_env: str):
        load_dotenv('.contentful.env')
        self.space_id = os.getenv(space_id_env)
        self.environment_id = os.getenv(environment_id_env)
        self.management_token = os.getenv('CONTENTFUL_MANAGEMENT_TOKEN')
        self.client: Client = Client(self.management_token)
    
    def fetch_content_model(self) -> List[ContentType]:
        try:
            space: Space = self.client.spaces().find(self.space_id)
            environment = space.environments().find(self.environment_id)
            content_types: List[ContentType] = environment.content_types().all()
            
            print(f"✅ Fetched {len(content_types)} content types from {self.space_id}/{self.environment_id}")
            
            self.save_model(content_types)
            
            return content_types
            
        except Exception as e:
            print(f"❌ Error fetching content model from {self.space_id}/{self.environment_id}: {str(e)}")
            raise
    
    def save_model(self, model: List[ContentType]) -> str:
        generated_dir: str = 'generated'
        if not os.path.exists(generated_dir):
            os.makedirs(generated_dir)

        filename: str = f"content_model_{self.space_id}_{self.environment_id}.json"
        filepath: str = os.path.join(generated_dir, filename)
        
        raw_data: List[Dict[str, Any]] = []
        for content_type in model:
            raw_data.append(content_type.raw)

        raw_data.sort(key=lambda ct: ct.get('name'))

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        
        print(f"Raw content model saved: {filepath}")
        return filepath
