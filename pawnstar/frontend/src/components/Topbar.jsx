import React, { useState, useEffect, useCallback, useRef } from 'react';

const Topbar = ({ onAnalyze, loading, darkMode, onToggleDarkMode }) => {
  const [username, setUsername] = useState(() => localStorage.getItem('pawnstar_username') || '');
  const [source, setSource] = useState(() => localStorage.getItem('pawnstar_source') || 'lichess');
  const [autoWatch, setAutoWatch] = useState(false);
  const [lastHash, setLastHash] = useState('');
  const [toast, setToast] = useState('');
  const debounceRef = useRef(null);
  const pollIntervalRef = useRef(null);

  const checkLatestGame = useCallback(async (user, src) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/latest-game?username=${encodeURIComponent(user)}&source=${encodeURIComponent(src)}`);
      if (response.ok) {
        const data = await response.json();
        if (lastHash && data.latest_hash !== lastHash) {
          // New game detected
          setToast('New game found — analyzing...');
          setTimeout(() => setToast(''), 3000);
          onAnalyze(user, src);
        }
        setLastHash(data.latest_hash);
      }
    } catch (error) {
      console.log('Failed to check latest game:', error);
    }
  }, [lastHash, onAnalyze]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (username.trim() && !loading) {
      onAnalyze(username.trim(), source);
    }
  };

  // Auto-watch polling
  useEffect(() => {
    if (autoWatch && username.trim()) {
      pollIntervalRef.current = setInterval(() => {
        checkLatestGame(username.trim(), source);
      }, 30000);
    } else {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [autoWatch, username, source, checkLatestGame]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  return (
    <div className="bg-surface border-b border-gray-700 px-4 py-3">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold text-primary">Pawnstar</h1>
          
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <select 
              value={source}
              onChange={(e) => {
                setSource(e.target.value);
                localStorage.setItem('pawnstar_source', e.target.value);
              }}
              className="bg-bg border border-gray-600 rounded px-2 py-1 text-sm text-text focus:outline-none focus:border-primary"
            >
              <option value="lichess">Lichess</option>
              <option value="chess.com">Chess.com</option>
            </select>
            
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => {
                const newUsername = e.target.value;
                setUsername(newUsername);
                localStorage.setItem('pawnstar_username', newUsername);
                
                // Debounce latest game check
                if (debounceRef.current) {
                  clearTimeout(debounceRef.current);
                }
                debounceRef.current = setTimeout(() => {
                  if (newUsername.trim()) {
                    checkLatestGame(newUsername.trim(), source);
                  }
                }, 500);
              }}
              className="bg-bg border border-gray-600 rounded px-3 py-1 text-text placeholder-gray-400 focus:outline-none focus:border-primary"
              disabled={loading}
            />
            
            <button
              type="submit"
              disabled={!username.trim() || loading}
              className="bg-primary hover:bg-primary/80 disabled:bg-gray-600 disabled:cursor-not-allowed px-4 py-1 rounded text-white font-medium transition-colors"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  Analyzing...
                </div>
              ) : (
                'Analyze'
              )}
            </button>
            
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={autoWatch}
                onChange={(e) => setAutoWatch(e.target.checked)}
                className="rounded"
              />
              <span className="text-text">Auto-watch</span>
            </label>
          </form>
        </div>

        {toast && (
          <div className="fixed top-4 right-4 bg-accent text-black px-4 py-2 rounded-lg shadow-lg z-50">
            {toast}
          </div>
        )}

        <button
          onClick={onToggleDarkMode}
          className="p-2 rounded-lg bg-bg hover:bg-gray-700 transition-colors"
          title="Toggle dark mode"
        >
          {darkMode ? (
            <svg className="w-5 h-5 text-accent" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
            </svg>
          ) : (
            <svg className="w-5 h-5 text-accent" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
};

export default Topbar;