"""
Updated Cache Service Module
Manages cache storage with FILE PERSISTENCE
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4
import logging
from src.file_storage import FileStorage

logger = logging.getLogger(__name__)


class CacheService:
    """Service for managing AI cache operations with persistent file storage"""
    
    def __init__(self, storage_backend=None, use_file_storage=True):
        """
        Initialize Cache Service
        
        Args:
            storage_backend: Backend for storage (memory, redis, database, file)
            use_file_storage: Use file-based persistence (default: True)
        """
        if use_file_storage:
            self.file_storage = FileStorage()
            self.storage = {}  # In-memory cache for quick access
        else:
            self.file_storage = None
            self.storage = storage_backend or {}
        
        self.cache_index = {}  # For fast lookups
        self._load_from_storage()
        
    def _load_from_storage(self) -> None:
        """Load all data from file storage on startup"""
        if self.file_storage:
            try:
                sessions = self.file_storage.get_all_sessions()
                interactions = self.file_storage.get_all_interactions()
                cache_entries = self.file_storage.get_all_cache()
                
                # Rebuild in-memory storage
                self.storage.update(sessions)
                self.storage.update(interactions)
                self.storage.update(cache_entries)
                
                # Rebuild cache index
                for cache_id, entry in cache_entries.items():
                    if 'pattern_hash' in entry:
                        self.cache_index[entry['pattern_hash']] = cache_id
                
                logger.info(f"Loaded {len(sessions)} sessions from storage")
            except Exception as e:
                logger.error(f"Error loading from storage: {str(e)}")
        
    def store_session(self, session_data: Dict[str, Any]) -> str:
        """
        Store a new AI session (PERSISTED)
        
        Args:
            session_data: Session metadata and details
            
        Returns:
            Session ID
        """
        session_id = str(uuid4())
        
        session = {
            'session_id': session_id,
            'user_id': session_data.get('user_id'),
            'start_time': session_data.get('start_time', datetime.now().isoformat()),
            'end_time': session_data.get('end_time'),
            'repository': session_data.get('repository'),
            'branch': session_data.get('branch', 'main'),
            'ai_provider': session_data.get('ai_provider', 'cache_ai'),
            'total_interactions': 0,
            'total_tokens': 0,
            'duration_seconds': session_data.get('duration_seconds'),
            'status': 'active',
            'metadata': session_data.get('metadata', {}),
            'interactions': []
        }
        
        self.storage[session_id] = session
        
        # Persist to file
        if self.file_storage:
            self.file_storage.save_session(session_id, session)
        
        logger.info(f"Session created and saved: {session_id}")
        return session_id
    
    def log_interaction(self, interaction_data: Dict[str, Any]) -> str:
        """
        Log an AI-user interaction (PERSISTED)
        
        Args:
            interaction_data: Interaction details
            
        Returns:
            Interaction ID
        """
        interaction_id = str(uuid4())
        session_id = interaction_data.get('session_id')
        
        if session_id not in self.storage:
            raise ValueError(f"Session {session_id} not found")
        
        interaction = {
            'interaction_id': interaction_id,
            'session_id': session_id,
            'timestamp': interaction_data.get('timestamp', datetime.now().isoformat()),
            'type': interaction_data.get('type'),
            'user_input': interaction_data.get('user_input'),
            'ai_response': interaction_data.get('ai_response'),
            'ai_provider': interaction_data.get('ai_provider', 'cache_ai'),
            'cache_hit': interaction_data.get('cache_hit', False),
            'tokens_used': interaction_data.get('tokens_used', 0),
            'response_time_ms': interaction_data.get('response_time_ms', 0),
            'model': interaction_data.get('model'),
            'success': interaction_data.get('success', True),
            'metadata': interaction_data.get('metadata', {})
        }
        
        # Add to session
        self.storage[session_id]['interactions'].append(interaction)
        self.storage[session_id]['total_interactions'] += 1
        self.storage[session_id]['total_tokens'] += interaction['tokens_used']
        
        # Persist to file
        if self.file_storage:
            self.file_storage.save_session(session_id, self.storage[session_id])
            self.file_storage.save_interaction(interaction_id, interaction)
        
        logger.info(f"Interaction logged and saved: {interaction_id}")
        return interaction_id
    
    def cache_pattern(self, pattern: str, response: str, ttl: int = 2592000) -> str:
        """
        Cache a code pattern and its response (PERSISTED)
        
        Args:
            pattern: Input pattern/prompt
            response: AI response
            ttl: Time to live in seconds (default 30 days)
            
        Returns:
            Cache ID
        """
        cache_id = str(uuid4())
        pattern_hash = hashlib.sha256(pattern.encode()).hexdigest()
        
        cache_entry = {
            'cache_id': cache_id,
            'pattern_hash': pattern_hash,
            'pattern': pattern,
            'cached_response': response,
            'hit_count': 0,
            'miss_count': 0,
            'last_hit': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat(),
            'ttl': ttl,
            'enabled': True
        }
        
        self.storage[cache_id] = cache_entry
        self.cache_index[pattern_hash] = cache_id
        
        # Persist to file
        if self.file_storage:
            self.file_storage.save_cache(cache_id, cache_entry)
        
        logger.info(f"Pattern cached and saved: {cache_id}")
        return cache_id
    
    def get_cache(self, pattern: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached response for a pattern
        
        Args:
            pattern: Pattern to search for
            
        Returns:
            Cache entry if found and valid, None otherwise
        """
        pattern_hash = hashlib.sha256(pattern.encode()).hexdigest()
        
        if pattern_hash not in self.cache_index:
            return None
        
        cache_id = self.cache_index[pattern_hash]
        cache_entry = self.storage.get(cache_id)
        
        if not cache_entry:
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(cache_entry['expires_at'])
        if datetime.now() > expires_at:
            self.delete_cache(cache_id)
            return None
        
        # Update hit count
        cache_entry['hit_count'] += 1
        cache_entry['last_hit'] = datetime.now().isoformat()
        
        # Persist update
        if self.file_storage:
            self.file_storage.save_cache(cache_id, cache_entry)
        
        logger.info(f"Cache hit: {cache_id}")
        return cache_entry
    
    def get_sessions(self, user_id: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve user sessions
        
        Args:
            user_id: Filter by user ID
            limit: Maximum number of sessions to return
            
        Returns:
            List of session objects
        """
        sessions = []
        for item in self.storage.values():
            if 'session_id' in item and 'user_id' in item and (user_id is None or item.get('user_id') == user_id):
                sessions.append(item)
        
        return sorted(sessions, key=lambda x: x['start_time'], reverse=True)[:limit]
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific session
        
        Args:
            session_id: Session ID
            
        Returns:
            Session object or None
        """
        return self.storage.get(session_id)
    
    def get_interactions(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve interactions from a session
        
        Args:
            session_id: Session ID
            
        Returns:
            List of interactions
        """
        session = self.storage.get(session_id)
        return session.get('interactions', []) if session else []
    
    def delete_cache(self, cache_id: str) -> bool:
        """
        Delete a cache entry
        
        Args:
            cache_id: Cache ID to delete
            
        Returns:
            True if successful
        """
        if cache_id in self.storage:
            entry = self.storage[cache_id]
            # Remove from index
            if 'pattern_hash' in entry:
                del self.cache_index[entry['pattern_hash']]
            del self.storage[cache_id]
            logger.info(f"Cache deleted: {cache_id}")
            return True
        return False
    
    def clear_expired_cache(self) -> int:
        """
        Remove all expired cache entries
        
        Returns:
            Number of entries deleted
        """
        now = datetime.now()
        expired_ids = []
        
        for cache_id, entry in self.storage.items():
            if 'expires_at' in entry:
                expires_at = datetime.fromisoformat(entry['expires_at'])
                if now > expires_at:
                    expired_ids.append(cache_id)
        
        for cache_id in expired_ids:
            self.delete_cache(cache_id)
        
        logger.info(f"Cleared {len(expired_ids)} expired cache entries")
        return len(expired_ids)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get cache and session statistics
        
        Returns:
            Statistics dictionary
        """
        total_sessions = sum(1 for item in self.storage.values() if 'session_id' in item and 'user_id' in item)
        total_interactions = sum(1 for item in self.storage.values() if 'interaction_id' in item)
        total_cache_entries = sum(1 for item in self.storage.values() if 'cache_id' in item)
        
        total_cache_hits = sum(item.get('hit_count', 0) for item in self.storage.values() if 'cache_id' in item)
        total_cache_requests = total_cache_hits + sum(item.get('miss_count', 0) for item in self.storage.values() if 'cache_id' in item)
        
        cache_hit_rate = (total_cache_hits / total_cache_requests * 100) if total_cache_requests > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'total_interactions': total_interactions,
            'total_cache_entries': total_cache_entries,
            'cache_hits': total_cache_hits,
            'cache_requests': total_cache_requests,
            'cache_hit_rate': f"{cache_hit_rate:.2f}%",
            'storage_items': len(self.storage)
        }
    
    def export_session(self, session_id: str, format: str = 'json') -> str:
        """
        Export session data
        
        Args:
            session_id: Session ID to export
            format: Export format ('json' or 'csv')
            
        Returns:
            Exported data as string
        """
        session = self.storage.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
        
        if format == 'json':
            return json.dumps(session, indent=2)
        
        raise ValueError(f"Unsupported export format: {format}")
