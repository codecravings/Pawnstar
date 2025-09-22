import React from 'react';

const PlayerComparison = ({ gameData }) => {
  if (!gameData?.player_reviews) {
    return null;
  }

  const { white: whiteReview, black: blackReview } = gameData.player_reviews;
  const whiteName = gameData.white || 'White';
  const blackName = gameData.black || 'Black';

  // Get ELO ratings from game headers if available
  const whiteElo = gameData.white_elo || '400';
  const blackElo = gameData.black_elo || '450';

  const AccuracyDisplay = ({ accuracy, player }) => (
    <div className="text-center">
      <div className="bg-white text-black rounded-lg p-3 mb-2 min-w-[80px]">
        <span className="text-2xl font-bold">{accuracy}</span>
      </div>
      <div className="relative">
        {/* Accuracy Bar */}
        <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden mx-auto">
          <div className="h-full bg-gradient-to-r from-green-500 to-red-500" />
        </div>
        {/* Accuracy markers */}
        <div className="flex justify-between text-xs text-gray-400 mt-1 w-20 mx-auto">
          <span className="text-green-400">{Math.round(accuracy)}</span>
          <span className="text-red-400">{Math.round(100 - accuracy)}</span>
        </div>
      </div>
    </div>
  );

  const EloDisplay = ({ elo }) => (
    <div className="bg-gray-700 rounded-lg p-3 text-center min-w-[80px]">
      <span className="text-2xl font-bold text-white">{elo}</span>
    </div>
  );

  const MoveQualityRow = ({ category, whiteCount, blackCount, icon, color, label }) => (
    <div className="flex items-center justify-between text-sm py-1">
      <div className="flex items-center gap-2 flex-1">
        <span className="text-lg">{icon}</span>
        <span className={`${color} font-medium`}>{label}</span>
      </div>
      <div className="flex gap-4 min-w-[80px] justify-center">
        <span className="text-gray-300 font-medium w-6 text-center">{whiteCount}</span>
        <span className="text-gray-300 font-medium w-6 text-center">{blackCount}</span>
      </div>
    </div>
  );

  return (
    <div className="bg-gray-900 rounded-xl p-6 shadow-lg border border-gray-600">
      {/* Header with player names */}
      <div className="flex items-center justify-center mb-6">
        <div className="flex items-center gap-8">
          <div className="text-center">
            <h3 className="text-lg font-bold text-white">{whiteName}</h3>
            <p className="text-sm text-gray-400">White</p>
          </div>
          <span className="text-2xl text-gray-500">vs</span>
          <div className="text-center">
            <h3 className="text-lg font-bold text-white">{blackName}</h3>
            <p className="text-sm text-gray-400">Black</p>
          </div>
        </div>
      </div>

      {/* Accuracy Section */}
      <div className="mb-6">
        <div className="flex items-center justify-center mb-4">
          <span className="text-yellow-400 text-lg flex items-center gap-2">
            <span>🎯</span>
            <span>Accuracy</span>
          </span>
        </div>
        
        <div className="flex items-end justify-center gap-12">
          <AccuracyDisplay accuracy={whiteReview.accuracy} player="white" />
          <AccuracyDisplay accuracy={blackReview.accuracy} player="black" />
        </div>
      </div>

      {/* ELO Section */}
      <div className="mb-6">
        <div className="flex items-center justify-center mb-4">
          <span className="text-yellow-400 text-lg flex items-center gap-2">
            <span>📊</span>
            <span>ELO</span>
          </span>
        </div>
        
        <div className="flex items-center justify-center gap-12">
          <EloDisplay elo={whiteElo} />
          <EloDisplay elo={blackElo} />
        </div>
      </div>

      {/* Move Quality Statistics */}
      <div className="grid grid-cols-2 gap-6">
        {/* Good Moves */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-white font-medium">Good</span>
            <div className="flex gap-1 ml-auto">
              <span className="bg-gray-600 text-white text-xs px-2 py-1 rounded">W</span>
              <span className="bg-gray-600 text-white text-xs px-2 py-1 rounded">B</span>
            </div>
          </div>
          
          <div className="space-y-1">
            <MoveQualityRow 
              category="brilliant"
              whiteCount={whiteReview.quality_stats.brilliant || 0}
              blackCount={blackReview.quality_stats.brilliant || 0}
              icon="⚡"
              color="text-cyan-400"
              label="Sigma"
            />
            <MoveQualityRow 
              category="excellent"
              whiteCount={whiteReview.quality_stats.excellent || 0}
              blackCount={blackReview.quality_stats.excellent || 0}
              icon="ℹ️"
              color="text-cyan-300"
              label="Awesome"
            />
            <MoveQualityRow 
              category="best"
              whiteCount={whiteReview.quality_stats.best || 0}
              blackCount={blackReview.quality_stats.best || 0}
              icon="✅"
              color="text-green-400"
              label="Best"
            />
            <MoveQualityRow 
              category="good"
              whiteCount={whiteReview.quality_stats.good || 0}
              blackCount={blackReview.quality_stats.good || 0}
              icon="✅"
              color="text-green-300"
              label="Nice"
            />
            <MoveQualityRow 
              category="ok"
              whiteCount={whiteReview.quality_stats.ok || 0}
              blackCount={blackReview.quality_stats.ok || 0}
              icon="✅"
              color="text-green-200"
              label="Ok"
            />
            <MoveQualityRow 
              category="book"
              whiteCount={whiteReview.quality_stats.book || 0}
              blackCount={blackReview.quality_stats.book || 0}
              icon="📖"
              color="text-gray-300"
              label="Book"
            />
          </div>
        </div>

        {/* Bad Moves */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
            <span className="text-white font-medium">Bad</span>
            <div className="flex gap-1 ml-auto">
              <span className="bg-gray-600 text-white text-xs px-2 py-1 rounded">W</span>
              <span className="bg-gray-600 text-white text-xs px-2 py-1 rounded">B</span>
            </div>
          </div>
          
          <div className="space-y-1">
            <MoveQualityRow 
              category="inaccuracy"
              whiteCount={whiteReview.quality_stats.inaccuracy || 0}
              blackCount={blackReview.quality_stats.inaccuracy || 0}
              icon="🔸"
              color="text-yellow-400"
              label="Strange"
            />
            <MoveQualityRow 
              category="mistake"
              whiteCount={whiteReview.quality_stats.mistake || 0}
              blackCount={blackReview.quality_stats.mistake || 0}
              icon="🔸"
              color="text-orange-400"
              label="Bad"
            />
            <MoveQualityRow 
              category="blunder"
              whiteCount={whiteReview.quality_stats.blunder || 0}
              blackCount={blackReview.quality_stats.blunder || 0}
              icon="❓"
              color="text-red-400"
              label="Clown"
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayerComparison;