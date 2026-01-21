import React from 'react';
import { Download, FileImage, FileText, FileSpreadsheet, BarChart3 } from 'lucide-react';

interface ExportMenuProps {
  onClose: () => void;
}

const ExportMenu: React.FC<ExportMenuProps> = ({ onClose }) => {
  const exportOptions = [
    { label: 'Download Image', icon: FileImage, action: () => console.log('Export as image') },
    { label: 'Download PDF', icon: FileText, action: () => console.log('Export as PDF') },
    { label: 'Download CSV', icon: FileSpreadsheet, action: () => console.log('Export as CSV') },
    { label: 'Export charts', icon: BarChart3, action: () => console.log('Export charts') }
  ];

  return (
    <div className="absolute left-full top-0 ml-2 w-48 bg-white rounded-lg shadow-xl border border-gray-200 py-1 z-50">
      {exportOptions.map((option, index) => {
        const Icon = option.icon;
        return (
          <button
            key={index}
            onClick={() => {
              option.action();
              onClose();
            }}
            className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
          >
            <Icon size={16} className="text-gray-500" />
            {option.label}
          </button>
        );
      })}
    </div>
  );
};

export default ExportMenu;
