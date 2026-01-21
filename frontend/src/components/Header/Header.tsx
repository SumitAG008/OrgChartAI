import React from 'react';
import { 
  Tag, FileText, Edit3, Download, Share2, 
  ChevronDown, Sparkles, User 
} from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50 flex items-center justify-between px-6">
      <div className="flex items-center gap-4">
        <div className="w-8 h-8 bg-gradient-to-r from-green-600 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-green-500/30">
          M
        </div>
        <div className="flex items-center gap-2 text-gray-600 cursor-pointer hover:text-gray-900">
          <span className="font-semibold">meldra AI</span>
          <ChevronDown size={16} />
        </div>
        <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <Tag size={16} />
          Add tag
        </button>
        <button className="flex items-center gap-2 px-4 py-2 text-sm text-gray-600 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
          <FileText size={16} />
          Template
        </button>
      </div>
      
      <div className="flex items-center gap-3">
        <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
          <Edit3 size={18} />
        </button>
        <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
          <Download size={18} />
        </button>
        <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
          <Share2 size={18} />
        </button>
        <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium">
          Copy
        </button>
        <button className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition-colors text-sm font-medium flex items-center gap-2 shadow-lg shadow-green-500/30">
          <Sparkles size={16} />
          meldra AI
        </button>
        <div className="w-9 h-9 bg-indigo-100 rounded-full flex items-center justify-center cursor-pointer hover:bg-indigo-200 transition-colors">
          <User size={18} className="text-indigo-600" />
        </div>
      </div>
    </header>
  );
};

export default Header;
