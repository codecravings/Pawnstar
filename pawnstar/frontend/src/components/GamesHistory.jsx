import React, { useState, useEffect } from 'react';

const GamesHistory = ({ username, source, onAnalyzeGame }) => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchGames = async () => {
    if (!username) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`http://127.0.0.1:8000/games?username=${encodeURIComponent(username)}&source=${source}&max_games=20`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch games: ${response.status}`);
      }
      
      const gamesData = await response.json();
      setGames(gamesData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGames();
  }, [username, source]);

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Unknown';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    } catch {
      return dateStr;
    }
  };

  const getResultColor = (result, white, black, currentUser) => {
    if (result === '1/2-1/2') return 'text-yellow-400';
    
    const isWhite = white.toLowerCase() === currentUser.toLowerCase();
    const won = (result === '1-0' && isWhite) || (result === '0-1' && !isWhite);
    
    return won ? 'text-green-400' : 'text-red-400';
  };

  const getResultText = (result) => {
    switch(result) {
      case '1-0': return 'White won';
      case '0-1': return 'Black won';
      case '1/2-1/2': return 'Draw';
      default: return result;
    }
  };

  if (loading) {
    return (
      <div className="bg-surface rounded-lg p-4">
        <h3 className="text-lg font-semibold text-primary mb-4">Recent Games</h3>
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent"></div>
          <span className="ml-3 text-secondary">Loading games...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-surface rounded-lg p-4">
        <h3 className="text-lg font-semibold text-primary mb-4">Recent Games</h3>
        <div className="text-red-400 text-center py-4">
          Error: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-gradient-to-br from-surface to-gray-800 rounded-xl p-5 shadow-lg border border-gray-600">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold text-accent flex items-center">
          🕒 Recent Games
        </h3>
        <button 
          onClick={fetchGames}
          className="text-sm text-accent hover:text-accent-light transition-colors px-3 py-1 bg-background rounded-lg hover:bg-gray-700"
        >
          🔄 Refresh
        </button>
      </div>
      
      {games.length === 0 ? (
        <div className="text-secondary text-center py-4">
          No games found
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {games.map((game, index) => (
            <div key={index} className="bg-gradient-to-r from-background to-gray-800 rounded-lg p-4 hover:from-gray-700 hover:to-gray-600 transition-all duration-200 border border-gray-600 shadow-md">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 text-sm">
                    <span className="text-primary font-medium">{game.white}</span>
                    <span className="text-secondary">vs</span>
                    <span className="text-primary font-medium">{game.black}</span>
                  </div>
                  
                  <div className="flex items-center space-x-4 mt-1 text-xs text-secondary">
                    <span>{formatDate(game.date)}</span>
                    <span>{game.time_control}</span>
                    {game.opening && <span className="truncate max-w-32">{game.opening}</span>}
                  </div>
                </div>
                
                <div className="text-right">
                  <div className={`text-sm font-medium ${getResultColor(game.result, game.white, game.black, username)}`}>
                    {getResultText(game.result)}
                  </div>
                  <div className="flex flex-col space-y-1 mt-1">
                    {game.url && (
                      <a 
                        href={game.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-xs text-accent hover:text-accent-light transition-colors"
                      >
                        View Game
                      </a>
                    )}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onAnalyzeGame && onAnalyzeGame(game);
                      }}
                      className="text-xs text-green-400 hover:text-green-300 transition-colors"
                    >
                      🔍 Analyze
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default GamesHistory;