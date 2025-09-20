import React, { useState, useEffect } from 'react';

const MemeOverlay = () => {
  const [memeUrl, setMemeUrl] = useState('');
  
  const blunderMemes = [
    'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="%23FF6B6B"/><text x="100" y="100" font-family="Arial" font-size="20" fill="white" text-anchor="middle" dominant-baseline="middle">BLUNDER!</text><text x="100" y="130" font-family="Arial" font-size="14" fill="white" text-anchor="middle" dominant-baseline="middle">😱</text></svg>',
    'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="%23FF6B6B"/><text x="100" y="80" font-family="Arial" font-size="16" fill="white" text-anchor="middle" dominant-baseline="middle">OOPS!</text><text x="100" y="120" font-family="Arial" font-size="40" fill="white" text-anchor="middle" dominant-baseline="middle">🤦</text><text x="100" y="160" font-family="Arial" font-size="12" fill="white" text-anchor="middle" dominant-baseline="middle">That was not the move</text></svg>',
    'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="%23FF6B6B"/><text x="100" y="70" font-family="Arial" font-size="14" fill="white" text-anchor="middle" dominant-baseline="middle">MAJOR BLUNDER</text><text x="100" y="120" font-family="Arial" font-size="50" fill="white" text-anchor="middle" dominant-baseline="middle">💥</text><text x="100" y="160" font-family="Arial" font-size="12" fill="white" text-anchor="middle" dominant-baseline="middle">Stockfish is disappointed</text></svg>'
  ];
  
  useEffect(() => {
    // Try to load from assets/memes first, fallback to built-in memes
    const randomMeme = blunderMemes[Math.floor(Math.random() * blunderMemes.length)];
    setMemeUrl(randomMeme);
  }, []);
  
  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none">
      <div className="bg-black/70 p-6 rounded-lg animate-pulse">
        <img 
          src={memeUrl} 
          alt="Blunder meme" 
          className="w-48 h-48 object-contain rounded"
          onError={(e) => {
            // Fallback to text if image fails
            e.target.style.display = 'none';
            e.target.nextSibling.style.display = 'block';
          }}
        />
        <div 
          className="w-48 h-48 bg-danger rounded flex items-center justify-center text-white text-center hidden"
        >
          <div>
            <div className="text-4xl mb-2">😱</div>
            <div className="text-xl font-bold">BLUNDER!</div>
            <div className="text-sm">That was not optimal</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MemeOverlay;