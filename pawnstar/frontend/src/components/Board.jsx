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
    
    // Explicit mapping for white and black pieces
    const pieceMap = {
      // White pieces (uppercase)
      'K': '/pieces/wK.svg',
      'Q': '/pieces/wQ_new.svg', 
      'R': '/pieces/wR_new.svg',
      'B': '/pieces/wB_new.svg',
      'N': '/pieces/wN_new.svg',
      'P': '/pieces/wP_new.svg',
      // Black pieces (lowercase)
      'k': '/pieces/bK.svg',
      'q': '/pieces/bQ_cburnett.svg',
      'r': '/pieces/bR_cburnett.svg', 
      'b': '/pieces/bB_cburnett.svg',
      'n': '/pieces/bN_cburnett.svg',
      'p': '/pieces/bP_cburnett.svg'
    };
    
    return pieceMap[piece] || `/pieces/${piece}.svg`;
  };

  const isLightSquare = (row, col) => (row + col) % 2 === 0;

  return (
    <div className="flex justify-center">
      <div className="inline-block bg-surface p-6 rounded-xl shadow-2xl border border-gray-600">
        <div className="relative">
          <div className="grid grid-cols-8 gap-0 border-4 border-gray-700 rounded-lg overflow-hidden shadow-inner">
            {board.map((rank, rankIndex) =>
              rank.map((piece, fileIndex) => (
                <div
                  key={`${rankIndex}-${fileIndex}`}
                  className={`
                    w-12 h-12 sm:w-16 sm:h-16 lg:w-18 lg:h-18 flex items-center justify-center
                    transition-all duration-300 cursor-pointer hover:brightness-110 relative
                    ${isLightSquare(rankIndex, fileIndex) 
                      ? 'bg-gradient-to-br from-amber-50 to-amber-100' 
                      : 'bg-gradient-to-br from-amber-700 to-amber-900'
                    }
                  `}
                >
                  {piece && (
                    <img 
                      src={getPieceImage(piece)}
                      alt={piece}
                      className="chess-piece w-10 h-10 sm:w-12 sm:h-12 lg:w-14 lg:h-14 object-contain select-none transition-transform duration-200 hover:scale-110 drop-shadow-lg"
                      draggable={false}
                    />
                  )}
                </div>
              ))
            )}
          </div>
        </div>
        
        {/* Coordinates */}
        <div className="flex justify-between mt-3 px-1">
          {['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'].map(file => (
            <span key={file} className="text-sm font-medium text-gray-300 w-12 sm:w-16 lg:w-18 text-center">
              {file}
            </span>
          ))}
        </div>
        
        <div className="absolute left-0 top-0 flex flex-col justify-between h-full py-6">
          {[8, 7, 6, 5, 4, 3, 2, 1].map(rank => (
            <span key={rank} className="text-sm font-medium text-gray-300 h-12 sm:h-16 lg:h-18 flex items-center pr-3">
              {rank}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Board;