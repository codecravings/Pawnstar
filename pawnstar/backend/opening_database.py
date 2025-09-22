"""
Opening database for chess position analysis
"""

import chess
import chess.pgn
from typing import Dict, Optional, Tuple

class OpeningDatabase:
    def __init__(self):
        # ECO opening database - basic openings for now
        self.openings = {
            # King's Pawn Openings (C00-C99)
            "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": {
                "name": "King's Pawn Opening", 
                "eco": "B00",
                "category": "Open Game"
            },
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": {
                "name": "King's Pawn Game", 
                "eco": "C20",
                "category": "Open Game"
            },
            "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": {
                "name": "King's Knight Opening", 
                "eco": "C40",
                "category": "Open Game"
            },
            "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3": {
                "name": "Italian Game", 
                "eco": "C50",
                "category": "Open Game"
            },
            "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3": {
                "name": "Italian Game", 
                "eco": "C50",
                "category": "Open Game"
            },
            "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4": {
                "name": "Italian Game: Two Knights Defense", 
                "eco": "C55",
                "category": "Open Game"
            },
            
            # Queen's Pawn Openings (D00-D99)
            "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": {
                "name": "Queen's Pawn Opening", 
                "eco": "D00",
                "category": "Closed Game"
            },
            "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR w KQkq - 0 2": {
                "name": "Queen's Pawn Game", 
                "eco": "D00",
                "category": "Closed Game"
            },
            "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2": {
                "name": "Queen's Gambit", 
                "eco": "D06",
                "category": "Queen's Gambit"
            },
            "rnbqkbnr/ppp2ppp/8/3pp3/2PP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3": {
                "name": "Queen's Gambit Declined", 
                "eco": "D30",
                "category": "Queen's Gambit"
            },
            "rnbqkbnr/ppp2ppp/8/8/2pP4/8/PP2PPPP/RNBQKBNR w KQkq - 0 3": {
                "name": "Queen's Gambit Accepted", 
                "eco": "D20",
                "category": "Queen's Gambit"
            },
            
            # Sicilian Defense (B20-B99)
            "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": {
                "name": "Sicilian Defense", 
                "eco": "B20",
                "category": "Semi-Open Game"
            },
            "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": {
                "name": "Sicilian Defense: Open", 
                "eco": "B20",
                "category": "Semi-Open Game"
            },
            "r1bqkbnr/pp1ppppp/2n5/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3": {
                "name": "Sicilian Defense: Open", 
                "eco": "B20",
                "category": "Semi-Open Game"
            },
            "r1bqkbnr/pp1ppppp/2n5/2p5/3PP3/5N2/PPP2PPP/RNBQKB1R b KQkq - 0 3": {
                "name": "Sicilian Defense: Open Variation", 
                "eco": "B40",
                "category": "Semi-Open Game"
            },
            "r1bqkbnr/pp2pppp/2np4/2p5/3PP3/5N2/PPP2PPP/RNBQKB1R w KQkq - 1 4": {
                "name": "Sicilian Defense: Najdorf Variation", 
                "eco": "B90",
                "category": "Semi-Open Game"
            },
            
            # French Defense (C00-C19)
            "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": {
                "name": "French Defense", 
                "eco": "C00",
                "category": "Semi-Open Game"
            },
            "rnbqkbnr/ppp1pppp/8/3p4/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 0 2": {
                "name": "French Defense: Advance Variation", 
                "eco": "C02",
                "category": "Semi-Open Game"
            },
            "rnbqkbnr/ppp1pppp/8/3p4/3PP3/2N5/PPP2PPP/R1BQKBNR b KQkq - 1 2": {
                "name": "French Defense: Exchange Variation", 
                "eco": "C01",
                "category": "Semi-Open Game"
            },
            
            # Caro-Kann Defense (B10-B19)
            "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2": {
                "name": "Caro-Kann Defense", 
                "eco": "B10",
                "category": "Semi-Open Game"
            },
            "rnbqkbnr/pp1ppppp/2p5/8/3PP3/8/PPP2PPP/RNBQKBNR b KQkq - 0 2": {
                "name": "Caro-Kann Defense: Advance Variation", 
                "eco": "B12",
                "category": "Semi-Open Game"
            },
            
            # English Opening (A10-A39)
            "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1": {
                "name": "English Opening", 
                "eco": "A10",
                "category": "Flank Opening"
            },
            "rnbqkbnr/ppp1pppp/8/3p4/2P5/8/PP1PPPPP/RNBQKBNR w KQkq - 0 2": {
                "name": "English Opening: Symmetrical", 
                "eco": "A30",
                "category": "Flank Opening"
            },
            
            # Ruy Lopez (C60-C99)
            "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3": {
                "name": "Ruy Lopez", 
                "eco": "C60",
                "category": "Open Game"
            },
            "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3": {
                "name": "Spanish Opening", 
                "eco": "C60",
                "category": "Open Game"
            },
        }
        
        # Opening performance tracking
        self.opening_stats = {}
    
    def identify_opening(self, moves: list) -> Optional[Dict]:
        """Identify the opening from a list of moves"""
        board = chess.Board()
        
        # Play moves and check for opening matches
        for i, move in enumerate(moves):
            if i >= 10:  # Only check first 10 moves for opening
                break
                
            try:
                # Convert move notation to chess move
                if isinstance(move, str):
                    chess_move = board.parse_san(move)
                else:
                    # If it's a dict with uci_move
                    uci_move = move.get('uci_move', str(move))
                    chess_move = chess.Move.from_uci(uci_move)
                
                board.push(chess_move)
                
                # Check if current position matches any opening
                fen = board.fen()
                if fen in self.openings:
                    opening = self.openings[fen].copy()
                    opening['moves_played'] = i + 1
                    opening['position_fen'] = fen
                    return opening
                    
            except (ValueError, chess.InvalidMoveError):
                continue
        
        return None
    
    def get_opening_stats(self, username: str, opening_name: str) -> Dict:
        """Get user's performance in a specific opening"""
        if username not in self.opening_stats:
            self.opening_stats[username] = {}
        
        if opening_name not in self.opening_stats[username]:
            return {
                "games_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "win_rate": 0.0,
                "avg_accuracy": 0.0
            }
        
        return self.opening_stats[username][opening_name]
    
    def update_opening_stats(self, username: str, opening_name: str, result: str, accuracy: float):
        """Update user's opening statistics"""
        if username not in self.opening_stats:
            self.opening_stats[username] = {}
        
        if opening_name not in self.opening_stats[username]:
            self.opening_stats[username][opening_name] = {
                "games_played": 0,
                "wins": 0,
                "draws": 0,
                "losses": 0,
                "accuracies": []
            }
        
        stats = self.opening_stats[username][opening_name]
        stats["games_played"] += 1
        stats["accuracies"].append(accuracy)
        
        if result == "1-0":  # User won as white
            stats["wins"] += 1
        elif result == "0-1":  # User won as black  
            stats["wins"] += 1
        elif result == "1/2-1/2":
            stats["draws"] += 1
        else:
            stats["losses"] += 1
        
        # Calculate derived stats
        total_games = stats["games_played"]
        stats["win_rate"] = (stats["wins"] / total_games * 100) if total_games > 0 else 0
        stats["avg_accuracy"] = sum(stats["accuracies"]) / len(stats["accuracies"]) if stats["accuracies"] else 0
    
    def get_popular_openings(self) -> list:
        """Get list of most popular openings"""
        popular = [
            {"name": "Sicilian Defense", "eco": "B20", "frequency": "25%"},
            {"name": "Queen's Gambit", "eco": "D06", "frequency": "15%"},
            {"name": "Ruy Lopez", "eco": "C60", "frequency": "12%"},
            {"name": "Italian Game", "eco": "C50", "frequency": "10%"},
            {"name": "French Defense", "eco": "C00", "frequency": "8%"},
            {"name": "Caro-Kann Defense", "eco": "B10", "frequency": "6%"},
            {"name": "English Opening", "eco": "A10", "frequency": "5%"},
        ]
        return popular
    
    def suggest_openings(self, username: str, color: str = "white") -> list:
        """Suggest openings for the user to study"""
        suggestions = []
        
        if color == "white":
            suggestions = [
                {"name": "Italian Game", "reason": "Great for tactical development", "eco": "C50"},
                {"name": "Queen's Gambit", "reason": "Solid positional foundation", "eco": "D06"},
                {"name": "English Opening", "reason": "Flexible and modern", "eco": "A10"},
                {"name": "Ruy Lopez", "reason": "Classical and principled", "eco": "C60"},
            ]
        else:
            suggestions = [
                {"name": "Sicilian Defense", "reason": "Sharp and aggressive", "eco": "B20"},
                {"name": "French Defense", "reason": "Solid structure", "eco": "C00"},
                {"name": "Caro-Kann Defense", "reason": "Reliable and safe", "eco": "B10"},
                {"name": "Queen's Gambit Declined", "reason": "Classical approach", "eco": "D30"},
            ]
        
        return suggestions

# Global instance
opening_db = OpeningDatabase()