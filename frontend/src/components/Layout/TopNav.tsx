import React, { useState } from 'react';
import { 
  Share2, Download, Lightbulb, Copy, 
  User, ChevronDown, Tag, FileText,
  MoreVertical, FileImage, FileSpreadsheet, BarChart3
} from 'lucide-react';

const TopNav: React.FC = () => {
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showOrgMenu, setShowOrgMenu] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [showMainMenu, setShowMainMenu] = useState(false);

  return (
    <div className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      {/* Left Section */}
      <div className="flex items-center gap-4">
        {/* Logo and Title */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">M</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="text-lg font-semibold text-gray-900">
              meldra AI
            </span>
            <button
              onClick={() => setShowOrgMenu(!showOrgMenu)}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <ChevronDown size={16} className="text-gray-600" />
            </button>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg flex items-center gap-1.5">
            <Tag size={16} />
            Add tag
          </button>
          <button className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg flex items-center gap-1.5">
            <FileText size={16} />
            Template
          </button>
        </div>
      </div>

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* Main Menu Button */}
        <div className="relative">
          <button
            onClick={() => setShowMainMenu(!showMainMenu)}
            className="p-2 hover:bg-gray-100 rounded-lg"
            title="More options"
          >
            <MoreVertical size={18} className="text-gray-600" />
          </button>
          {showMainMenu && (
            <div className="absolute left-0 top-full mt-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-1 z-50">
                    <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                      Copy
                    </button>
                    <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                      Share
                    </button>
                    <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                      Create link
                    </button>
                    <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                      Import / update
                    </button>
                    <div className="relative">
                      <button
                        onClick={() => setShowExportMenu(!showExportMenu)}
                        className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 flex items-center justify-between font-medium"
                      >
                        Export
                        <span className="text-xs">▶</span>
                      </button>
                      {showExportMenu && (
                        <div className="absolute left-full top-0 ml-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-1 z-50">
                          <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 flex items-center gap-2 font-medium">
                            <FileImage size={16} className="text-black" />
                            Download Image
                          </button>
                          <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 flex items-center gap-2 font-medium">
                            <FileText size={16} className="text-black" />
                            Download PDF
                          </button>
                          <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 flex items-center gap-2 font-medium">
                            <FileSpreadsheet size={16} className="text-black" />
                            Download CSV
                          </button>
                          <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 flex items-center gap-2 font-medium">
                            <BarChart3 size={16} className="text-black" />
                            Export charts
                          </button>
                        </div>
                      )}
                    </div>
                    <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                      Tutorial
                    </button>
                    <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                      Settings
                    </button>
                    <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                      History
                    </button>
                    <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                      Archive
                    </button>
            </div>
          )}
        </div>

        {/* Icons */}
        <button className="p-2 hover:bg-gray-100 rounded-lg" title="Share">
          <Share2 size={18} className="text-gray-600" />
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-lg" title="Download">
          <Download size={18} className="text-gray-600" />
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-lg" title="Insights">
          <Lightbulb size={18} className="text-gray-600" />
        </button>
        <button className="p-2 hover:bg-gray-100 rounded-lg" title="Share Link">
          <Share2 size={18} className="text-gray-600" />
        </button>
        <button className="px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg flex items-center gap-1.5">
          <Copy size={16} />
          Copy
        </button>

        {/* meldra AI Button - Prominent Purple */}
        <button className="px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 text-white font-semibold rounded-lg hover:from-purple-700 hover:to-purple-800 flex items-center gap-2 shadow-md">
          <span className="text-lg">✨</span>
          <span>meldra AI</span>
        </button>

        {/* User Profile */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="w-8 h-8 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center hover:ring-2 hover:ring-blue-300"
          >
            <User size={18} className="text-white" />
          </button>
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                Profile
              </button>
              <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                Settings
              </button>
              <button className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 font-medium">
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TopNav;
