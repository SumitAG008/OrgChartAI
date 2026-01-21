import React from 'react';
import { Maximize2 } from 'lucide-react';

interface ZoomControlsProps {
  scale: number;
  onScaleChange: (scale: number) => void;
  onReset: () => void;
}

const ZoomControls: React.FC<ZoomControlsProps> = ({ scale, onScaleChange, onReset }) => {
  return (
    <div className="absolute bottom-5 right-5 flex gap-2 bg-white border border-gray-200 rounded-lg p-2 shadow-lg">
      <button
        onClick={() => onScaleChange(Math.max(0.5, scale - 0.1))}
        className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors"
      >
        −
      </button>
      <button className="px-3 py-1.5 text-sm text-gray-700 font-medium min-w-[60px]">
        {Math.round(scale * 100)}%
      </button>
      <button
        onClick={() => onScaleChange(Math.min(2, scale + 0.1))}
        className="px-3 py-1.5 text-sm text-gray-600 hover:bg-gray-100 rounded transition-colors"
      >
        +
      </button>
      <div className="w-px bg-gray-200 mx-1" />
      <button
        onClick={onReset}
        className="p-1.5 text-gray-600 hover:bg-gray-100 rounded transition-colors"
        title="Reset zoom"
      >
        <Maximize2 size={16} />
      </button>
    </div>
  );
};

export default ZoomControls;
