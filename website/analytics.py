"""
🔍 Analytics and Usage Tracking for Omics Oracle
Track who's using the demo and what they're searching for
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional
import hashlib
import os

class UsageTracker:
    def __init__(self, db_path: str = "usage_analytics.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize the analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                user_hash TEXT,
                query_text TEXT,
                query_type TEXT,
                targets_found INTEGER,
                session_id TEXT,
                ip_hash TEXT,
                processing_time_seconds REAL,
                success BOOLEAN,
                error_message TEXT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date DATE PRIMARY KEY,
                total_queries INTEGER DEFAULT 0,
                unique_users INTEGER DEFAULT 0,
                avg_processing_time REAL DEFAULT 0,
                success_rate REAL DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def track_query(self, 
                   query: str, 
                   query_type: str, 
                   targets_found: int,
                   processing_time: float,
                   success: bool,
                   error_message: Optional[str] = None,
                   user_id: Optional[str] = None,
                   session_id: Optional[str] = None,
                   ip_address: Optional[str] = None):
        """Track a user query with privacy-safe hashing"""
        
        # Create privacy-safe hashes
        user_hash = self._hash_user_id(user_id) if user_id else "anonymous"
        ip_hash = self._hash_ip(ip_address) if ip_address else "unknown"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO queries 
            (user_hash, query_text, query_type, targets_found, session_id, 
             ip_hash, processing_time_seconds, success, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_hash, query[:500], query_type, targets_found, session_id,
              ip_hash, processing_time, success, error_message))
        
        conn.commit()
        conn.close()
        
        # Update daily stats
        self._update_daily_stats()
    
    def _hash_user_id(self, user_id: str) -> str:
        """Create privacy-safe hash of user identifier"""
        return hashlib.sha256(f"user_{user_id}".encode()).hexdigest()[:16]
    
    def _hash_ip(self, ip: str) -> str:
        """Create privacy-safe hash of IP address"""
        return hashlib.sha256(f"ip_{ip}".encode()).hexdigest()[:16]
    
    def _update_daily_stats(self):
        """Update daily aggregated statistics"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate today's stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_queries,
                COUNT(DISTINCT user_hash) as unique_users,
                AVG(processing_time_seconds) as avg_time,
                AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) as success_rate
            FROM queries 
            WHERE DATE(timestamp) = ?
        """, (today,))
        
        stats = cursor.fetchone()
        
        cursor.execute("""
            INSERT OR REPLACE INTO daily_stats 
            (date, total_queries, unique_users, avg_processing_time, success_rate)
            VALUES (?, ?, ?, ?, ?)
        """, (today, stats[0], stats[1], stats[2] or 0, stats[3] or 0))
        
        conn.commit()
        conn.close()
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total stats
        cursor.execute("SELECT COUNT(*) FROM queries")
        total_queries = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(DISTINCT user_hash) FROM queries")
        total_users = cursor.fetchone()[0]
        
        # Recent activity (last 7 days)
        cursor.execute("""
            SELECT COUNT(*) FROM queries 
            WHERE timestamp >= datetime('now', '-7 days')
        """)
        recent_queries = cursor.fetchone()[0]
        
        # Popular query types
        cursor.execute("""
            SELECT query_type, COUNT(*) as count
            FROM queries 
            GROUP BY query_type 
            ORDER BY count DESC
            LIMIT 5
        """)
        popular_types = cursor.fetchall()
        
        # Success rate
        cursor.execute("""
            SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) * 100
            FROM queries
        """)
        success_rate = cursor.fetchone()[0] or 0
        
        # Top query patterns (first 50 chars)
        cursor.execute("""
            SELECT SUBSTR(query_text, 1, 50) as query_preview, COUNT(*) as count
            FROM queries 
            WHERE success = 1
            GROUP BY SUBSTR(query_text, 1, 50)
            ORDER BY count DESC
            LIMIT 10
        """)
        popular_queries = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_queries": total_queries,
            "total_users": total_users,
            "recent_queries_7d": recent_queries,
            "success_rate_percent": round(success_rate, 1),
            "popular_query_types": popular_types,
            "popular_queries": popular_queries
        }
    
    def get_daily_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get daily usage trends"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT date, total_queries, unique_users, success_rate
            FROM daily_stats 
            WHERE date >= date('now', '-{} days')
            ORDER BY date DESC
        """.format(days))
        
        trends = cursor.fetchall()
        conn.close()
        
        return {
            "daily_data": trends,
            "total_days": len(trends)
        }
