"""
Performance tracking system for chess analysis
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3
from pathlib import Path

@dataclass
class GamePerformance:
    username: str
    source: str
    game_date: str
    game_url: str
    color: str  # "white" or "black"
    result: str  # "1-0", "0-1", "1/2-1/2"
    accuracy: float
    blunders: int
    mistakes: int
    inaccuracies: int
    excellent_moves: int
    brilliant_moves: int
    opening_name: str
    opening_eco: str
    centipawn_loss: int
    game_length: int  # number of moves
    time_control: str
    rating: Optional[int] = None

@dataclass
class PerformanceStats:
    total_games: int
    avg_accuracy: float
    accuracy_trend: List[float]  # Last 10 games
    best_accuracy: float
    worst_accuracy: float
    blunder_rate: float
    improvement_score: float  # Trend-based improvement metric
    favorite_openings: List[Dict[str, Any]]
    performance_by_color: Dict[str, Dict[str, float]]
    recent_achievements: List[str]

class PerformanceTracker:
    def __init__(self, db_path: str = "backend/performance.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for performance tracking"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else ".", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create games table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                source TEXT NOT NULL,
                game_date TEXT NOT NULL,
                game_url TEXT,
                color TEXT NOT NULL,
                result TEXT NOT NULL,
                accuracy REAL NOT NULL,
                blunders INTEGER DEFAULT 0,
                mistakes INTEGER DEFAULT 0,
                inaccuracies INTEGER DEFAULT 0,
                excellent_moves INTEGER DEFAULT 0,
                brilliant_moves INTEGER DEFAULT 0,
                opening_name TEXT,
                opening_eco TEXT,
                centipawn_loss INTEGER DEFAULT 0,
                game_length INTEGER DEFAULT 0,
                time_control TEXT,
                rating INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create achievements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                achievement_type TEXT NOT NULL,
                achievement_title TEXT NOT NULL,
                achievement_description TEXT NOT NULL,
                earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                game_id INTEGER,
                FOREIGN KEY (game_id) REFERENCES games (id)
            )
        ''')
        
        # Create indices for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON games (username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_game_date ON games (game_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_opening_eco ON games (opening_eco)')
        
        conn.commit()
        conn.close()
    
    def record_game_performance(self, game_data: Dict[str, Any]) -> List[str]:
        """Record game performance and return any new achievements"""
        # Extract performance data from game analysis
        performance = self._extract_performance_data(game_data)
        
        # Store in database
        game_id = self._store_game_performance(performance)
        
        # Check for achievements
        achievements = self._check_achievements(performance, game_id)
        
        return achievements
    
    def get_user_stats(self, username: str, days: int = 30) -> PerformanceStats:
        """Get comprehensive performance statistics for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Get recent games
        cursor.execute('''
            SELECT * FROM games 
            WHERE username = ? AND game_date >= ? 
            ORDER BY game_date DESC
        ''', (username, start_date.isoformat()))
        
        games = cursor.fetchall()
        
        if not games:
            conn.close()
            return PerformanceStats(
                total_games=0,
                avg_accuracy=0.0,
                accuracy_trend=[],
                best_accuracy=0.0,
                worst_accuracy=0.0,
                blunder_rate=0.0,
                improvement_score=0.0,
                favorite_openings=[],
                performance_by_color={"white": {}, "black": {}},
                recent_achievements=[]
            )
        
        # Calculate statistics
        stats = self._calculate_stats(games, cursor, username)
        
        conn.close()
        return stats
    
    def get_opening_performance(self, username: str, opening_eco: str = None) -> Dict[str, Any]:
        """Get performance statistics for specific openings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if opening_eco:
            cursor.execute('''
                SELECT opening_name, opening_eco, color, result, accuracy, blunders
                FROM games 
                WHERE username = ? AND opening_eco = ?
                ORDER BY game_date DESC
            ''', (username, opening_eco))
        else:
            cursor.execute('''
                SELECT opening_name, opening_eco, color, result, accuracy, blunders,
                       COUNT(*) as game_count
                FROM games 
                WHERE username = ? AND opening_eco IS NOT NULL
                GROUP BY opening_eco
                ORDER BY game_count DESC
                LIMIT 10
            ''', (username,))
        
        results = cursor.fetchall()
        conn.close()
        
        return self._process_opening_stats(results, opening_eco is not None)
    
    def get_improvement_trends(self, username: str) -> Dict[str, Any]:
        """Get improvement trends over time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get monthly accuracy trends
        cursor.execute('''
            SELECT 
                strftime('%Y-%m', game_date) as month,
                AVG(accuracy) as avg_accuracy,
                COUNT(*) as games_played,
                AVG(blunders) as avg_blunders
            FROM games 
            WHERE username = ?
            GROUP BY strftime('%Y-%m', game_date)
            ORDER BY month
        ''', (username,))
        
        monthly_trends = cursor.fetchall()
        
        # Get rating progression if available
        cursor.execute('''
            SELECT game_date, rating, accuracy
            FROM games 
            WHERE username = ? AND rating IS NOT NULL
            ORDER BY game_date
        ''', (username,))
        
        rating_progression = cursor.fetchall()
        
        conn.close()
        
        return {
            "monthly_trends": [
                {
                    "month": row[0],
                    "avg_accuracy": row[1],
                    "games_played": row[2],
                    "avg_blunders": row[3]
                } for row in monthly_trends
            ],
            "rating_progression": [
                {
                    "date": row[0],
                    "rating": row[1],
                    "accuracy": row[2]
                } for row in rating_progression
            ]
        }
    
    def _extract_performance_data(self, game_data: Dict[str, Any]) -> GamePerformance:
        """Extract performance metrics from game analysis data"""
        # Get player reviews data
        player_reviews = game_data.get("player_reviews", {})
        
        # Determine user's color (assume they're white for now, could be improved)
        user_color = "white"  # This could be determined from username matching
        user_stats = player_reviews.get(user_color, {})
        
        # Extract move quality stats
        quality_stats = user_stats.get("quality_stats", {})
        
        return GamePerformance(
            username=game_data.get("username", "unknown"),
            source=game_data.get("source", "unknown"),
            game_date=game_data.get("analyzed_at", datetime.now().isoformat()),
            game_url=game_data.get("game_url", ""),
            color=user_color,
            result=game_data.get("result", "*"),
            accuracy=user_stats.get("accuracy", 0.0),
            blunders=len(user_stats.get("blunders", [])),
            mistakes=quality_stats.get("mistake", 0),
            inaccuracies=quality_stats.get("inaccuracy", 0),
            excellent_moves=quality_stats.get("excellent", 0),
            brilliant_moves=quality_stats.get("brilliant", 0),
            opening_name=game_data.get("opening", {}).get("name", "Unknown"),
            opening_eco=game_data.get("opening", {}).get("eco", "A00"),
            centipawn_loss=user_stats.get("total_centipawn_loss", 0),
            game_length=user_stats.get("move_count", 0),
            time_control="",  # Not available in current data
            rating=None  # Could be extracted from API data if available
        )
    
    def _store_game_performance(self, performance: GamePerformance) -> int:
        """Store game performance in database and return game ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO games (
                username, source, game_date, game_url, color, result,
                accuracy, blunders, mistakes, inaccuracies, excellent_moves,
                brilliant_moves, opening_name, opening_eco, centipawn_loss,
                game_length, time_control, rating
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            performance.username, performance.source, performance.game_date,
            performance.game_url, performance.color, performance.result,
            performance.accuracy, performance.blunders, performance.mistakes,
            performance.inaccuracies, performance.excellent_moves,
            performance.brilliant_moves, performance.opening_name,
            performance.opening_eco, performance.centipawn_loss,
            performance.game_length, performance.time_control, performance.rating
        ))
        
        game_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return game_id
    
    def _check_achievements(self, performance: GamePerformance, game_id: int) -> List[str]:
        """Check for new achievements and record them"""
        achievements = []
        
        # Check various achievement conditions
        if performance.accuracy >= 95:
            achievements.append(self._award_achievement(
                performance.username, "accuracy_perfectionist", 
                "Perfectionist", "Achieved 95%+ accuracy!", game_id
            ))
        
        if performance.accuracy >= 90:
            achievements.append(self._award_achievement(
                performance.username, "accuracy_master", 
                "Accuracy Master", "Achieved 90%+ accuracy!", game_id
            ))
        
        if performance.blunders == 0:
            achievements.append(self._award_achievement(
                performance.username, "blunder_free", 
                "Blunder Free", "Played a game without blunders!", game_id
            ))
        
        if performance.brilliant_moves >= 3:
            achievements.append(self._award_achievement(
                performance.username, "brilliant_tactician", 
                "Brilliant Tactician", "Made 3+ brilliant moves in one game!", game_id
            ))
        
        # Check for milestone achievements
        total_games = self._get_user_game_count(performance.username)
        if total_games in [10, 50, 100, 500, 1000]:
            achievements.append(self._award_achievement(
                performance.username, f"games_{total_games}", 
                f"{total_games} Games Milestone", f"Analyzed {total_games} games!", game_id
            ))
        
        return [ach for ach in achievements if ach]  # Filter out None values
    
    def _award_achievement(self, username: str, achievement_type: str, title: str, description: str, game_id: int) -> Optional[str]:
        """Award achievement if not already earned"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if achievement already exists
        cursor.execute('''
            SELECT id FROM achievements 
            WHERE username = ? AND achievement_type = ?
        ''', (username, achievement_type))
        
        if cursor.fetchone():
            conn.close()
            return None  # Already earned
        
        # Award achievement
        cursor.execute('''
            INSERT INTO achievements (username, achievement_type, achievement_title, achievement_description, game_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, achievement_type, title, description, game_id))
        
        conn.commit()
        conn.close()
        
        return f"🏆 {title}: {description}"
    
    def _get_user_game_count(self, username: str) -> int:
        """Get total game count for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM games WHERE username = ?', (username,))
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def _calculate_stats(self, games: List, cursor, username: str) -> PerformanceStats:
        """Calculate comprehensive performance statistics"""
        if not games:
            return PerformanceStats(
                total_games=0, avg_accuracy=0.0, accuracy_trend=[],
                best_accuracy=0.0, worst_accuracy=0.0, blunder_rate=0.0,
                improvement_score=0.0, favorite_openings=[],
                performance_by_color={"white": {}, "black": {}},
                recent_achievements=[]
            )
        
        # Basic stats
        accuracies = [game[7] for game in games]  # accuracy column
        total_games = len(games)
        avg_accuracy = sum(accuracies) / total_games
        best_accuracy = max(accuracies)
        worst_accuracy = min(accuracies)
        
        # Accuracy trend (last 10 games)
        accuracy_trend = accuracies[:10]
        
        # Blunder rate
        total_blunders = sum(game[8] for game in games)  # blunders column
        blunder_rate = total_blunders / total_games
        
        # Improvement score (trend of recent vs older games)
        improvement_score = self._calculate_improvement_score(accuracies)
        
        # Favorite openings
        favorite_openings = self._get_favorite_openings(cursor, username)
        
        # Performance by color
        performance_by_color = self._get_performance_by_color(games)
        
        # Recent achievements
        recent_achievements = self._get_recent_achievements(cursor, username)
        
        return PerformanceStats(
            total_games=total_games,
            avg_accuracy=avg_accuracy,
            accuracy_trend=accuracy_trend,
            best_accuracy=best_accuracy,
            worst_accuracy=worst_accuracy,
            blunder_rate=blunder_rate,
            improvement_score=improvement_score,
            favorite_openings=favorite_openings,
            performance_by_color=performance_by_color,
            recent_achievements=recent_achievements
        )
    
    def _calculate_improvement_score(self, accuracies: List[float]) -> float:
        """Calculate improvement score based on accuracy trend"""
        if len(accuracies) < 5:
            return 0.0
        
        recent = accuracies[:5]  # Last 5 games
        older = accuracies[5:10] if len(accuracies) >= 10 else accuracies[5:]
        
        if not older:
            return 0.0
        
        recent_avg = sum(recent) / len(recent)
        older_avg = sum(older) / len(older)
        
        return recent_avg - older_avg  # Positive = improving
    
    def _get_favorite_openings(self, cursor, username: str) -> List[Dict[str, Any]]:
        """Get user's most played openings with stats"""
        cursor.execute('''
            SELECT opening_name, opening_eco, COUNT(*) as games,
                   AVG(accuracy) as avg_accuracy, AVG(blunders) as avg_blunders
            FROM games 
            WHERE username = ? AND opening_eco IS NOT NULL
            GROUP BY opening_eco
            ORDER BY games DESC
            LIMIT 5
        ''', (username,))
        
        return [
            {
                "name": row[0],
                "eco": row[1],
                "games": row[2],
                "avg_accuracy": row[3],
                "avg_blunders": row[4]
            } for row in cursor.fetchall()
        ]
    
    def _get_performance_by_color(self, games: List) -> Dict[str, Dict[str, float]]:
        """Calculate performance statistics by color"""
        white_games = [g for g in games if g[5] == "white"]  # color column
        black_games = [g for g in games if g[5] == "black"]
        
        def calc_color_stats(color_games):
            if not color_games:
                return {"games": 0, "avg_accuracy": 0.0, "avg_blunders": 0.0}
            
            return {
                "games": len(color_games),
                "avg_accuracy": sum(g[7] for g in color_games) / len(color_games),
                "avg_blunders": sum(g[8] for g in color_games) / len(color_games)
            }
        
        return {
            "white": calc_color_stats(white_games),
            "black": calc_color_stats(black_games)
        }
    
    def _get_recent_achievements(self, cursor, username: str) -> List[str]:
        """Get recent achievements for user"""
        cursor.execute('''
            SELECT achievement_title, achievement_description, earned_at
            FROM achievements 
            WHERE username = ?
            ORDER BY earned_at DESC
            LIMIT 5
        ''', (username,))
        
        return [f"🏆 {row[0]}: {row[1]}" for row in cursor.fetchall()]
    
    def _process_opening_stats(self, results: List, is_specific: bool) -> Dict[str, Any]:
        """Process opening statistics results"""
        if is_specific:
            # Detailed stats for specific opening
            return {
                "games": results,
                "summary": {
                    "total_games": len(results),
                    "avg_accuracy": sum(r[4] for r in results) / len(results) if results else 0,
                    "blunder_rate": sum(r[5] for r in results) / len(results) if results else 0
                }
            }
        else:
            # Summary of all openings
            return {
                "top_openings": [
                    {
                        "name": row[0],
                        "eco": row[1], 
                        "games": row[6]
                    } for row in results
                ]
            }

# Global instance
performance_tracker = PerformanceTracker()