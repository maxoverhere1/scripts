#!/usr/bin/env python3
"""
ContentfulModelReader - A class for reading content models from Contentful spaces.

This module provides functionality to:
- Connect to Contentful Management API
- Fetch content types from specified spaces and environments
- Handle authentication and error management
"""

import contentful_management
import os
import json
from typing import List, Any
from dotenv import load_dotenv


class ContentfulModelReader:

    def __init__(self, space_id_env: str, environment_id_env: str):
        load_dotenv('.contentful.env')
        self.space_id = os.getenv(space_id_env)
        self.environment_id = os.getenv(environment_id_env)
        self.management_token = os.getenv('CONTENTFUL_MANAGEMENT_TOKEN')
        self.client = contentful_management.Client(self.management_token)
    
    def fetch_content_model(self) -> List[Any]:
        try:
            space = self.client.spaces().find(self.space_id)
            environment = space.environments().find(self.environment_id)
            content_types = environment.content_types().all()
            
            print(f"✅ Fetched {len(content_types)} content types from {self.space_id}/{self.environment_id}")
            
            self._auto_save_model(content_types)
            
            return content_types
            
        except Exception as e:
            print(f"❌ Error fetching content model from {self.space_id}/{self.environment_id}: {str(e)}")
            raise
    
    def _auto_save_model(self, model: List[Any]) -> str:
        generated_dir = 'generated'
        if not os.path.exists(generated_dir):
            os.makedirs(generated_dir)

        filename = f"content_model_{self.space_id}.json"
        filepath = os.path.join(generated_dir, filename)
        
        raw_data = []
        for content_type in model:
            if hasattr(content_type, 'raw'):
                raw_data.append(content_type.raw)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(raw_data, f, indent=2, ensure_ascii=False)
        
        print(f"Raw content model saved: {filepath}")
        return filepath
