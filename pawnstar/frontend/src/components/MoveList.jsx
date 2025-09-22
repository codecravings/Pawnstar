import React from 'react';

const MoveList = ({ moves, currentIndex, onMoveSelect, topBlunders = [] }) => {
  if (!moves || moves.length === 0) {
    return (
      <div className="text-gray-400 text-sm text-center py-4">
        No moves to display
      </div>
    );
  }

  const getQualityBadge = (move) => {
    if (!move.quality) return null;
    
    const quality = move.quality;
    const colors = {
      brilliant: 'bg-gradient-to-r from-yellow-400 to-orange-500 text-black',
      best: 'bg-gradient-to-r from-blue-500 to-purple-600 text-white',
      excellent: 'bg-green-500 text-white',
      good: 'bg-green-400 text-white',
      ok: 'bg-gray-500 text-white',
      inaccuracy: 'bg-yellow-500 text-black',
      mistake: 'bg-orange-500 text-white',
      blunder: 'bg-red-600 text-white',
      catastrophe: 'bg-gradient-to-r from-red-600 to-black text-white animate-pulse'
    };
    
    return (
      <span className={`text-xs px-1 py-0.5 rounded ml-2 ${colors[quality.category] || 'bg-gray-500 text-white'}`}>
        {quality.emoji} {quality.category.toUpperCase()}
      </span>
    );
  };

  const formatEval = (evaluation) => {
    if (!evaluation) return '0.00';
    
    if (evaluation.type === 'mate') {
      return `M${evaluation.value}`;
    } else if (evaluation.type === 'cp') {
      return (evaluation.value / 100).toFixed(2);
    }
    
    return '0.00';
  };

  return (
    <div className="max-h-64 overflow-y-auto space-y-1">
      {moves.map((move, index) => {
        const isSelected = index === currentIndex;
        const qualityBadge = getQualityBadge(move);
        
        return (
          <div
            key={index}
            onClick={() => onMoveSelect(index)}
            className={`
              p-2 rounded cursor-pointer transition-all duration-200
              ${isSelected 
                ? 'bg-primary text-white' 
                : 'bg-bg hover:bg-gray-700'
              }
            `}
            title={move.quality ? move.quality.description : ''}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <span className="font-mono text-sm">
                  {Math.floor(move.ply / 2) + 1}{move.ply % 2 === 1 ? '.' : '...'} {move.uci_move}
                </span>
                {qualityBadge}
              </div>
              
              <div className="text-xs">
                <span className={`font-mono ${
                  move.evaluation && move.evaluation.type === 'cp' && move.evaluation.value > 0 
                    ? 'text-green-400' 
                    : 'text-red-400'
                }`}>
                  {formatEval(move.evaluation)}
                </span>
              </div>
            </div>
            
            {move.best_move && move.best_move !== move.uci_move && (
              <div className="text-xs text-gray-400 mt-1">
                Best: {move.best_move}
              </div>
            )}
            
            {move.quality && (
              <div className="text-xs text-gray-300 mt-1 italic">
                {move.quality.description}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default MoveList;