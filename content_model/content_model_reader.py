#!/usr/bin/env python3
"""
ContentfulModelReader - A class for reading content models from Contentful spaces.

This module provides functionality to:
- Connect to Contentful Management API
- Fetch content types from specified spaces and environments
- Handle authentication and error management
"""

import contentful_management
from typing import List, Any


class ContentfulModelReader:

    def __init__(self, space_id: str, environment_id: str, management_token: str):
        self.space_id = space_id
        self.environment_id = environment_id
        self.management_token = management_token
        self.client = contentful_management.Client(management_token)
    
    def fetch_content_model(self) -> List[Any]:
        try:
            space = self.client.spaces().find(self.space_id)
            environment = space.environments().find(self.environment_id)
            content_types = environment.content_types().all()
            
            print(f"✅ Fetched {len(content_types)} content types from {self.space_id}/{self.environment_id}")
            
            return content_types
            
        except Exception as e:
            print(f"❌ Error fetching content model from {self.space_id}/{self.environment_id}: {str(e)}")
            raise
