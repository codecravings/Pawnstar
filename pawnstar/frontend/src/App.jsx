import React, { useState } from 'react';
import Topbar from './components/Topbar';
import Board from './components/Board';
import MoveList from './components/MoveList';
import EvalGraph from './components/EvalGraph';
import MemeOverlay from './components/MemeOverlay';
import GamesHistory from './components/GamesHistory';
import LoadingScreen from './components/LoadingScreen';
import PlayerComparison from './components/PlayerComparison';
import TabbedSidebar from './components/TabbedSidebar';

function App() {
  const [gameData, setGameData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentMoveIndex, setCurrentMoveIndex] = useState(0);
  const [showMeme, setShowMeme] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [currentUsername, setCurrentUsername] = useState('');
  const [currentSource, setCurrentSource] = useState('lichess');
  const [loadingMessage, setLoadingMessage] = useState('Analyzing your game...');

  const analyzeSpecificGame = async (gameInfo) => {
    setLoading(true);
    setLoadingMessage('🎯 Fetching individual game...');
    setError('');
    setGameData(null);
    setCurrentMoveIndex(0);
    
    try {
      const gameUrl = gameInfo.url;
      if (!gameUrl) {
        throw new Error('Game URL not available for analysis');
      }
      
      setLoadingMessage('🧠 Deep analyzing with Stockfish...');
      
      // Use the new analyze-game endpoint
      const response = await fetch('http://127.0.0.1:8000/analyze-game', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          game_url: gameUrl
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Analysis failed: ${response.status}`);
      }

      const data = await response.json();
      if (data.games && data.games.length > 0) {
        setGameData(data.games[0]);
        setCurrentMoveIndex(0);
      } else {
        throw new Error('No game data received');
      }
    } catch (err) {
      setError(`Failed to analyze game: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyze = async (username, source = 'lichess') => {
    setLoading(true);
    setLoadingMessage('🔍 Fetching latest games...');
    setError('');
    setGameData(null);
    setCurrentUsername(username);
    setCurrentSource(source);
    
    try {
      setLoadingMessage('🧠 Running deep Stockfish analysis...');
      
      const response = await fetch('http://127.0.0.1:8000/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username,
          source,
          max: 1,
          depth: 12
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      if (data && data.games && data.games.length > 0) {
        setGameData(data.games[0]);
        setCurrentMoveIndex(0);
        
        // Check for blunders and show meme overlay
        const moves = data.games[0].moves || [];
        const hasBlunder = moves.some(move => {
          const evaluation = move.evaluation;
          if (evaluation && evaluation.type === 'cp') {
            return Math.abs(evaluation.value) >= 150;
          }
          return false;
        });
        
        if (hasBlunder) {
          setShowMeme(true);
          setTimeout(() => setShowMeme(false), 3000);
        }
      }
    } catch (err) {
      setError(`Failed to analyze games: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode;
    setDarkMode(newDarkMode);
    localStorage.setItem('darkMode', newDarkMode.toString());
    
    if (newDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const currentFen = gameData && gameData.moves && gameData.moves[currentMoveIndex] 
    ? gameData.moves[currentMoveIndex].fen 
    : 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1';

  const evalValues = gameData && gameData.moves 
    ? gameData.moves.map(move => {
        if (move.evaluation && move.evaluation.type === 'cp') {
          return move.evaluation.value;
        }
        return 0;
      })
    : [];

  return (
    <div className="min-h-screen bg-bg text-text">
      <Topbar 
        onAnalyze={handleAnalyze} 
        loading={loading}
        darkMode={darkMode}
        onToggleDarkMode={toggleDarkMode}
      />
      
      {error && (
        <div className="mx-4 mt-4 p-3 bg-danger/20 border border-danger rounded-lg text-danger">
          {error}
        </div>
      )}

      <div className="flex flex-col xl:flex-row min-h-[calc(100vh-4rem)] gap-6 p-4">
        {/* Board Column */}
        <div className="flex-1 flex justify-center items-start">
          <Board 
            fen={currentFen}
            moves={gameData?.moves || []}
            currentMoveIndex={currentMoveIndex}
          />
        </div>

        {/* Sidebar */}
        <div className="w-full xl:w-96 space-y-6">
          {/* Player Comparison - New Component */}
          {gameData?.player_reviews && (
            <PlayerComparison gameData={gameData} />
          )}
          
          {/* Tabbed Interface */}
          <TabbedSidebar 
            gameData={gameData}
            evalValues={evalValues}
            currentMoveIndex={currentMoveIndex}
            onMoveSelect={setCurrentMoveIndex}
            currentUsername={currentUsername}
            currentSource={currentSource}
            onAnalyzeGame={analyzeSpecificGame}
          />
        </div>
      </div>

      {showMeme && <MemeOverlay />}
      {loading && <LoadingScreen message={loadingMessage} />}
    </div>
  );
}

export default App;