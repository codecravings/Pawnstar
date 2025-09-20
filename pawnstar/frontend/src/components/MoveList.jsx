import React from 'react';

const MoveList = ({ moves, currentIndex, onMoveSelect }) => {
  if (!moves || moves.length === 0) {
    return (
      <div className="text-gray-400 text-sm text-center py-4">
        No moves to display
      </div>
    );
  }

  const getEvalBadge = (evaluation, prevEvaluation) => {
    if (!evaluation || evaluation.type !== 'cp') return null;
    
    const currentEval = evaluation.value;
    const prevEval = prevEvaluation && prevEvaluation.type === 'cp' ? prevEvaluation.value : 0;
    const swing = Math.abs(currentEval - prevEval);
    
    if (Math.abs(currentEval) >= 150 || swing >= 150) {
      return <span className="text-xs bg-danger px-1 py-0.5 rounded text-white ml-2">Blunder</span>;
    } else if (swing >= 100) {
      return <span className="text-xs bg-orange-500 px-1 py-0.5 rounded text-white ml-2">Mistake</span>;
    } else if (swing >= 50) {
      return <span className="text-xs bg-yellow-500 px-1 py-0.5 rounded text-black ml-2">Inaccuracy</span>;
    }
    
    return null;
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
        const isBlunder = move.evaluation && move.evaluation.type === 'cp' && Math.abs(move.evaluation.value) >= 150;
        const prevMove = index > 0 ? moves[index - 1] : null;
        const badge = getEvalBadge(move.evaluation, prevMove?.evaluation);
        
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
              ${isBlunder && !isSelected ? 'blunder-pulse' : ''}
            `}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <span className="font-mono text-sm">
                  {Math.floor(move.ply / 2) + 1}{move.ply % 2 === 1 ? '.' : '...'} {move.uci_move}
                </span>
                {badge}
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
          </div>
        );
      })}
    </div>
  );
};

export default MoveList;