from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import chess
import chess.engine
import chess.pgn
from io import StringIO
from typing import List, Dict, Any, Optional

app = FastAPI()

STOCKFISH_PATH = r"C:\stockfish\stockfish.exe"

class AnalysisRequest(BaseModel):
    username: str
    max: int = 10
    depth: int = 12

class MoveAnalysis(BaseModel):
    ply: int
    uci_move: str
    fen: str
    best_move: str
    evaluation: Dict[str, Any]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/analyze/lichess")
async def analyze_lichess_games(request: AnalysisRequest) -> List[Dict[str, Any]]:
    """
    Analyze recent games from a Lichess user using Stockfish
    """
    try:
        # Fetch recent games from Lichess API
        lichess_url = f"https://lichess.org/api/games/user/{request.username}"
        params = {
            "max": request.max,
            "format": "pgn",
            "rated": "true"
        }
        
        response = requests.get(lichess_url, params=params)
        response.raise_for_status()
        
        games_pgn = response.text
        if not games_pgn.strip():
            raise HTTPException(status_code=404, detail="No games found for user")
        
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
                
                results.append(game_analysis)
        
        return results
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch games from Lichess: {str(e)}")
    except chess.engine.EngineError as e:
        raise HTTPException(status_code=500, detail=f"Stockfish engine error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)