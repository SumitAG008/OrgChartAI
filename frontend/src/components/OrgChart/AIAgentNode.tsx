import React from 'react';
import { Sparkles } from 'lucide-react';

interface AIAgentNodeProps {
  name: string;
  title: string;
  allocation?: string;
  onClick?: () => void;
}

const AIAgentNode: React.FC<AIAgentNodeProps> = ({ name, title, allocation = '100%', onClick }) => {
  return (
    <div
      onClick={onClick}
      className="relative bg-white border-2 border-purple-500 rounded-lg shadow-lg p-4 min-w-[200px] cursor-pointer hover:shadow-xl transition-all group"
    >
      {/* Purple AI Badge */}
      <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg">
        <span className="text-white font-bold text-sm">A</span>
      </div>

      {/* AI Agent Label */}
      <div className="flex items-center gap-2 mb-2">
        <Sparkles size={14} className="text-purple-600" />
        <span className="text-xs font-semibold text-purple-700">AI Agent '{name}'</span>
      </div>

      {/* Title */}
      <div className="flex items-start gap-2">
        <div className="w-1.5 h-1.5 bg-purple-500 rounded-full mt-2 flex-shrink-0" />
        <div className="flex-1">
          <div className="text-sm font-semibold text-gray-900">{title}</div>
          <div className="text-xs text-gray-500 mt-1">{allocation}</div>
        </div>
      </div>

      {/* Hover Effect */}
      <div className="absolute inset-0 border-2 border-purple-300 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
    </div>
  );
};

export default AIAgentNode;
