"""
Analytics Engine Module
Analyze AI cache data and generate insights
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
from collections import Counter

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Engine for analyzing AI cache and session data"""
    
    def __init__(self, storage=None):
        """
        Initialize Analytics Engine
        
        Args:
            storage: Data storage backend
        """
        self.storage = storage or {}
    
    def analyze_ai_performance(self, ai_provider: str = None, period_days: int = 30) -> Dict[str, Any]:
        """
        Analyze AI performance metrics
        
        Args:
            ai_provider: Filter by AI provider (cursor, copilot, chatgpt, claude, etc.)
            period_days: Analysis period in days
            
        Returns:
            Performance metrics dictionary
        """
        cutoff_date = datetime.now() - timedelta(days=period_days)
        
        metrics = {
            'ai_provider': ai_provider,
            'period_days': period_days,
            'total_sessions': 0,
            'total_interactions': 0,
            'total_tokens': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_hit_rate': 0.0,
            'avg_response_time_ms': 0,
            'success_rate': 0.0,
            'avg_tokens_per_interaction': 0,
            'interaction_types': {},
            'average_accuracy': 0.0
        }
        
        response_times = []
        successful_interactions = 0
        total_interactions = 0
        
        for item in self.storage.values():
            if 'interaction_id' in item:  # It's an interaction
                if item.get('ai_provider') != ai_provider and ai_provider:
                    continue
                
                timestamp = datetime.fromisoformat(item.get('timestamp', datetime.now().isoformat()))
                if timestamp < cutoff_date:
                    continue
                
                total_interactions += 1
                metrics['total_interactions'] += 1
                
                if item.get('cache_hit'):
                    metrics['cache_hits'] += 1
                else:
                    metrics['cache_misses'] += 1
                
                tokens = item.get('tokens_used', 0)
                metrics['total_tokens'] += tokens
                
                response_time = item.get('response_time_ms', 0)
                response_times.append(response_time)
                
                if item.get('success', True):
                    successful_interactions += 1
                
                # Track interaction types
                interaction_type = item.get('type', 'unknown')
                metrics['interaction_types'][interaction_type] = metrics['interaction_types'].get(interaction_type, 0) + 1
        
        # Calculate derived metrics
        total_cache_requests = metrics['cache_hits'] + metrics['cache_misses']
        if total_cache_requests > 0:
            metrics['cache_hit_rate'] = metrics['cache_hits'] / total_cache_requests
        
        if response_times:
            metrics['avg_response_time_ms'] = sum(response_times) / len(response_times)
        
        if total_interactions > 0:
            metrics['success_rate'] = successful_interactions / total_interactions
            metrics['avg_tokens_per_interaction'] = metrics['total_tokens'] / total_interactions
        
        return metrics
    
    def compare_ai_providers(self, providers: List[str], period_days: int = 30) -> Dict[str, Any]:
        """
        Compare performance across multiple AI providers
        
        Args:
            providers: List of AI provider names
            period_days: Analysis period
            
        Returns:
            Comparison dictionary
        """
        comparison = {
            'providers': providers,
            'period_days': period_days,
            'comparison': {}
        }
        
        for provider in providers:
            comparison['comparison'][provider] = self.analyze_ai_performance(provider, period_days)
        
        return comparison
    
    def get_top_patterns(self, limit: int = 10, ai_provider: str = None) -> List[Dict[str, Any]]:
        """
        Get most used code patterns
        
        Args:
            limit: Maximum number of patterns
            ai_provider: Filter by AI provider
            
        Returns:
            List of top patterns
        """
        patterns = {}
        
        for item in self.storage.values():
            if 'pattern' in item:
                pattern = item.get('pattern', '')
                hit_count = item.get('hit_count', 0)
                
                if pattern not in patterns:
                    patterns[pattern] = {
                        'pattern': pattern,
                        'hit_count': hit_count,
                        'ai_provider': item.get('ai_provider'),
                        'created_at': item.get('created_at')
                    }
        
        sorted_patterns = sorted(patterns.values(), key=lambda x: x['hit_count'], reverse=True)
        return sorted_patterns[:limit]
    
    def analyze_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """
        Analyze specific user's AI usage patterns
        
        Args:
            user_id: User identifier
            
        Returns:
            User behavior analysis
        """
        behavior = {
            'user_id': user_id,
            'total_sessions': 0,
            'total_interactions': 0,
            'total_tokens_used': 0,
            'most_used_ai': None,
            'favorite_interaction_types': {},
            'average_session_duration': 0,
            'peak_usage_time': None
        }
        
        sessions = []
        for item in self.storage.values():
            if item.get('user_id') == user_id and 'session_id' in item:
                sessions.append(item)
                behavior['total_sessions'] += 1
                behavior['total_interactions'] += len(item.get('interactions', []))
        
        if sessions:
            total_duration = sum(s.get('duration_seconds', 0) for s in sessions)
            behavior['average_session_duration'] = total_duration / len(sessions) if sessions else 0
        
        return behavior
    
    def identify_ai_strengths(self, ai_provider: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Identify specific strengths of an AI provider
        
        Args:
            ai_provider: AI provider name
            period_days: Analysis period
            
        Returns:
            Strengths analysis
        """
        strengths = {
            'ai_provider': ai_provider,
            'code_generation': {'score': 0, 'accuracy': 0},
            'debugging': {'score': 0, 'success_rate': 0},
            'refactoring': {'score': 0, 'quality': 0},
            'documentation': {'score': 0, 'completeness': 0},
            'testing': {'score': 0, 'coverage': 0},
            'security': {'score': 0, 'vulnerabilities_found': 0},
            'performance': {'avg_response_time': 0, 'efficiency': 0},
            'cache_efficiency': {'hit_rate': 0, 'reuse_potential': 0}
        }
        
        return strengths
    
    def identify_ai_weaknesses(self, ai_provider: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Identify specific weaknesses of an AI provider
        
        Args:
            ai_provider: AI provider name
            period_days: Analysis period
            
        Returns:
            Weaknesses analysis
        """
        weaknesses = {
            'ai_provider': ai_provider,
            'error_rate': 0.0,
            'slow_response_times': [],
            'common_mistakes': [],
            'unsupported_features': [],
            'accuracy_issues': 0.0,
            'context_loss': 0.0
        }
        
        return weaknesses
    
    def cost_analysis(self, ai_provider: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Analyze cost efficiency of an AI provider
        
        Args:
            ai_provider: AI provider name
            period_days: Analysis period
            
        Returns:
            Cost analysis
        """
        # Provider pricing (example rates per 1M tokens)
        pricing = {
            'cursor': {'input': 3.00, 'output': 15.00},
            'copilot': {'monthly': 10.00},  # Fixed monthly
            'chatgpt': {'input': 0.50, 'output': 1.50},
            'claude': {'input': 3.00, 'output': 15.00},
            'gpt-4': {'input': 30.00, 'output': 60.00}
        }
        
        cost_analysis = {
            'ai_provider': ai_provider,
            'period_days': period_days,
            'total_tokens_used': 0,
            'total_cost_estimate': 0.0,
            'cost_per_session': 0.0,
            'cost_per_interaction': 0.0,
            'cost_efficiency_score': 0.0,
            'recommended_alternative': None
        }
        
        return cost_analysis
    
    def get_recommendations(self, ai_provider: str = None) -> List[str]:
        """
        Get optimization recommendations
        
        Args:
            ai_provider: Specific AI provider or None for general recommendations
            
        Returns:
            List of recommendations
        """
        recommendations = [
            "✅ Increase cache hit rate by storing common patterns",
            "✅ Use AI providers for their strengths (e.g., Claude for complex analysis)",
            "✅ Consider Cursor for faster local development",
            "✅ Use ChatGPT for cost-effective simple queries",
            "✅ Implement caching for frequently asked questions",
            "✅ Monitor response times and optimize slow queries",
            "✅ Rotate AI providers for load balancing",
            "✅ Track and reduce token usage for better cost efficiency"
        ]
        
        if ai_provider:
            recommendations = [r for r in recommendations if ai_provider.lower() in r.lower() or '✅' in r]
        
        return recommendations
    
    def generate_report(self, ai_provider: str = None, period_days: int = 30) -> Dict[str, Any]:
        """
        Generate comprehensive analysis report
        
        Args:
            ai_provider: AI provider name
            period_days: Analysis period
            
        Returns:
            Complete report
        """
        report = {
            'generated_at': datetime.now().isoformat(),
            'period_days': period_days,
            'performance_metrics': self.analyze_ai_performance(ai_provider, period_days),
            'top_patterns': self.get_top_patterns(5, ai_provider),
            'strengths': self.identify_ai_strengths(ai_provider, period_days),
            'weaknesses': self.identify_ai_weaknesses(ai_provider, period_days),
            'cost_analysis': self.cost_analysis(ai_provider, period_days),
            'recommendations': self.get_recommendations(ai_provider)
        }
        
        return report
