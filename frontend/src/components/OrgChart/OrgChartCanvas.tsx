import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Filter, Layers, Layout, Users, Settings, 
  Download, Share2, Sparkles, ZoomIn, ZoomOut, Maximize2
} from 'lucide-react';
import LayoutSelector from './LayoutSelector';
import OrgChartRenderer from './OrgChartRenderer';
import { OrgStructureType } from '../../types/orgStructures';
import { TreeNode } from '../../types';
import { fetchOrgChart } from '../../services/api';
import { DisplayProperties } from './PropertiesPanel';

interface OrgChartCanvasProps {
  displayProperties?: DisplayProperties;
}

const OrgChartCanvas: React.FC<OrgChartCanvasProps> = ({ displayProperties }) => {
  const [layoutType, setLayoutType] = useState<OrgStructureType>('classic-top-down');
  const [selectedNode, setSelectedNode] = useState<TreeNode | null>(null);
  const [hoveredNode, setHoveredNode] = useState<TreeNode | null>(null);
  const [showAIChat, setShowAIChat] = useState(false);
  const [filter, setFilter] = useState('Top item');
  const [layers, setLayers] = useState(2);

  // Fetch org chart data
  const { data: orgChartData, isLoading, error } = useQuery({
    queryKey: ['orgChart', layoutType],
    queryFn: () => fetchOrgChart(),
    refetchOnWindowFocus: false
  });

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100
      }
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-center"
        >
          <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Loading organizational chart...</p>
        </motion.div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center p-8 bg-red-50 rounded-lg border border-red-200">
          <p className="text-red-600 mb-2">Error loading chart</p>
          <p className="text-sm text-gray-600">Please check your connection and try again</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-50 via-green-50 to-emerald-50">
      {/* Control Bar */}
      <motion.div
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="bg-white/80 backdrop-blur-sm border-b border-gray-200 px-6 py-3 shadow-sm"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            {/* Layout Selector */}
            <LayoutSelector
              currentLayout={layoutType}
              onLayoutChange={setLayoutType}
            />

            {/* Properties Dropdown */}
            <div className="relative">
              <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                <Settings className="w-4 h-4" />
                <span>Properties</span>
              </button>
            </div>

            {/* Filter */}
            <div className="relative">
              <select
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent appearance-none pr-8"
              >
                <option>Top item</option>
                <option>All levels</option>
                <option>Active only</option>
                <option>With vacancies</option>
              </select>
              <Filter className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
            </div>

            {/* Layers Indicator */}
            <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg">
              <Layers className="w-4 h-4" />
              <span>Layers: {layers} below</span>
            </div>

            {/* Layout Type */}
            <div className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg">
              <Layout className="w-4 h-4" />
              <span>Layout: Narrow</span>
            </div>

            {/* Roles Toggle */}
            <button className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
              <Users className="w-4 h-4" />
              <span>Roles</span>
            </button>
          </div>

          <div className="flex items-center gap-2">
            <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
              <Download className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
              <Share2 className="w-5 h-5" />
            </button>
            <button className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
              <Maximize2 className="w-5 h-5" />
            </button>
          </div>
        </div>
      </motion.div>

      {/* Main Canvas Area */}
      <div className="flex-1 relative overflow-hidden">
        <AnimatePresence mode="wait">
          <motion.div
            key={layoutType}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.3 }}
            className="w-full h-full"
          >
            <OrgChartRenderer
              data={orgChartData?.tree || null}
              layoutType={layoutType}
              onNodeClick={setSelectedNode}
              onNodeHover={setHoveredNode}
              displayProperties={displayProperties}
            />
          </motion.div>
        </AnimatePresence>

        {/* AI Chat Assistant */}
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setShowAIChat(!showAIChat)}
          className="absolute bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-green-600 to-emerald-600 rounded-full shadow-2xl shadow-green-500/50 flex items-center justify-center text-white hover:shadow-green-500/70 transition-all duration-300 z-50"
        >
          <Sparkles className="w-6 h-6" />
        </motion.button>

        {/* AI Chat Panel */}
        <AnimatePresence>
          {showAIChat && (
            <motion.div
              initial={{ x: 400, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: 400, opacity: 0 }}
              className="absolute bottom-24 right-6 w-96 h-96 bg-white rounded-2xl shadow-2xl border border-gray-200 z-50 flex flex-col overflow-hidden"
            >
              <div className="bg-gradient-to-r from-green-600 to-emerald-600 p-4 text-white shadow-lg">
                <h3 className="font-semibold flex items-center gap-2">
                  <Sparkles className="w-5 h-5" />
                  meldra AI
                </h3>
              </div>
              <div className="flex-1 p-4 overflow-y-auto">
                <div className="space-y-4">
                  <div className="bg-gray-100 rounded-lg p-3">
                    <p className="text-sm text-gray-700">
                      Ask me anything about your organization structure...
                    </p>
                  </div>
                </div>
              </div>
              <div className="border-t border-gray-200 p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Ask me anything..."
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  />
                  <button className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg transition-shadow shadow-md shadow-green-500/30">
                    Send
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Node Info Panel */}
        {selectedNode && (
          <motion.div
            initial={{ x: -400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -400, opacity: 0 }}
            className="absolute top-6 left-6 w-80 bg-white rounded-xl shadow-2xl border border-gray-200 p-6 z-50"
          >
            <h3 className="font-semibold text-lg mb-2">{selectedNode.person.name}</h3>
            <p className="text-gray-600 mb-4">{selectedNode.person.title}</p>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Status:</span>
                <span className="text-green-600 font-medium">Active</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Direct Reports:</span>
                <span className="font-medium">{selectedNode.children?.length || 0}</span>
              </div>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="mt-4 w-full px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors text-sm"
            >
              Close
            </button>
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default OrgChartCanvas;
