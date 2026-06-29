"""
File Storage Backend for Cache AI
Persists data to JSON files so it survives between CLI runs
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileStorage:
    """Store cache data in JSON files"""
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize file storage
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        self.sessions_file = os.path.join(data_dir, 'sessions.json')
        self.interactions_file = os.path.join(data_dir, 'interactions.json')
        self.cache_file = os.path.join(data_dir, 'cache.json')
        
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self) -> None:
        """Initialize JSON files if they don't exist"""
        for file_path in [self.sessions_file, self.interactions_file, self.cache_file]:
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump({}, f, indent=2)
                logger.info(f"Created {file_path}")
    
    def save_session(self, session_id: str, session_data: Dict[str, Any]) -> None:
        """Save session to file"""
        try:
            sessions = self._load_file(self.sessions_file)
            sessions[session_id] = session_data
            self._save_file(self.sessions_file, sessions)
            logger.info(f"Saved session: {session_id}")
        except Exception as e:
            logger.error(f"Error saving session: {str(e)}")
    
    def load_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Load session from file"""
        try:
            sessions = self._load_file(self.sessions_file)
            return sessions.get(session_id)
        except Exception as e:
            logger.error(f"Error loading session: {str(e)}")
            return None
    
    def get_all_sessions(self) -> Dict[str, Any]:
        """Get all sessions"""
        try:
            return self._load_file(self.sessions_file)
        except Exception as e:
            logger.error(f"Error loading sessions: {str(e)}")
            return {}
    
    def save_interaction(self, interaction_id: str, interaction_data: Dict[str, Any]) -> None:
        """Save interaction to file"""
        try:
            interactions = self._load_file(self.interactions_file)
            interactions[interaction_id] = interaction_data
            self._save_file(self.interactions_file, interactions)
            logger.info(f"Saved interaction: {interaction_id}")
        except Exception as e:
            logger.error(f"Error saving interaction: {str(e)}")
    
    def load_interaction(self, interaction_id: str) -> Optional[Dict[str, Any]]:
        """Load interaction from file"""
        try:
            interactions = self._load_file(self.interactions_file)
            return interactions.get(interaction_id)
        except Exception as e:
            logger.error(f"Error loading interaction: {str(e)}")
            return None
    
    def get_all_interactions(self) -> Dict[str, Any]:
        """Get all interactions"""
        try:
            return self._load_file(self.interactions_file)
        except Exception as e:
            logger.error(f"Error loading interactions: {str(e)}")
            return {}
    
    def save_cache(self, cache_id: str, cache_data: Dict[str, Any]) -> None:
        """Save cache entry to file"""
        try:
            cache = self._load_file(self.cache_file)
            cache[cache_id] = cache_data
            self._save_file(self.cache_file, cache)
            logger.info(f"Saved cache: {cache_id}")
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")
    
    def load_cache(self, cache_id: str) -> Optional[Dict[str, Any]]:
        """Load cache entry from file"""
        try:
            cache = self._load_file(self.cache_file)
            return cache.get(cache_id)
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            return None
    
    def get_all_cache(self) -> Dict[str, Any]:
        """Get all cache entries"""
        try:
            return self._load_file(self.cache_file)
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            return {}
    
    def _load_file(self, file_path: str) -> Dict[str, Any]:
        """Load JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    
    def _save_file(self, file_path: str, data: Dict[str, Any]) -> None:
        """Save JSON file"""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def clear_all(self) -> None:
        """Clear all data"""
        for file_path in [self.sessions_file, self.interactions_file, self.cache_file]:
            self._save_file(file_path, {})
        logger.info("Cleared all data")
