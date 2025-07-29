import warnings
import os
import re
import logging
import hashlib
import time




from .utils_py.database import DatabaseManager
from .utils_py.embeddings import EmbeddingManager
from .utils_py.prompts import PromptManager
from .utils_py.auction import AuctionManager
from typing import List, Dict, Optional
import gc
import torch

class Garlic:
    def __init__(self, api_key: str):
        """Initialize RAG system with API key authentication
        
        Args:
            api_key: API key for authentication
        """
        if not api_key:
            raise ValueError("API key is required")
            
        try:
            # Clear memory before initialization
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            # Don't sanitize the API key - use it as is
            api_key = api_key.strip().strip('"\'')
            
            try:
                self.db = DatabaseManager()
                
                # Verify API key with rate limiting
                is_valid, self.key_id = self._verify_api_key_with_rate_limit(api_key)
                
                # Check if API key is valid
                if not is_valid:
                    raise ValueError("Invalid API key")
            except Exception as e:
                raise
            
            # Initialize with memory management
            self.embedding_manager = EmbeddingManager()
            self.prompt_manager = PromptManager()
            self.auction_manager = AuctionManager()
            
            # Load campaigns data if database is available
            if self.db:
                self.df = self.db.get_campaigns()
                # Check and update missing embeddings
                self._update_missing_embeddings()
                
                # Check if there are any active campaigns with bids
                has_active_campaigns_with_bids = self.db.check_active_campaigns_with_bids()
                if not has_active_campaigns_with_bids:
                    logging.warning("No active campaigns with bids found - ads will not be displayed")
            else:
                # Create empty dataframe for dev mode
                import pandas as pd
                self.df = pd.DataFrame(columns=['id', 'product_description', 'embedding'])
            
            # Log successful initialization
            logging.info(f"Garlic initialized successfully with key_id: {self.key_id}")
            
        except Exception as e:
            logging.error(f"Error initializing Garlic: {str(e)}")
            raise

    # def _sanitize_input(self, input_str: str) -> str:
    #     """Sanitize input to prevent injection attacks"""
    #     # Remove any potentially dangerous characters
    #     return re.sub(r'[^\w\-\.]', '', input_str)

    def _verify_api_key_with_rate_limit(self, api_key: str) -> tuple:
        """Verify API key with rate limiting"""
        try:
            # Basic rate limiting check
            result = self.db.verify_api_key(api_key)
            
            # Add logging for security auditing
            if result[0]:
                logging.info(f"Successful API key verification for key_id: {result[1]}")
                
            return result
        except Exception as e:
            logging.error(f"Error in API key verification: {str(e)}")
            return False, None

    def _update_missing_embeddings(self):
        """Check and update any missing embeddings in campaigns"""
        try:
            # Filter campaigns with missing embeddings
            missing_embeddings = self.df[self.df['embedding'].isna() & self.df['product_description'].notna()]
            
            if not missing_embeddings.empty:
                # Process each campaign with missing embedding
                for idx, campaign in missing_embeddings.iterrows():
                    description = campaign['product_description']
                    if description and isinstance(description, str):
                        # Create embedding for the description
                        embedding = self.embedding_manager.create_single_embedding(description)
                        
                        if len(embedding) > 0:
                            # Update the embedding in the database
                            self.db.update_campaign_embedding(campaign['id'], embedding.tolist())
                            
                            # Update the dataframe in memory
                            self.df.at[idx, 'embedding'] = embedding.tolist()
        
        except Exception as e:
            # Remove print statement
            pass

    def find_similar_campaigns(self, query: str, top_k: int = 5) -> List[dict]:
        """Find campaigns similar to the query"""
        try:
            query_embedding = self.embedding_manager.embed_query(query)
            
            if len(query_embedding) == 0:
                return []
            
            query_embedding = query_embedding.tolist()
            
            # Use campaign search instead of companies
            results = self.db.search_similar_campaigns(query_embedding, top_k)
            
            return results
            
        except Exception as e:
            # Remove print statement
            return []

    def generate_response(self, query: str, chat_history: Optional[List] = None) -> str:
        """Generate ad response based on context and bids"""
        try:
            # Log API call with proper error handling
            try:
                self.db.log_api_call(self.key_id, 'generate')
            except Exception as e:
                # Remove error logging
                pass
            
            # Get candidate campaigns - use the simpler approach from core_edit.py
            candidates = self.find_similar_campaigns(query)
            # Remove logging
            
            if not candidates:
                # Remove logging
                return ""
                
            # Get campaign bids - use the exact same approach as core_edit.py
            campaign_ids = [c['id'] for c in candidates]
            campaign_bids = self.db.get_campaign_bids(campaign_ids)
            
            # Select ad through auction mechanism
            selected_campaigns = self.auction_manager.select_ad(candidates, campaign_bids)
            # Remove logging
            
            # Format response and increment views
            if selected_campaigns:
                ad_response = self.prompt_manager.format_prompt(
                    query, 
                    selected_campaigns, 
                    self.df  # Pass campaigns DataFrame for user info
                )
                
                # Increment views for selected campaign
                try:
                    self.db.increment_campaign_views(selected_campaigns)
                except Exception as e:
                    # Remove error logging
                    pass
                
                return ad_response
            else:
                # Remove logging
                pass
            
            return ""

        except Exception as e:
            # Remove error logging
            try:
                self.db.log_api_call(self.key_id, 'generate', 'error')
            except:
                pass
            return ""

    def parse_response(self, response: Dict) -> Dict:
        """Parse the response into a clean format"""
        return {
            "query": response.get("query"),
            "response": response.get("response", ""),
            "recommendation": response.get("recommendation", ""),
            "companies": response.get("companies", [])
        }