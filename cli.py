#!/usr/bin/env python3
"""
Cache AI CLI - Command Line Interface
Usage: python cli.py [command] [options]
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional
from src.cache_service import CacheService
from src.analytics_engine import AnalyticsEngine
from src.cache_ai_rating import CacheAIRatingEngine


class CacheAICLI:
    """Command Line Interface for Cache AI"""
    
    def __init__(self):
        self.cache_service = CacheService()
        self.analytics = AnalyticsEngine(self.cache_service.storage)
        self.rating_engine = CacheAIRatingEngine()
    
    def create_session(self, user_id: str, repository: Optional[str] = None, 
                      branch: str = 'main', ai_provider: str = 'cache_ai') -> str:
        """Create a new session"""
        session_data = {
            'user_id': user_id,
            'repository': repository,
            'branch': branch,
            'ai_provider': ai_provider
        }
        session_id = self.cache_service.store_session(session_data)
        print(f"✅ Session created: {session_id}")
        return session_id
    
    def log_interaction(self, session_id: str, interaction_type: str, user_input: str, 
                       ai_response: str, tokens: int = 0, response_time: int = 0) -> str:
        """Log an interaction"""
        interaction_data = {
            'session_id': session_id,
            'type': interaction_type,
            'user_input': user_input,
            'ai_response': ai_response,
            'tokens_used': tokens,
            'response_time_ms': response_time
        }
        interaction_id = self.cache_service.log_interaction(interaction_data)
        print(f"✅ Interaction logged: {interaction_id}")
        return interaction_id
    
    def cache_pattern(self, pattern: str, response: str, ttl: int = 2592000) -> str:
        """Cache a code pattern"""
        cache_id = self.cache_service.cache_pattern(pattern, response, ttl)
        print(f"✅ Pattern cached: {cache_id}")
        return cache_id
    
    def get_session(self, session_id: str) -> None:
        """Get session details"""
        session = self.cache_service.get_session(session_id)
        if session:
            print(json.dumps(session, indent=2))
        else:
            print(f"❌ Session {session_id} not found")
    
    def list_sessions(self, user_id: Optional[str] = None, limit: int = 10) -> None:
        """List sessions"""
        sessions = self.cache_service.get_sessions(user_id, limit)
        if sessions:
            print(f"\n📋 Sessions ({len(sessions)} found):")
            for i, session in enumerate(sessions, 1):
                print(f"\n{i}. Session ID: {session['session_id']}")
                print(f"   User: {session['user_id']}")
                print(f"   Repository: {session.get('repository', 'N/A')}")
                print(f"   Interactions: {session['total_interactions']}")
                print(f"   Tokens: {session['total_tokens']}")
        else:
            print("❌ No sessions found")
    
    def get_stats(self) -> None:
        """Get cache statistics"""
        stats = self.cache_service.get_statistics()
        print("\n📊 Cache Statistics:")
        print(f"   Total Sessions: {stats['total_sessions']}")
        print(f"   Total Interactions: {stats['total_interactions']}")
        print(f"   Cache Entries: {stats['total_cache_entries']}")
        print(f"   Cache Hit Rate: {stats['cache_hit_rate']}")
        print(f"   Storage Items: {stats['storage_items']}")
    
    def analyze_performance(self, ai_provider: Optional[str] = None, 
                           period_days: int = 30) -> None:
        """Analyze AI performance"""
        metrics = self.analytics.analyze_ai_performance(ai_provider, period_days)
        print("\n📈 Performance Analysis:")
        print(json.dumps(metrics, indent=2))
    
    def compare_providers(self, providers: str, period_days: int = 30) -> None:
        """Compare multiple AI providers"""
        provider_list = [p.strip() for p in providers.split(',')]
        comparison = self.analytics.compare_ai_providers(provider_list, period_days)
        print("\n🔄 Provider Comparison:")
        print(json.dumps(comparison, indent=2))
    
    def get_top_patterns(self, limit: int = 10) -> None:
        """Get top code patterns"""
        patterns = self.analytics.get_top_patterns(limit)
        print(f"\n🎯 Top {limit} Code Patterns:")
        if patterns:
            for i, pattern in enumerate(patterns, 1):
                print(f"\n{i}. Pattern: {pattern['pattern'][:50]}...")
                print(f"   Hits: {pattern['hit_count']}")
        else:
            print("❌ No patterns found")
    
    def rate_cache_ai(self) -> None:
        """Get Cache AI rating"""
        report = self.rating_engine.generate_full_report()
        print("\n⭐ Cache AI Rating Report:")
        print(f"\n📊 Overall Score: {report['cache_ai_rating']['ratings']['overall']}/10")
        print("\n🏆 Rankings:")
        for item in report['vs_all_providers']['overall_rankings']:
            print(f"   {item['rank']}. {item['medal']} {item['provider'].upper()}: {item['overall_score']}/10")
        
        print("\n💪 Strengths:")
        for strength in report['strengths']['cache_ai_strengths'][:3]:
            print(f"   ✅ {strength['category']}: {strength['score']}/10")
        
        print("\n⚠️ Areas for Improvement:")
        for weakness in report['weaknesses']['cache_ai_weaknesses'][:3]:
            print(f"   📈 {weakness['category']}: {weakness['score']}/10 (need +{weakness['improvement_needed']})")
        
        print("\n💡 Recommendations:")
        for rec in report['recommendations'][:5]:
            print(f"   {rec}")
    
    def cache_ai_vs(self, provider: str) -> None:
        """Compare Cache AI vs specific provider"""
        comparison = self.rating_engine.get_cache_ai_vs_specific(provider)
        if 'error' in comparison:
            print(f"❌ {comparison['error']}")
            return
        
        print(f"\n⚔️ Cache AI vs {provider.upper()}:")
        print(f"\n   Overall: Cache AI {comparison['overall']['cache_ai']}/10 vs {provider} {comparison['overall']['opponent']}/10")
        print(f"   Winner: {comparison['overall']['winner'].upper()}")
        
        print("\n   Category Breakdown:")
        for category, scores in comparison['category_breakdown'].items():
            winner = "✅" if scores['winner'] == 'cache_ai' else "❌"
            diff = f"({scores['difference']:+.1f})" if scores['difference'] != 0 else "(tied)"
            print(f"   {winner} {category}: Cache AI {scores['cache_ai']} vs {provider} {scores[provider]} {diff}")
    
    def export_session(self, session_id: str, format: str = 'json') -> None:
        """Export session data"""
        try:
            data = self.cache_service.export_session(session_id, format)
            print(data)
        except ValueError as e:
            print(f"❌ {str(e)}")
    
    def help(self) -> None:
        """Show help message"""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    Cache AI - CLI Usage                      ║
╚══════════════════════════════════════════════════════════════╝

📌 SESSION COMMANDS:
  create-session          Create a new session
    --user-id USER       User ID (required)
    --repo REPO          Repository name (optional)
    --branch BRANCH      Branch name (default: main)
    --provider PROVIDER  AI provider (default: cache_ai)
  
  log-interaction         Log an AI interaction
    --session-id ID      Session ID (required)
    --type TYPE          Interaction type: code_generation, debugging, etc
    --input INPUT        User input/prompt
    --response RESPONSE  AI response
    --tokens TOKENS      Tokens used (optional)
    --time TIME          Response time in ms (optional)
  
  get-session            Get session details
    --session-id ID      Session ID (required)
  
  list-sessions          List all sessions
    --user-id USER       Filter by user (optional)
    --limit N            Max results (default: 10)
  
  export-session         Export session as JSON
    --session-id ID      Session ID (required)

📊 CACHE COMMANDS:
  cache-pattern          Cache a code pattern
    --pattern CODE       Code pattern (required)
    --response RESPONSE  Cached response (required)
    --ttl SECONDS        Time to live (default: 30 days)

📈 ANALYTICS COMMANDS:
  stats                  Show cache statistics
  
  analyze                Analyze AI performance
    --provider PROVIDER  AI provider (optional)
    --period DAYS        Period in days (default: 30)
  
  compare                Compare multiple providers
    --providers P1,P2,P3 Comma-separated provider list
    --period DAYS        Period in days (default: 30)
  
  top-patterns           Show most used code patterns
    --limit N            Max results (default: 10)

⭐ RATING COMMANDS:
  rate                   Get Cache AI rating report
  
  vs                     Compare Cache AI vs provider
    --provider PROVIDER  Provider name (cursor, copilot, chatgpt, claude, codex)

EXAMPLES:
  # Create a session
  python cli.py create-session --user-id john_doe --repo my-project

  # Log an interaction
  python cli.py log-interaction --session-id abc123 --type code_generation \\
    --input "Create a React component" --response "import React..." --tokens 150

  # Get Cache AI rating
  python cli.py rate

  # Compare Cache AI vs Cursor
  python cli.py vs --provider cursor

  # Show statistics
  python cli.py stats

  # List all sessions
  python cli.py list-sessions

  # Analyze performance
  python cli.py analyze --provider cache_ai --period 30

  # Compare providers
  python cli.py compare --providers cursor,copilot,chatgpt --period 30

  # Get top patterns
  python cli.py top-patterns --limit 5

  # Export session
  python cli.py export-session --session-id abc123

"""
        print(help_text)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Cache AI - AI Cache Database CLI',
        add_help=False
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Session commands
    create_session_parser = subparsers.add_parser('create-session', help='Create a new session')
    create_session_parser.add_argument('--user-id', required=True, help='User ID')
    create_session_parser.add_argument('--repo', help='Repository name')
    create_session_parser.add_argument('--branch', default='main', help='Branch name')
    create_session_parser.add_argument('--provider', default='cache_ai', help='AI provider')
    
    log_interaction_parser = subparsers.add_parser('log-interaction', help='Log an interaction')
    log_interaction_parser.add_argument('--session-id', required=True, help='Session ID')
    log_interaction_parser.add_argument('--type', required=True, help='Interaction type')
    log_interaction_parser.add_argument('--input', required=True, help='User input')
    log_interaction_parser.add_argument('--response', required=True, help='AI response')
    log_interaction_parser.add_argument('--tokens', type=int, default=0, help='Tokens used')
    log_interaction_parser.add_argument('--time', type=int, default=0, help='Response time (ms)')
    
    get_session_parser = subparsers.add_parser('get-session', help='Get session details')
    get_session_parser.add_argument('--session-id', required=True, help='Session ID')
    
    list_sessions_parser = subparsers.add_parser('list-sessions', help='List sessions')
    list_sessions_parser.add_argument('--user-id', help='User ID')
    list_sessions_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    export_session_parser = subparsers.add_parser('export-session', help='Export session')
    export_session_parser.add_argument('--session-id', required=True, help='Session ID')
    
    # Cache commands
    cache_pattern_parser = subparsers.add_parser('cache-pattern', help='Cache a pattern')
    cache_pattern_parser.add_argument('--pattern', required=True, help='Code pattern')
    cache_pattern_parser.add_argument('--response', required=True, help='Cached response')
    cache_pattern_parser.add_argument('--ttl', type=int, default=2592000, help='Time to live')
    
    # Analytics commands
    subparsers.add_parser('stats', help='Show statistics')
    
    analyze_parser = subparsers.add_parser('analyze', help='Analyze performance')
    analyze_parser.add_argument('--provider', help='AI provider')
    analyze_parser.add_argument('--period', type=int, default=30, help='Period (days)')
    
    compare_parser = subparsers.add_parser('compare', help='Compare providers')
    compare_parser.add_argument('--providers', required=True, help='Comma-separated providers')
    compare_parser.add_argument('--period', type=int, default=30, help='Period (days)')
    
    top_patterns_parser = subparsers.add_parser('top-patterns', help='Show top patterns')
    top_patterns_parser.add_argument('--limit', type=int, default=10, help='Max results')
    
    # Rating commands
    subparsers.add_parser('rate', help='Get Cache AI rating')
    
    vs_parser = subparsers.add_parser('vs', help='Compare vs provider')
    vs_parser.add_argument('--provider', required=True, help='Provider name')
    
    subparsers.add_parser('help', help='Show help')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command or args.command == 'help':
        cli = CacheAICLI()
        cli.help()
        return
    
    cli = CacheAICLI()
    
    try:
        if args.command == 'create-session':
            cli.create_session(args.user_id, args.repo, args.branch, args.provider)
        
        elif args.command == 'log-interaction':
            cli.log_interaction(args.session_id, args.type, args.input, args.response, args.tokens, args.time)
        
        elif args.command == 'get-session':
            cli.get_session(args.session_id)
        
        elif args.command == 'list-sessions':
            cli.list_sessions(args.user_id, args.limit)
        
        elif args.command == 'export-session':
            cli.export_session(args.session_id)
        
        elif args.command == 'cache-pattern':
            cli.cache_pattern(args.pattern, args.response, args.ttl)
        
        elif args.command == 'stats':
            cli.get_stats()
        
        elif args.command == 'analyze':
            cli.analyze_performance(args.provider, args.period)
        
        elif args.command == 'compare':
            cli.compare_providers(args.providers, args.period)
        
        elif args.command == 'top-patterns':
            cli.get_top_patterns(args.limit)
        
        elif args.command == 'rate':
            cli.rate_cache_ai()
        
        elif args.command == 'vs':
            cli.cache_ai_vs(args.provider)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()
