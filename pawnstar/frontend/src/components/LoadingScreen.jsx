import React from 'react';

const LoadingScreen = ({ message = "Analyzing your game..." }) => {
  return (
    <div className="fixed inset-0 bg-bg/95 backdrop-blur-md z-50 flex items-center justify-center">
      <div className="text-center space-y-8">
        {/* Animated Chess Pieces */}
        <div className="relative">
          <div className="flex items-center justify-center space-x-4 mb-8">
            <div className="animate-bounce" style={{ animationDelay: '0ms' }}>
              <div className="w-16 h-16 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center text-3xl shadow-lg">
                ♚
              </div>
            </div>
            <div className="animate-bounce" style={{ animationDelay: '100ms' }}>
              <div className="w-16 h-16 bg-gradient-to-br from-blue-400 to-purple-500 rounded-lg flex items-center justify-center text-3xl shadow-lg">
                ♛
              </div>
            </div>
            <div className="animate-bounce" style={{ animationDelay: '200ms' }}>
              <div className="w-16 h-16 bg-gradient-to-br from-green-400 to-teal-500 rounded-lg flex items-center justify-center text-3xl shadow-lg">
                ♜
              </div>
            </div>
            <div className="animate-bounce" style={{ animationDelay: '300ms' }}>
              <div className="w-16 h-16 bg-gradient-to-br from-pink-400 to-red-500 rounded-lg flex items-center justify-center text-3xl shadow-lg">
                ♝
              </div>
            </div>
            <div className="animate-bounce" style={{ animationDelay: '400ms' }}>
              <div className="w-16 h-16 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center text-3xl shadow-lg">
                ♞
              </div>
            </div>
            <div className="animate-bounce" style={{ animationDelay: '500ms' }}>
              <div className="w-16 h-16 bg-gradient-to-br from-indigo-400 to-blue-500 rounded-lg flex items-center justify-center text-3xl shadow-lg">
                ♟
              </div>
            </div>
          </div>
        </div>

        {/* Loading Spinner */}
        <div className="relative">
          <div className="w-24 h-24 mx-auto">
            <div className="absolute inset-0 rounded-full border-4 border-accent/20"></div>
            <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-accent animate-spin"></div>
            <div className="absolute inset-2 rounded-full border-4 border-transparent border-t-accent-light animate-spin" style={{ animationDirection: 'reverse', animationDuration: '1.5s' }}></div>
          </div>
        </div>

        {/* Loading Text */}
        <div className="space-y-4">
          <h2 className="text-3xl font-bold text-accent">
            🧠 Deep Analysis in Progress
          </h2>
          <p className="text-xl text-gray-300 max-w-md mx-auto">
            {message}
          </p>
          
          {/* Progress Dots */}
          <div className="flex items-center justify-center space-x-2">
            <div className="w-3 h-3 bg-accent rounded-full animate-pulse"></div>
            <div className="w-3 h-3 bg-accent rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-3 h-3 bg-accent rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
          </div>
        </div>

        {/* Fun Facts */}
        <div className="max-w-lg mx-auto p-6 bg-gradient-to-r from-surface/50 to-gray-800/50 rounded-xl border border-gray-600">
          <p className="text-sm text-gray-400 italic">
            💡 Did you know? Stockfish can calculate over 70 million positions per second!
          </p>
        </div>

        {/* Chess Board Background Pattern */}
        <div className="absolute inset-0 opacity-5 pointer-events-none">
          <div className="grid grid-cols-8 h-full">
            {Array.from({ length: 64 }).map((_, i) => (
              <div
                key={i}
                className={`${
                  (Math.floor(i / 8) + i) % 2 === 0 ? 'bg-white' : 'bg-gray-800'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoadingScreen;