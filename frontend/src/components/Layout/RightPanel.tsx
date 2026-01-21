import React, { useState } from 'react';
import { X, Download, Plus, ChevronDown, Star, Send, Info } from 'lucide-react';

interface RightPanelProps {
  position: any;
  onClose: () => void;
}

const RightPanel: React.FC<RightPanelProps> = ({ position, onClose }) => {
  const [expandedSections, setExpandedSections] = useState({
    responsibilities: true,
    accountabilities: false
  });
  const [aiChatMessage, setAiChatMessage] = useState('');

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section as keyof typeof prev]
    }));
  };

  return (
    <div className="w-80 bg-white border-l border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-gray-600">Position</h3>
          <h2 className="text-lg font-bold text-black mt-1">{position?.title || 'AI Market Analyst'}</h2>
        </div>
        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-100 rounded">
            <Download size={18} className="text-black" />
          </button>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded">
            <X size={18} className="text-black" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {/* Position Info */}
        <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">A</span>
          </div>
          <div className="flex-1">
            <div className="text-sm font-bold text-black">{position?.title || 'AI Market Analyst'}</div>
            <div className="text-xs text-black font-semibold">100%</div>
          </div>
        </div>

        {/* Responsibilities */}
        <div>
          <button
            onClick={() => toggleSection('responsibilities')}
            className="w-full flex items-center justify-between p-2 hover:bg-gray-50 rounded-lg"
          >
            <span className="text-sm font-bold text-black">
              4 Responsibilities
            </span>
            {expandedSections.responsibilities ? (
              <ChevronDown size={16} className="text-black" />
            ) : (
              <ChevronRight size={16} className="text-black" />
            )}
          </button>
          {expandedSections.responsibilities && (
            <div className="mt-2 space-y-2 pl-4">
              <div className="text-sm text-black font-semibold">
                • Continuous Market Monitoring: Analyze...
              </div>
              <div className="text-sm text-black font-semibold">
                • Sentiment Analysis and Brand...
              </div>
              <div className="text-sm text-black font-semibold">
                • Competitive Intelligence Synthesis:...
              </div>
              <div className="text-sm text-black font-semibold">
                • Predictive Campaign Performance:...
              </div>
            </div>
          )}
        </div>

        {/* Accountabilities */}
        <div>
          <div className="flex items-center justify-between p-2">
            <span className="text-sm font-bold text-black">Accountabilities</span>
            <div className="flex items-center gap-2">
              <span className="text-xs bg-gray-100 text-black px-2 py-0.5 rounded-full font-bold">0</span>
              <button className="p-1 hover:bg-gray-100 rounded">
                <Plus size={16} className="text-black" />
              </button>
            </div>
          </div>
        </div>

        {/* Move down in chart */}
        <div>
          <label className="text-xs font-bold text-black mb-1 block">Move down in chart</label>
          <select className="w-full border border-gray-200 rounded px-3 py-2 text-sm text-black font-semibold bg-white">
            <option>None</option>
            <option>1 level</option>
            <option>2 levels</option>
          </select>
        </div>

        {/* Calculations */}
        <div>
          <h4 className="text-sm font-bold text-black mb-3">Calculations</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="relative w-20 h-20 mx-auto">
                <svg className="transform -rotate-90" viewBox="0 0 36 36">
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="3"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="3"
                    strokeDasharray="75 100"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xs font-bold text-black">3</span>
                </div>
              </div>
              <div className="mt-2 flex items-center justify-center gap-1">
                <span className="text-xs text-black font-semibold">Layers</span>
                <Info size={12} className="text-black" />
              </div>
            </div>
            <div className="text-center">
              <div className="relative w-20 h-20 mx-auto">
                <svg className="transform -rotate-90" viewBox="0 0 36 36">
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#e5e7eb"
                    strokeWidth="3"
                  />
                  <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#3b82f6"
                    strokeWidth="3"
                    strokeDasharray="60 100"
                    strokeLinecap="round"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-xs font-bold text-black">5</span>
                </div>
              </div>
              <div className="mt-2 flex items-center justify-center gap-1">
                <span className="text-xs text-black font-semibold">Span</span>
                <Info size={12} className="text-black" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* AI Chat Bubble - Fixed at Bottom */}
      <div className="p-4 border-t border-gray-200 bg-white">
        <div className="relative">
          <input
            type="text"
            value={aiChatMessage}
            onChange={(e) => setAiChatMessage(e.target.value)}
            placeholder="Ask me anything..."
            className="w-full pl-10 pr-20 py-2.5 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 text-sm text-black font-semibold placeholder-gray-500"
          />
          <Star size={18} className="absolute left-3 top-3 text-purple-500" />
          <button className="absolute right-2 top-2 p-1.5 bg-purple-600 text-white rounded hover:bg-purple-700">
            <Send size={16} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default RightPanel;
