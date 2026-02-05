from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import chess
import chess.engine
import chess.pgn
from io import StringIO
from typing import List, Dict, Any, Optional
import os
import json
import hashlib
from datetime import datetime
from dateutil import parser
from dotenv import load_dotenv
from opening_database import opening_db
from tactical_patterns import tactical_analyzer
from performance_tracker import performance_tracker

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration from environment
STOCKFISH_PATH = os.getenv("STOCKFISH_PATH", r"C:\stockfish\stockfish.exe")
CACHE_DIR = os.getenv("CACHE_DIR", "backend/cache")

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

class AnalysisRequest(BaseModel):
    username: str
    source: str = "lichess"
    max: int = 10
    depth: int = 12

class MoveAnalysis(BaseModel):
    ply: int
    uci_move: str
    fen: str
    best_move: str
    evaluation: Dict[str, Any]

class LatestGameResponse(BaseModel):
    username: str
    source: str
    latest_hash: str
    timestamp: str

class GameReview(BaseModel):
    top_blunders: List[Dict[str, Any]]
    accuracy_estimate: float
    weak_squares: List[str]
    summary_text: str

class GameSummary(BaseModel):
    white: str
    black: str
    result: str
    date: str
    time_control: str
    opening: Optional[str] = None
    url: Optional[str] = None

def get_cache_key(data: str) -> str:
    """Generate SHA256 hash for caching."""
    return hashlib.sha256(data.encode()).hexdigest()

def get_latest_cache_path(source: str, username: str) -> str:
    """Get path for latest game cache file."""
    return os.path.join(CACHE_DIR, f"latest_{source}_{username}.txt")

def get_analysis_cache_path(hash_key: str) -> str:
    """Get path for analysis cache file."""
    return os.path.join(CACHE_DIR, f"{hash_key}.json")

async def fetch_lichess_latest(username: str) -> Dict[str, Any]:
    """Fetch latest game metadata from Lichess."""
    url = f"https://lichess.org/api/games/user/{username}"
    headers = {"User-Agent": "PawnstarLocal/0.1"}
    params = {"max": 1, "format": "pgn", "rated": "true"}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    pgn_content = response.text.strip()
    if not pgn_content:
        raise HTTPException(status_code=404, detail="no public games found")
    
    # Parse PGN to get timestamp
    pgn_io = StringIO(pgn_content)
    game = chess.pgn.read_game(pgn_io)
    if not game:
        raise HTTPException(status_code=404, detail="no public games found")
    
    # Get timestamp from headers
    timestamp = game.headers.get("UTCDate", "") + "T" + game.headers.get("UTCTime", "00:00:00") + "Z"
    hash_key = get_cache_key(pgn_content)
    
    return {
        "username": username,
        "source": "lichess",
        "latest_hash": hash_key,
        "timestamp": timestamp
    }

async def fetch_chesscom_latest(username: str) -> Dict[str, Any]:
    """Fetch latest game metadata from Chess.com."""
    headers = {"User-Agent": "PawnstarLocal/0.1"}
    
    # Get user's archives
    archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
    response = requests.get(archives_url, headers=headers)
    response.raise_for_status()
    
    archives = response.json().get("archives", [])
    if not archives:
        raise HTTPException(status_code=404, detail="no public games found")
    
    # Get latest month's games
    latest_archive = archives[-1]
    response = requests.get(latest_archive, headers=headers)
    response.raise_for_status()
    
    games_data = response.json().get("games", [])
    if not games_data:
        raise HTTPException(status_code=404, detail="no public games found")
    
    # Get latest game
    latest_game = games_data[-1]
    game_id = str(latest_game.get("uuid", latest_game.get("url", "")))
    end_time = latest_game.get("end_time", 0)
    
    # Convert timestamp to ISO format
    timestamp = datetime.fromtimestamp(end_time).isoformat() + "Z"
    hash_key = get_cache_key(game_id)
    
    return {
        "username": username,
        "source": "chess.com",
        "latest_hash": hash_key,
        "timestamp": timestamp
    }
 hive_flutter: ^1.1.0
  path_provider: ^2.1.1
  image_picker: ^1.0.4
  file_picker: ^8.0.0
  permission_handler: ^11.0.1
  provider: ^6.1.1
  fl_chart: ^0.65.0
  google_fonts: ^6.1.0
  flutter_animate: ^4.3.0
  uuid: ^4.2.1
  intl: ^0.18.1
  shared_preferences: ^2.2.2
  flutter_local_notifications: ^17.0.0
  google_mobile_ads: ^4.0.0
  video_player: ^2.8.2
  in_app_purchase: ^3.1.13

