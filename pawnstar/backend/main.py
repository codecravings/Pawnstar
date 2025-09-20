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

# Load environment variables
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
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

def generate_reviews(moves: List[Dict[str, Any]], game_data: Dict[str, Any]) -> GameReview:
    """Generate game review with blunders, accuracy, and summary."""
    blunders = []
    total_moves = len(moves)
    total_centipawn_loss = 0
    
    for i, move in enumerate(moves):
        if move.get("evaluation") and move["evaluation"].get("type") == "cp":
            current_eval = move["evaluation"]["value"]
            
            # Check if this is a blunder (significant eval drop)
            if i > 0:
                prev_move = moves[i-1]
                if prev_move.get("evaluation") and prev_move["evaluation"].get("type") == "cp":
                    prev_eval = prev_move["evaluation"]["value"]
                    eval_swing = abs(current_eval - prev_eval)
                    
                    if eval_swing >= 150:
                        blunders.append({
                            "ply": move["ply"],
                            "move": move["uci_move"],
                            "eval_before": prev_eval,
                            "eval_after": current_eval,
                            "centipawn_loss": eval_swing
                        })
                        total_centipawn_loss += eval_swing
    
    # Calculate accuracy estimate (simplified)
    accuracy = max(0, 100 - (total_centipawn_loss / max(total_moves, 1)) / 10)
    
    # Generate summary
    blunder_count = len(blunders)
    if blunder_count == 0:
        summary = f"Excellent game! No major blunders detected. Accuracy: {accuracy:.1f}%"
    elif blunder_count <= 2:
        summary = f"Good game with {blunder_count} blunder(s). Accuracy: {accuracy:.1f}%"
    else:
        summary = f"Challenging game with {blunder_count} blunders. Accuracy: {accuracy:.1f}%"
    
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
        
        # Check cache first
        pgn_hash = get_cache_key(games_pgn)
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
                    
                    # Get Stockfish analysis
                    info = engine.analyse(board, chess.engine.Limit(depth=request.depth))
                    
                    # Extract evaluation
                    eval_data = {}
                    if "score" in info:
                        score = info["score"].white()
                        if score.is_mate():
                            eval_data = {"type": "mate", "value": score.mate()}
                        else:
                            eval_data = {"type": "cp", "value": score.score()}
                    
                    # Get best move
                    best_move = ""
                    if "pv" in info and info["pv"]:
                        best_move = str(info["pv"][0])
                    
                    move_analysis = {
                        "ply": ply,
                        "uci_move": str(move),
                        "fen": current_fen,
                        "best_move": best_move,
                        "evaluation": eval_data
                    }
                    
                    game_analysis["moves"].append(move_analysis)
                    
                    # Make the move
                    board.push(move)
                
                # Generate reviews for this game
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

# Legacy endpoint for backward compatibility
@app.post("/analyze/lichess")
async def analyze_lichess_games(request: AnalysisRequest) -> Dict[str, Any]:
    """Legacy endpoint - use /analyze instead"""
    request.source = "lichess"
    return await analyze_games(request)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)