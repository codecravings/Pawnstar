import React, { useState } from 'react';
import Topbar from './components/Topbar';
import Board from './components/Board';
import MoveList from './components/MoveList';
import EvalGraph from './components/EvalGraph';
import MemeOverlay from './components/MemeOverlay';

function App() {
  const [gameData, setGameData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [currentMoveIndex, setCurrentMoveIndex] = useState(0);
  const [showMeme, setShowMeme] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  const handleAnalyze = async (username, source = 'lichess') => {
    setLoading(true);
    setError('');
    setGameData(null);
    
    try {
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

      <div className="flex flex-col lg:flex-row min-h-[calc(100vh-4rem)]">
        {/* Board Column */}
        <div className="flex-1 p-4">
          <Board 
            fen={currentFen}
            moves={gameData?.moves || []}
            currentMoveIndex={currentMoveIndex}
          />
        </div>

        {/* Sidebar */}
        <div className="w-full lg:w-96 p-4 space-y-4">
          <div className="bg-surface rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 text-accent">Evaluation</h3>
            <EvalGraph values={evalValues} />
          </div>
          
          <div className="bg-surface rounded-lg p-4">
            <h3 className="text-lg font-semibold mb-3 text-accent">Moves</h3>
            <MoveList 
              moves={gameData?.moves || []}
              currentIndex={currentMoveIndex}
              onMoveSelect={setCurrentMoveIndex}
              topBlunders={gameData?.review?.top_blunders || []}
            />
          </div>
          
          {gameData?.review && (
            <div className="bg-surface rounded-lg p-4">
              <h3 className="text-lg font-semibold mb-3 text-accent">Analysis</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Accuracy:</span>
                  <span className="font-semibold text-accent">{gameData.review.accuracy_estimate}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Blunders:</span>
                  <span className="font-semibold text-danger">{gameData.review.top_blunders.length}</span>
                </div>
                <p className="mt-3 text-gray-300">{gameData.review.summary_text}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {showMeme && <MemeOverlay />}
    </div>
  );
}

export default App;