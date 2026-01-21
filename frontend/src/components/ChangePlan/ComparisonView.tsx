import React, { useState } from 'react';
import { Eye, User, Clock, ChevronDown, ArrowRight, Sparkles } from 'lucide-react';

const ComparisonView: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [showExplorer, setShowExplorer] = useState(false);

  return (
    <div className="flex flex-col h-full bg-white p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold text-black">Change plan</h1>
          <button
            onClick={() => setShowExplorer(!showExplorer)}
            className="text-sm text-blue-600 hover:text-blue-700 font-semibold"
          >
            Show Explorer
          </button>
        </div>
      </div>

      {/* Comparison Interface */}
      <div className="flex items-center justify-center gap-8 mb-8">
        {/* Left Side - Select to Compare */}
        <div className="flex flex-col items-center gap-4">
          <button
            onClick={() => setSelectedScenario('scenario-1')}
            className="flex items-center gap-3 px-6 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold shadow-lg"
          >
            <Eye size={20} />
            <span>Compare: Select to compare</span>
            <ChevronDown size={18} />
          </button>
          {selectedScenario && (
            <div className="text-sm text-black font-semibold">
              Selected: {selectedScenario}
            </div>
          )}
        </div>

        {/* Arrow */}
        <div className="flex items-center">
          <ArrowRight size={32} className="text-blue-600" />
        </div>

        {/* Right Side - Current Scenario */}
        <div className="flex flex-col items-center gap-4">
          <button className="flex items-center gap-3 px-6 py-4 bg-gray-100 text-black rounded-lg hover:bg-gray-200 font-semibold border border-gray-300">
            <User size={20} className="text-black" />
            <span>with this scenario:</span>
            <Clock size={18} className="text-black" />
            <span className="font-semibold">Loading... / current version</span>
            <ChevronDown size={18} className="text-black" />
          </button>
        </div>
      </div>

      {/* Informational Section */}
      <div className="max-w-3xl mx-auto bg-blue-50 border border-blue-200 rounded-xl p-8">
        <h2 className="text-2xl font-bold text-black mb-4">
          See what's changed in your organization
        </h2>
        <p className="text-base text-black mb-4 leading-relaxed font-semibold">
          Select a previous version or another scenario from the dropdown above to compare with this one. 
          You'll see exactly which positions, dotted-line roles, and roles were added, removed, or updated — 
          and can even export a change document for each position to help drive the transition.
        </p>
        <a
          href="#"
          className="text-blue-600 hover:text-blue-700 font-semibold underline"
        >
          Learn more about the change plan
        </a>
      </div>

      {/* AI Assistant Prompt */}
      <div className="mt-8 max-w-3xl mx-auto">
        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Sparkles size={18} className="text-purple-600" />
            <span className="text-sm font-bold text-black">AI Assistant</span>
          </div>
          <button className="w-full text-left px-4 py-3 bg-white border-2 border-purple-200 rounded-lg hover:border-purple-300 focus:outline-none focus:border-purple-500 text-sm text-black font-semibold">
            Ask about changes, transitions, impact...
          </button>
        </div>
      </div>
    </div>
  );
};

export default ComparisonView;
