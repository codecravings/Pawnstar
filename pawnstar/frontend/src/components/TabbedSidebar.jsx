import React, { useState } from 'react';
import EvalGraph from './EvalGraph';
import MoveList from './MoveList';
import GamesHistory from './GamesHistory';

const TabbedSidebar = ({ 
  gameData, 
  evalValues, 
  currentMoveIndex, 
  onMoveSelect, 
  currentUsername, 
  currentSource, 
  onAnalyzeGame 
}) => {
  const [activeTab, setActiveTab] = useState('evaluation');

  const tabs = [
    { id: 'evaluation', label: 'Evaluation', icon: '📊' },
    { id: 'moves', label: 'Moves', icon: '♞' },
    { id: 'games', label: 'Recent Games', icon: '🎮' }
  ];

  const TabButton = ({ tab, isActive, onClick }) => (
    <button
      onClick={onClick}
      className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 ${
        isActive
          ? 'bg-accent text-black shadow-lg'
          : 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white'
      }`}
    >
      <span>{tab.icon}</span>
      <span className="hidden sm:inline">{tab.label}</span>
    </button>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'evaluation':
        return (
          <div className="space-y-4">
            <EvalGraph values={evalValues} />
          </div>
        );
      
      case 'moves':
        return (
          <div className="space-y-4">
            <MoveList 
              moves={gameData?.moves || []}
              currentIndex={currentMoveIndex}
              onMoveSelect={onMoveSelect}
              topBlunders={gameData?.review?.top_blunders || []}
            />
          </div>
        );
      
      case 'games':
        return (
          <div className="space-y-4">
            <GamesHistory 
              username={currentUsername}
              source={currentSource}
              onAnalyzeGame={onAnalyzeGame}
            />
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="bg-gradient-to-br from-surface to-gray-800 rounded-xl shadow-lg border border-gray-600 overflow-hidden">
      {/* Tab Navigation */}
      <div className="bg-gray-800 p-4 border-b border-gray-600">
        <div className="flex gap-2 justify-center sm:justify-start">
          {tabs.map((tab) => (
            <TabButton
              key={tab.id}
              tab={tab}
              isActive={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
            />
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-5">
        {renderTabContent()}
      </div>

      {/* Legacy Analysis Summary - keep for backward compatibility */}
      {gameData?.review && !gameData?.player_reviews && activeTab === 'evaluation' && (
        <div className="p-5 border-t border-gray-600">
          <h4 className="text-lg font-bold mb-3 text-accent flex items-center">
            🔍 Analysis Summary
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between items-center p-3 bg-background rounded-lg">
              <span className="text-gray-300">Accuracy:</span>
              <span className="font-bold text-2xl text-accent">{gameData.review.accuracy_estimate}%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-background rounded-lg">
              <span className="text-gray-300">Major Blunders:</span>
              <span className="font-bold text-xl text-danger">{gameData.review.top_blunders.length}</span>
            </div>
            <div className="p-4 bg-gradient-to-r from-blue-900/20 to-purple-900/20 rounded-lg border border-blue-500/30">
              <p className="text-gray-100 leading-relaxed text-sm">{gameData.review.summary_text}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TabbedSidebar;