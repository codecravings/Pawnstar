import React from 'react';

const Board = ({ fen, moves, currentMoveIndex }) => {
  // Parse FEN to get board position
  const parseFen = (fen) => {
    const [position] = fen.split(' ');
    const ranks = position.split('/');
    const board = [];
    
    ranks.forEach(rank => {
      const row = [];
      for (let char of rank) {
        if (isNaN(char)) {
          row.push(char);
        } else {
          for (let i = 0; i < parseInt(char); i++) {
            row.push(null);
          }
        }
      }
      board.push(row);
    });
    
    return board;
  };

  const board = parseFen(fen);

  const getPieceImage = (piece) => {
    if (!piece) return null;
    return `/pieces/${piece}.svg`;
  };

  const isLightSquare = (row, col) => (row + col) % 2 === 0;

  return (
    <div className="flex justify-center">
      <div className="inline-block bg-surface p-4 rounded-lg shadow-lg">
        <div className="grid grid-cols-8 gap-0 border-2 border-gray-600 rounded overflow-hidden">
          {board.map((rank, rankIndex) =>
            rank.map((piece, fileIndex) => (
              <div
                key={`${rankIndex}-${fileIndex}`}
                className={`
                  w-12 h-12 sm:w-16 sm:h-16 flex items-center justify-center text-2xl sm:text-4xl
                  transition-all duration-300 cursor-pointer hover:brightness-110
                  ${isLightSquare(rankIndex, fileIndex) 
                    ? 'bg-amber-100' 
                    : 'bg-amber-800'
                  }
                `}
              >
                {piece && (
                  <img 
                    src={getPieceImage(piece)}
                    alt={piece}
                    className="chess-piece w-8 h-8 sm:w-12 sm:h-12 object-contain select-none transition-transform duration-200 hover:scale-110"
                    draggable={false}
                  />
                )}
              </div>
            ))
          )}
        </div>
        
        {/* Coordinates */}
        <div className="flex justify-between mt-2 px-1">
          {['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].map(file => (
            <span key={file} className="text-xs text-gray-400 w-12 sm:w-16 text-center">
              {file}
            </span>
          ))}
        </div>
        
        <div className="absolute left-0 top-0 flex flex-col justify-between h-full py-4">
          {[8, 7, 6, 5, 4, 3, 2, 1].map(rank => (
            <span key={rank} className="text-xs text-gray-400 h-12 sm:h-16 flex items-center pr-2">
              {rank}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Board;