dev_dependencies:
  flutter_test:
    sdk: flutter
  flutter_lints: ^3.0.1
  hive_generator: ^2.0.1
  build_runner: ^2.4.7

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/icons/
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/latest-game")
async def get_latest_game(username: str, source: str = "lichess") -> LatestGameResponse:
    """Get latest game metadata for a user."""
    try:
        # Check cache first
        cache_path = get_latest_cache_path(source, username)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cached_data = json.load(f)
                # Return cached data if it's less than 5 minutes old
                cached_time = parser.parse(cached_data["timestamp"])
                if (datetime.now() - cached_time.replace(tzinfo=None)).seconds < 300:
                    return LatestGameResponse(**cached_data)
        
        # Fetch fresh data
        if source == "lichess":
            data = await fetch_lichess_latest(username)
        elif source == "chess.com":
            data = await fetch_chesscom_latest(username)
        else:
            raise HTTPException(status_code=400, detail="unsupported source")
        
        # Cache the result
        with open(cache_path, 'w') as f:
            json.dump(data, f)
        
        return LatestGameResponse(**data)
        
    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code in [429, 403]:
                raise HTTPException(status_code=502, detail=f"Rate limited by {source}. Please try again in a few minutes.")
            elif e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="no public games found")
        raise HTTPException(status_code=502, detail=f"Failed to fetch from {source}: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@app.get("/games")
async def get_user_games(username: str, source: str = "lichess", max_games: int = 20) -> List[GameSummary]:
    """Get previous games for a user."""
    try:
        headers = {"User-Agent": "PawnstarLocal/0.1"}
        
        if source == "lichess":
            url = f"https://lichess.org/api/games/user/{username}"
            params = {"max": max_games, "format": "pgn", "rated": "true"}
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            games_pgn = response.text
            if not games_pgn.strip():
                return []
            
            games = []
            pgn_io = StringIO(games_pgn)
            
            while True:
                game = chess.pgn.read_game(pgn_io)
                if game is None:
                    break
                    
                # Extract game info
                headers_dict = dict(game.headers)
                date = headers_dict.get("UTCDate", "")
                time = headers_dict.get("UTCTime", "")
                
                game_summary = GameSummary(
                    white=headers_dict.get("White", "Unknown"),
                    black=headers_dict.get("Black", "Unknown"),
                    result=headers_dict.get("Result", "*"),
                    date=f"{date} {time}" if date and time else date,
                    time_control=headers_dict.get("TimeControl", "Unknown"),
                    opening=headers_dict.get("Opening", None),
                    url=headers_dict.get("Site", None)
                )
                games.append(game_summary)
            
            return games
            
        elif source == "chess.com":
            # Get user's archives
            archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
            response = requests.get(archives_url, headers=headers)
            response.raise_for_status()
            
            archives = response.json().get("archives", [])
            if not archives:
                return []
            
            # Get latest month's games
            latest_archive = archives[-1]
            response = requests.get(latest_archive, headers=headers)
            response.raise_for_status()
            
            games_data = response.json().get("games", [])
            if not games_data:
                return []
            
            games = []
            for game_data in games_data[-max_games:]:
                white_info = game_data.get("white", {})
                black_info = game_data.get("black", {})
                end_time = game_data.get("end_time", 0)
                
                game_summary = GameSummary(
                    white=white_info.get("username", "Unknown"),
                    black=black_info.get("username", "Unknown"),
                    result=game_data.get("result", "*"),
                    date=datetime.fromtimestamp(end_time).isoformat() if end_time else "",
                    time_control=game_data.get("time_class", "Unknown"),
                    opening=None,
                    url=game_data.get("url", None)
                )
                games.append(game_summary)
            
            return games
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported source")
            
    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code in [429, 403]:
                raise HTTPException(status_code=502, detail=f"Rate limited by {source}. Please try again in a few minutes.")
            elif e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="User not found")
        raise HTTPException(status_code=502, detail=f"Failed to fetch games from {source}: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

def summarize_tactical_patterns(patterns: List) -> Dict[str, Any]:
    """Summarize tactical patterns for move analysis"""
    if not patterns:
        return None
    
    summary = {
        "count": len(patterns),
        "patterns": []
    }
    
    for pattern in patterns:
        pattern_info = {
            "name": pattern.name,
            "type": pattern.pattern_type,
            "description": pattern.description,
            "severity": pattern.severity,
            "emoji": pattern.emoji,
            "attacking_square": pattern.attacking_square,
            "target_squares": pattern.target_squares
        }
        summary["patterns"].append(pattern_info)
    
    # Add summary statistics
    severity_counts = {}
    for pattern in patterns:
        severity = pattern.severity
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    summary["severity_breakdown"] = severity_counts
    
    # Generate human-readable summary
    if len(patterns) == 1:
        summary["text"] = f"{patterns[0].emoji} {patterns[0].name}: {patterns[0].description}"
    else:
        critical = severity_counts.get("critical", 0)
        major = severity_counts.get("major", 0)
        minor = severity_counts.get("minor", 0)
        
        if critical > 0:
            summary["text"] = f"🚨 {critical} critical tactical pattern{'s' if critical > 1 else ''} found!"
        elif major > 0:
            summary["text"] = f"⚠️ {major} major tactical pattern{'s' if major > 1 else ''} detected"
        else:
            summary["text"] = f"ℹ️ {minor} minor tactical opportunity{'ies' if minor > 1 else 'y'}"
    
    return summary

def get_move_quality(centipawn_loss: int, is_best_move: bool = False, is_second_best: bool = False) -> Dict[str, str]:
    """Get realistic move quality description based on Chess.com standards."""
    
    # Brilliant moves: Must be best move with tactical complexity or sacrifice
    if is_best_move and centipawn_loss == 0:
        return {
            "category": "brilliant",
            "description": "⚡ BRILLIANT! Outstanding tactical play!",
            "emoji": "⚡"
        }
    
    # Best moves: Optimal or near-optimal play
    elif centipawn_loss <= 5:
        return {
            "category": "best",
            "description": "✅ BEST! Perfect engine move!",
            "emoji": "✅"
        }
    
    # Excellent: Very good moves with minimal loss
    elif centipawn_loss <= 15:
        return {
            "category": "excellent",
            "description": "👍 EXCELLENT! Very strong play!",
            "emoji": "👍"
        }
    
    # Good: Solid moves with acceptable loss
    elif centipawn_loss <= 30:
        return {
            "category": "good",
            "description": "😊 GOOD! Solid move!",
            "emoji": "😊"
        }
    
    # Book/Natural: Standard opening/endgame moves
    elif centipawn_loss <= 50:
        return {
            "category": "book",
            "description": "📖 BOOK! Standard move!",
            "emoji": "📖"
        }
    
    # Inaccuracy: Noticeable but not critical mistakes  
    elif centipawn_loss <= 100:
        return {
            "category": "inaccuracy",
            "description": "⚠️ INACCURACY! Could be better!",
            "emoji": "⚠️"
        }
    elif centipawn_loss <= 150:
        return {
            "category": "inaccuracy",
            "description": "😬 INACCURACY! Your move made Stockfish slightly nervous!",
            "emoji": "😅"
        }
    elif centipawn_loss <= 250:
        return {
            "category": "mistake",
            "description": "🤦 MISTAKE! Even your pieces are facepalming!",
            "emoji": "🙈"
        }
    elif centipawn_loss <= 400:
        return {
            "category": "blunder",
            "description": "💀 BLUNDER! Your opponent is doing a happy dance!",
            "emoji": "🤡"
        }
    else:
        return {
            "category": "catastrophe",
            "description": "💥 CATASTROPHIC BLUNDER! Chess.com servers felt that one!",
            "emoji": "🔥💀"
        }

def generate_player_reviews(moves: List[Dict[str, Any]], game_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate separate game reviews for White and Black players."""
    white_moves = []
    black_moves = []
    white_blunders = []
    black_blunders = []
    white_total_loss = 0
    black_total_loss = 0
    
    # Separate moves by player using pre-calculated centipawn loss
    for i, move in enumerate(moves):
        is_white_move = move["ply"] % 2 == 1
        
        # Use pre-calculated centipawn loss from move analysis
        centipawn_loss = move.get("centipawn_loss", 0)
        
        # Add to player totals
        if is_white_move:
            white_total_loss += centipawn_loss
        else:
            black_total_loss += centipawn_loss
        
        # Check if this qualifies as a significant mistake/blunder
        if centipawn_loss >= 100:
            blunder = {
                "ply": move["ply"],
                "move": move["uci_move"],
                "centipawn_loss": centipawn_loss
            }
            if is_white_move:
                white_blunders.append(blunder)
            else:
                black_blunders.append(blunder)
        
        # Separate moves by player
        if is_white_move:
            white_moves.append(move)
        else:
            black_moves.append(move)
    
    # Calculate accuracy for each player
    def calculate_accuracy(total_loss: float, move_count: int) -> float:
        if move_count > 0:
            avg_centipawn_loss = total_loss / move_count
            return max(10, 95 - (avg_centipawn_loss * 1.0))
        return 50
    
    white_accuracy = calculate_accuracy(white_total_loss, len(white_moves))
    black_accuracy = calculate_accuracy(black_total_loss, len(black_moves))
    
    # Generate summaries
    def get_summary(accuracy: float, blunder_count: int, player: str) -> str:
        if accuracy >= 90:
            base = f"🏆 GODLIKE! {accuracy:.1f}% accuracy! Are you even human? 🤖"
        elif accuracy >= 85:
            base = f"💎 MASTERCLASS! {accuracy:.1f}% accuracy! Magnus is sweating! 😰"
        elif accuracy >= 80:
            base = f"⭐ EXCELLENT! {accuracy:.1f}% accuracy! Your chess engine approves! 👍"
        elif accuracy >= 75:
            base = f"✨ SOLID PLAY! {accuracy:.1f}% accuracy! Not bad, human! 🙂"
        elif accuracy >= 65:
            base = f"😐 DECENT EFFORT! {accuracy:.1f}% accuracy! Room for improvement! 📚"
        elif accuracy >= 50:
            base = f"😬 ROUGH GAME! {accuracy:.1f}% accuracy! Your pieces are questioning your choices! 🤔"
        else:
            base = f"💀 MASSACRE! {accuracy:.1f}% accuracy! Even beginners are cringing! 🙈"
        
        if blunder_count > 0:
            base += f" | {blunder_count} major blunder{'s' if blunder_count != 1 else ''} detected! 🚨"
        return base
    
    # Calculate move quality statistics for each player
    def get_move_quality_stats(player_moves):
        quality_counts = {}
        for move in player_moves:
            quality = move.get("quality", {}).get("category", "unknown")
            quality_counts[quality] = quality_counts.get(quality, 0) + 1
        return quality_counts
    
    white_quality_stats = get_move_quality_stats(white_moves)
    black_quality_stats = get_move_quality_stats(black_moves)
    
    return {
        "white": {
            "accuracy": round(white_accuracy, 1),
            "blunders": sorted(white_blunders, key=lambda x: x["centipawn_loss"], reverse=True)[:5],
            "summary": get_summary(white_accuracy, len(white_blunders), "White"),
            "move_count": len(white_moves),
            "quality_stats": white_quality_stats,
            "total_centipawn_loss": white_total_loss
        },
        "black": {
            "accuracy": round(black_accuracy, 1),
            "blunders": sorted(black_blunders, key=lambda x: x["centipawn_loss"], reverse=True)[:5],
            "summary": get_summary(black_accuracy, len(black_blunders), "Black"),
            "move_count": len(black_moves),
            "quality_stats": black_quality_stats,
            "total_centipawn_loss": black_total_loss
        },
        "overall": {
            "total_moves": len(moves),
            "white_moves": len(white_moves),
            "black_moves": len(black_moves)
        }
    }

def generate_reviews(moves: List[Dict[str, Any]], game_data: Dict[str, Any]) -> GameReview:
    """Generate legacy game review format for backward compatibility."""
    blunders = []
    total_moves = len(moves)
    total_centipawn_loss = 0
    
    for i, move in enumerate(moves):
        centipawn_loss = 0
        
        # Calculate centipawn loss from previous move
        if i > 0 and move.get("evaluation") and move["evaluation"].get("type") == "cp":
            current_eval = move["evaluation"]["value"]
            prev_move = moves[i-1]
            
            if prev_move.get("evaluation") and prev_move["evaluation"].get("type") == "cp":
                prev_eval = prev_move["evaluation"]["value"]
                
                # Calculate loss based on perspective
                # Positive evals favor white, negative favor black
                if move["ply"] % 2 == 1:  # White move (odd ply)
                    # For white, eval should increase or stay same
                    centipawn_loss = max(0, prev_eval - current_eval)
                else:  # Black move (even ply)
                    # For black, eval should decrease (become more negative) or stay same
                    centipawn_loss = max(0, current_eval - prev_eval)
                
                total_centipawn_loss += centipawn_loss
                
                # Check if this qualifies as a significant mistake/blunder
                if centipawn_loss >= 100:  # Lowered threshold for blunders
                    blunders.append({
                        "ply": move["ply"],
                        "move": move["uci_move"],
                        "eval_before": prev_eval,
                        "eval_after": current_eval,
                        "centipawn_loss": centipawn_loss
                    })
        
        # Don't overwrite move quality - it's already calculated in main analysis
        # Only add quality if it doesn't exist (for backward compatibility)
        if "quality" not in move:
            quality = get_move_quality(centipawn_loss, False)
            move["quality"] = quality
    
    # Calculate accuracy estimate - improved formula
    # Use a more realistic accuracy calculation based on average centipawn loss per move
    if total_moves > 0:
        avg_centipawn_loss = total_centipawn_loss / total_moves
        # More realistic scaling: perfect play = 95%, 10cp loss per move = 85%, 20cp = 75%, etc.
        accuracy = max(10, 95 - (avg_centipawn_loss * 1.0))  # Each centipawn costs 1% accuracy
    else:
        accuracy = 50
    
    # Generate humorous summary
    blunder_count = len(blunders)
    if accuracy >= 90:
        summary = f"🏆 GODLIKE! {accuracy:.1f}% accuracy! Are you even human? 🤖"
    elif accuracy >= 85:
        summary = f"💎 MASTERCLASS! {accuracy:.1f}% accuracy! Magnus is sweating! 😰"
    elif accuracy >= 80:
        summary = f"⭐ EXCELLENT! {accuracy:.1f}% accuracy! Your chess engine approves! 👍"
    elif accuracy >= 75:
        summary = f"✨ SOLID PLAY! {accuracy:.1f}% accuracy! Not bad, human! 🙂"
    elif accuracy >= 65:
        summary = f"😐 DECENT EFFORT! {accuracy:.1f}% accuracy! Room for improvement! 📚"
    elif accuracy >= 50:
        summary = f"😬 ROUGH GAME! {accuracy:.1f}% accuracy! Your pieces are questioning your choices! 🤔"
    else:
        summary = f"💀 MASSACRE! {accuracy:.1f}% accuracy! Even beginners are cringing! 🙈"
    
    if blunder_count > 0:
        summary += f" | {blunder_count} major blunder{'s' if blunder_count != 1 else ''} detected! 🚨"
    
    return GameReview(
        top_blunders=sorted(blunders, key=lambda x: x["centipawn_loss"], reverse=True)[:5],
        accuracy_estimate=round(accuracy, 1),
        weak_squares=[],  # Would need deeper analysis
        summary_text=summary
    )

async def fetch_games_for_analysis(username: str, source: str, max_games: int) -> str:
    """Fetch games PGN for analysis."""
    headers = {"User-Agent": "PawnstarLocal/0.1"}
    
    if source == "lichess":
        url = f"https://lichess.org/api/games/user/{username}"
        params = {"max": max_games, "format": "pgn", "rated": "true"}
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.text
        
    elif source == "chess.com":
        # For chess.com, we'll need to get PGN differently
        # First get archives, then latest games
        archives_url = f"https://api.chess.com/pub/player/{username}/games/archives"
        response = requests.get(archives_url, headers=headers)
        response.raise_for_status()
        
        archives = response.json().get("archives", [])
        if not archives:
            return ""
            
        # Get latest month's games
        latest_archive = archives[-1]
        response = requests.get(latest_archive, headers=headers)
        response.raise_for_status()
        
        games_data = response.json().get("games", [])
        if not games_data:
            return ""
            
        # Take last N games and convert to PGN format
        recent_games = games_data[-max_games:]
        pgn_parts = []
        
        for game in recent_games:
            # Convert chess.com game to PGN format
            white = game.get("white", {}).get("username", "Unknown")
            black = game.get("black", {}).get("username", "Unknown") 
            result = game.get("result", "*")
            pgn = game.get("pgn", "")
            
            if pgn:
                pgn_parts.append(pgn)
        
        return "\n\n".join(pgn_parts)
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported source")

@app.post("/analyze-game")
async def analyze_single_game(request: Dict[str, str]) -> Dict[str, Any]:
    """Analyze a specific game by URL."""
    game_url = request.get("game_url")
    if not game_url:
        raise HTTPException(status_code=400, detail="game_url is required")
    
    try:
        # Extract game ID and source from URL
        if "lichess.org" in game_url:
            game_id = game_url.split("/")[-1].split("?")[0]  # Remove query params
            source = "lichess"
            
            # Fetch specific game from Lichess
            headers = {"User-Agent": "PawnstarLocal/0.1"}
            pgn_url = f"https://lichess.org/game/export/{game_id}"
            response = requests.get(pgn_url, headers=headers)
            response.raise_for_status()
            games_pgn = response.text
            
        elif "chess.com" in game_url:
            # For chess.com, extract from URL like: https://www.chess.com/game/live/123456789
            game_id = game_url.split("/")[-1]
            source = "chess.com"
            
            # Try to fetch the game from Chess.com API
            headers = {"User-Agent": "PawnstarLocal/0.1"}
            api_url = f"https://www.chess.com/callback/live/game/{game_id}"
            
            try:
                response = requests.get(api_url, headers=headers)
                response.raise_for_status()
                game_data = response.json()
                
                # Extract game info from Chess.com response
                if "game" in game_data:
                    game_info = game_data["game"]
                    
                    # Construct PGN from headers and move list
                    if "pgnHeaders" in game_info:
                        headers_dict = game_info["pgnHeaders"]
                        
                        # Build PGN headers
                        pgn_lines = []
                        for key, value in headers_dict.items():
                            pgn_lines.append(f'[{key} "{value}"]')
                        
                        pgn_lines.append("")  # Empty line after headers
                        
                        # Convert move list to PGN moves if available
                        if "moveList" in game_info and game_info["moveList"]:
                            # Chess.com uses encoded move format, try to decode it
                            move_list = game_info["moveList"]
                            
                            # For now, we'll fetch the PGN from archive API if available
                            # Try to get the PGN from Chess.com's archive API
                            try:
                                # Extract year and month from date header
                                date_str = headers_dict.get("Date", "")
                                if date_str:
                                    year, month = date_str.split(".")[0], date_str.split(".")[1]
                                    username = headers_dict.get("White", "").lower()
                                    if not username:
                                        username = headers_dict.get("Black", "").lower()
                                    
                                    # Try to get PGN from monthly archive
                                    archive_url = f"https://api.chess.com/pub/player/{username}/games/{year}/{month:0>2}/pgn"
                                    archive_response = requests.get(archive_url, headers=headers)
                                    if archive_response.status_code == 200:
                                        archive_pgn = archive_response.text
                                        # Look for our specific game in the archive using Link header
                                        link_to_find = f"https://www.chess.com/game/live/{game_id}"
                                        
                                        # Split into individual games
                                        games_in_archive = archive_pgn.split('\n\n\n')
                                        for game_block in games_in_archive:
                                            if link_to_find in game_block:
                                                games_pgn = game_block.strip()
                                                break
                                        else:
                                            # If not found by link, try matching by players and date
                                            for game_block in games_in_archive:
                                                if (headers_dict.get("White", "") in game_block and 
                                                    headers_dict.get("Black", "") in game_block and
                                                    headers_dict.get("Date", "") in game_block):
                                                    games_pgn = game_block.strip()
                                                    break
                                            else:
                                                # If still not found, construct basic PGN
                                                games_pgn = "\n".join(pgn_lines) + "\n\n*"
                                    else:
                                        # Archive not accessible, construct basic PGN
                                        games_pgn = "\n".join(pgn_lines) + "\n\n*"
                                else:
                                    # No date available, construct basic PGN
                                    games_pgn = "\n".join(pgn_lines) + "\n\n*"
                            except:
                                # Fallback to basic PGN construction
                                games_pgn = "\n".join(pgn_lines) + "\n\n*"
                        else:
                            # No moves available, construct basic PGN
                            games_pgn = "\n".join(pgn_lines) + "\n\n*"
                    else:
                        raise HTTPException(status_code=404, detail="Could not extract game headers from Chess.com game.")
                else:
                    raise HTTPException(status_code=404, detail="Invalid Chess.com game response format.")
                        
            except requests.RequestException as e:
                raise HTTPException(status_code=502, detail=f"Failed to fetch Chess.com game: {str(e)}")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error processing Chess.com game: {str(e)}")
            
        else:
            raise HTTPException(status_code=400, detail="Unsupported game URL. Please use Lichess or Chess.com URLs.")
        
        if not games_pgn.strip():
            raise HTTPException(status_code=404, detail="Game not found or not public")
        
        # Use unique cache key for this specific game
        # Always include game_id and source to ensure uniqueness
        cache_data = f"individual_game_{source}_{game_id}"
        pgn_hash = get_cache_key(cache_data)
        cache_path = get_analysis_cache_path(pgn_hash)
        
        # Check cache first
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cached_result = json.load(f)
                return cached_result
        
        # Parse the PGN
        games = []
        pgn_io = StringIO(games_pgn)
        
        game = chess.pgn.read_game(pgn_io)
        if game is None:
            raise HTTPException(status_code=404, detail="No valid game found")
        
        # Analyze the game with Stockfish
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            board = chess.Board()
            moves = []
            ply = 1
            
            for move in game.mainline_moves():
                # Analyze current position BEFORE making the move with multi-PV
                current_position_analysis = engine.analyse(board, chess.engine.Limit(depth=12), multipv=3)
                
                # Extract top 3 moves with evaluations
                top_moves = []
                best_move = None
                current_eval = 0
                
                for i, analysis in enumerate(current_position_analysis):
                    if "pv" in analysis and analysis["pv"]:
                        move_uci = str(analysis["pv"][0])
                        score = analysis.get("score")
                        
                        move_info = {
                            "move": move_uci,
                            "rank": i + 1,
                            "evaluation": {}
                        }
                        
                        if score:
                            score_relative = score.relative
                            if score_relative.is_mate():
                                move_info["evaluation"] = {"type": "mate", "value": score_relative.mate()}
                            else:
                                move_info["evaluation"] = {"type": "cp", "value": score_relative.score() or 0}
                                if i == 0:  # First move evaluation for current_eval
                                    current_eval = score_relative.score() or 0
                        
                        top_moves.append(move_info)
                        
                        if i == 0:  # First move is the best move
                            best_move = move_uci
                
                # Calculate if the played move is the best move
                played_move = str(move)
                is_best_move = (played_move == best_move)
                
                # Calculate centipawn loss by comparing evaluations
                centipawn_loss = 0
                if not is_best_move and best_move:
                    try:
                        # Make the played move and get evaluation
                        board.push(move)
                        played_eval = engine.analyse(board, chess.engine.Limit(depth=10))["score"].relative.score() or 0
                        board.pop()  # Undo the move
                        
                        # Make the best move and get evaluation  
                        best_move_obj = chess.Move.from_uci(best_move)
                        board.push(best_move_obj)
                        best_eval = engine.analyse(board, chess.engine.Limit(depth=10))["score"].relative.score() or 0
                        board.pop()  # Undo the move
                        
                        # Calculate centipawn loss (difference between best and played evaluation)
                        # Note: We need to flip perspective for the next player
                        centipawn_loss = abs(best_eval - played_eval)
                        
                        
                    except Exception as e:
                        centipawn_loss = 0
                
                # Get move quality based on centipawn loss
                quality = get_move_quality(centipawn_loss, is_best_move)
                
                # Analyze tactical patterns in the position BEFORE the move
                position_fen = board.fen()
                tactical_patterns = tactical_analyzer.analyze_position(chess.Board(position_fen))
                tactical_summary = summarize_tactical_patterns(tactical_patterns) if tactical_patterns else None
                
                moves.append({
                    "ply": ply,
                    "uci_move": played_move,
                    "fen": board.fen(),
                    "best_move": best_move,
                    "top_moves": top_moves,  # Add top 3 moves with evaluations
                    "evaluation": {"type": "cp", "value": current_eval},
                    "centipawn_loss": centipawn_loss,
                    "quality": quality,
                    "tactical_patterns": tactical_summary  # Add tactical analysis
                })
                
                # Actually make the move for next iteration
                board.push(move)
                ply += 1
        
        # Get game metadata
        headers_dict = dict(game.headers)
        
        game_analysis = {
            "game_index": 0,
            "white": headers_dict.get("White", "Unknown"),
            "black": headers_dict.get("Black", "Unknown"), 
            "result": headers_dict.get("Result", "*"),
            "source": source,
            "moves": moves
        }
        
        # Add opening analysis
        opening_info = opening_db.identify_opening(moves)
        if opening_info:
            game_analysis["opening"] = opening_info
            
            # Update opening stats for both players
            white_player = game_analysis["white"]
            black_player = game_analysis["black"]
            result = game_analysis["result"]
            
            # Calculate average accuracy for opening stats
            white_acc = 0
            black_acc = 0
            if moves:
                # This will be calculated later with player_reviews, for now use placeholder
                white_acc = 75  # Will be updated after player_reviews
                black_acc = 75
        else:
            game_analysis["opening"] = {
                "name": "Unknown Opening",
                "eco": "A00",
                "category": "Unknown",
                "moves_played": 0
            }
        
        # Generate player-separated reviews
        player_reviews = generate_player_reviews(moves, game_analysis)
        game_analysis["player_reviews"] = player_reviews
        
        # Generate legacy reviews for backward compatibility
        review = generate_reviews(moves, game_analysis)
        game_analysis["review"] = review.model_dump()
        
        result = {
            "games": [game_analysis],
            "analysis_hash": pgn_hash,
            "analyzed_at": datetime.now().isoformat(),
            "game_url": game_url
        }
        
        # Record performance and check for achievements
        try:
            achievements = performance_tracker.record_game_performance(game_analysis)
            if achievements:
                result["achievements"] = achievements
        except Exception as e:
            print(f"Performance tracking error: {e}")  # Log but don't fail
        
        # Cache the result
        with open(cache_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        return result
        
    except HTTPException:
        # Re-raise HTTPExceptions (like the Chess.com error)
        raise
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")  # Debug logging
        raise HTTPException(status_code=502, detail=f"Failed to fetch game: {str(e)}")
    except chess.engine.EngineError as e:
        print(f"Engine error: {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Stockfish engine error: {str(e)}")
    except Exception as e:
        print(f"Analysis error (individual game): {str(e)}")  # Debug logging
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze")
async def analyze_games(request: AnalysisRequest) -> Dict[str, Any]:
    """
    Analyze recent games from specified source using Stockfish with caching
    """
    try:
        # Fetch games PGN
        games_pgn = await fetch_games_for_analysis(request.username, request.source, request.max)
        if not games_pgn.strip():
            raise HTTPException(status_code=404, detail="No games found for user")
        
        # Check cache first - include username in cache key to prevent cross-user pollution
        cache_data = f"{request.username}_{request.source}_{games_pgn}"
        pgn_hash = get_cache_key(cache_data)
        cache_path = get_analysis_cache_path(pgn_hash)
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                cached_result = json.load(f)
                return cached_result
        
        # Parse PGN games
        games = []
        pgn_io = StringIO(games_pgn)
        
        while True:
            game = chess.pgn.read_game(pgn_io)
            if game is None:
                break
            games.append(game)
        
        if not games:
            raise HTTPException(status_code=404, detail="No valid games found")
        
        # Analyze games with Stockfish
        results = []
        
        with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
            for game_idx, game in enumerate(games):
                board = game.board()
                game_analysis = {
                    "game_index": game_idx,
                    "white": game.headers.get("White", "Unknown"),
                    "black": game.headers.get("Black", "Unknown"),
                    "result": game.headers.get("Result", "*"),
                    "source": request.source,
                    "moves": []
                }
                
                ply = 0
                for move in game.mainline_moves():
                    ply += 1
                    
                    # Get current position FEN
                    current_fen = board.fen()
                    
                    # Get Stockfish analysis of current position with multi-PV for top 3 moves
                    current_analysis = engine.analyse(board, chess.engine.Limit(depth=request.depth), multipv=3)
                    
                    # Get best move from current position (first PV)
                    best_move = ""
                    top_moves = []
                    
                    # Handle the fact that multipv=3 returns a list of analysis objects
                    if isinstance(current_analysis, list):
                        analysis_list = current_analysis
                    else:
                        # If it's a single analysis object, wrap it in a list
                        analysis_list = [current_analysis]
                    
                    # Extract top 3 moves with evaluations
                    for i, analysis in enumerate(analysis_list):
                        if "pv" in analysis and analysis["pv"]:
                            move_uci = str(analysis["pv"][0])
                            score = analysis.get("score")
                            
                            move_info = {
                                "move": move_uci,
                                "rank": i + 1,
                                "evaluation": {}
                            }
                            
                            if score:
                                score_white = score.white()
                                if score_white.is_mate():
                                    move_info["evaluation"] = {"type": "mate", "value": score_white.mate()}
                                else:
                                    move_info["evaluation"] = {"type": "cp", "value": score_white.score()}
                            
                            top_moves.append(move_info)
                            
                            if i == 0:  # First move is the best move
                                best_move = move_uci
                    
                    # Calculate move quality by comparing played move with best move
                    is_best_move = str(move) == best_move
                    
                    # Make the actual move to get evaluation after
                    board.push(move)
                    actual_move_analysis = engine.analyse(board, chess.engine.Limit(depth=request.depth))
                    
                    # Get evaluation after the actual move
                    eval_data = {}
                    if "score" in actual_move_analysis:
                        score = actual_move_analysis["score"].white()
                        if score.is_mate():
                            eval_data = {"type": "mate", "value": score.mate()}
                        else:
                            eval_data = {"type": "cp", "value": score.score()}
                    
                    # Calculate REAL centipawn loss using Stockfish evaluations
                    centipawn_loss = 0
                    if not is_best_move:
                        # Get evaluation of best move by temporarily playing it
                        board.pop()  # Undo the actual move
                        
                        try:
                            # Play the best move
                            best_move_obj = chess.Move.from_uci(best_move)
                            board.push(best_move_obj)
                            best_analysis = engine.analyse(board, chess.engine.Limit(depth=max(10, request.depth-2)))
                            board.pop()  # Undo best move
                            
                            # Restore actual move
                            board.push(move)
                            
                            # Compare evaluations
                            if "score" in best_analysis and "score" in actual_move_analysis:
                                best_score = best_analysis["score"].white()
                                actual_score = actual_move_analysis["score"].white()
                                
                                if not best_score.is_mate() and not actual_score.is_mate():
                                    best_eval = best_score.score()
                                    actual_eval = actual_score.score()
                                    
                                    # Calculate centipawn loss from player's perspective
                                    if ply % 2 == 1:  # White's move
                                        centipawn_loss = max(0, best_eval - actual_eval)
                                    else:  # Black's move
                                        centipawn_loss = max(0, actual_eval - best_eval)
                        except Exception as e:
                            # If analysis fails, estimate based on position
                            print(f"Stockfish analysis failed: {e}")
                            centipawn_loss = 25 if not is_best_move else 0
                    
                    # Get move quality based on actual comparison
                    quality = get_move_quality(centipawn_loss, is_best_move)
                    
                    # Analyze tactical patterns in the position BEFORE the move
                    tactical_patterns = tactical_analyzer.analyze_position(chess.Board(current_fen))
                    tactical_summary = summarize_tactical_patterns(tactical_patterns) if tactical_patterns else None
                    
                    move_analysis = {
                        "ply": ply,
                        "uci_move": str(move),
                        "fen": current_fen,
                        "best_move": best_move,
                        "top_moves": top_moves,  # Add top 3 moves with evaluations
                        "evaluation": eval_data,
                        "quality": quality,
                        "centipawn_loss": centipawn_loss,
                        "tactical_patterns": tactical_summary  # Add tactical analysis
                    }
                    
                    game_analysis["moves"].append(move_analysis)
                    
                    # The move is already made (don't pop it since we need board progression)
                
                # Add opening analysis
                opening_info = opening_db.identify_opening(game_analysis["moves"])
                if opening_info:
                    game_analysis["opening"] = opening_info
                else:
                    game_analysis["opening"] = {
                        "name": "Unknown Opening",
                        "eco": "A00",
                        "category": "Unknown",
                        "moves_played": 0
                    }
                
                # Generate player-separated reviews for this game
                player_reviews = generate_player_reviews(game_analysis["moves"], game_analysis)
                game_analysis["player_reviews"] = player_reviews
                
                # Generate legacy reviews for backward compatibility
                review = generate_reviews(game_analysis["moves"], game_analysis)
                game_analysis["review"] = review.model_dump()
                
                results.append(game_analysis)
        
        # Prepare final result
        final_result = {
            "games": results,
            "username": request.username,
            "source": request.source,
            "analysis_hash": pgn_hash,
            "analyzed_at": datetime.now().isoformat()
        }
        
        # Record performance and check for achievements
        try:
            achievements = []
            for game in results:
                game_achievements = performance_tracker.record_game_performance(game)
                achievements.extend(game_achievements)
            
            if achievements:
                final_result["achievements"] = achievements
        except Exception as e:
            print(f"Performance tracking error: {e}")  # Log but don't fail
        
        # Cache the result
        with open(cache_path, 'w') as f:
            json.dump(final_result, f, indent=2)
        
        return final_result
        
    except requests.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            if e.response.status_code in [429, 403]:
                raise HTTPException(status_code=502, detail=f"Rate limited by {request.source}. Please try again in a few minutes.")
            elif e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="No games found for user")
        raise HTTPException(status_code=502, detail=f"Failed to fetch games from {request.source}: {str(e)}")
    except chess.engine.EngineError as e:
        raise HTTPException(status_code=500, detail=f"Stockfish engine error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Opening Analysis Endpoints
@app.get("/openings/popular")
def get_popular_openings():
    """Get list of most popular openings"""
    return opening_db.get_popular_openings()

@app.get("/openings/suggestions/{username}")
def get_opening_suggestions(username: str, color: str = "white"):
    """Get opening suggestions for a user"""
    return opening_db.suggest_openings(username, color)

# Performance Tracking Endpoints
@app.get("/performance/{username}")
def get_user_performance(username: str, days: int = 30):
    """Get comprehensive performance statistics for a user"""
    try:
        stats = performance_tracker.get_user_stats(username, days)
        return {
            "username": username,
            "period_days": days,
            "stats": stats.__dict__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance stats: {str(e)}")

@app.get("/performance/{username}/trends")
def get_performance_trends(username: str):
    """Get improvement trends over time"""
    try:
        trends = performance_tracker.get_improvement_trends(username)
        return {
            "username": username,
            "trends": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance trends: {str(e)}")

@app.get("/performance/{username}/openings")
def get_opening_performance(username: str, eco: str = None):
    """Get performance statistics for specific openings"""
    try:
        opening_stats = performance_tracker.get_opening_performance(username, eco)
        return {
            "username": username,
            "opening_eco": eco,
            "stats": opening_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get opening performance: {str(e)}")

@app.get("/leaderboard")
def get_leaderboard(metric: str = "accuracy", period_days: int = 30, limit: int = 10):
    """Get leaderboard for various metrics"""
    # This would require aggregating data across all users
    # For now, return a placeholder
    return {
        "metric": metric,
        "period_days": period_days,
        "leaderboard": [],
        "message": "Leaderboard feature coming soon!"
    }

@app.get("/openings/stats/{username}/{opening_name}")
def get_opening_stats(username: str, opening_name: str):
    """Get user's performance in a specific opening"""
    return opening_db.get_opening_stats(username, opening_name)

# Legacy endpoint for backward compatibility
@app.post("/analyze/lichess")
async def analyze_lichess_games(request: AnalysisRequest) -> Dict[str, Any]:
    """Legacy endpoint - use /analyze instead"""
    request.source = "lichess"
    return await analyze_games(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
