import React, { useState } from 'react';
import TopNav from './TopNav';
import LeftSidebar from './LeftSidebar';
import CenterCanvas from './CenterCanvas';
import RightPanel from './RightPanel';

interface MainLayoutProps {
  children?: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const [selectedView, setSelectedView] = useState<'org-chart' | 'people-positions' | 'functional-chart' | 'forecast-sheet' | 'change-plan'>('org-chart');
  const [selectedPosition, setSelectedPosition] = useState<any>(null);
  const [isRightPanelOpen, setIsRightPanelOpen] = useState(false);

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Top Navigation Bar */}
      <TopNav />

      {/* Main Content Area */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar */}
        <LeftSidebar 
          selectedView={selectedView}
          onViewChange={setSelectedView}
        />

        {/* Center Canvas */}
        <div className="flex-1 flex flex-col overflow-hidden">
          <CenterCanvas
            view={selectedView}
            onPositionSelect={(position) => {
              setSelectedPosition(position);
              setIsRightPanelOpen(true);
            }}
          />
        </div>

        {/* Right Panel */}
        {isRightPanelOpen && selectedPosition && (
          <RightPanel
            position={selectedPosition}
            onClose={() => {
              setIsRightPanelOpen(false);
              setSelectedPosition(null);
            }}
          />
        )}
      </div>
    </div>
  );
};

export default MainLayout;
