import React, { useState } from 'react';
import { BarChart3, Eye, Save, RotateCcw } from 'lucide-react';

const ForecastSheetView: React.FC = () => {
  const [dataType, setDataType] = useState('Compensation');
  const [groupBy, setGroupBy] = useState('Color');
  const [scale, setScale] = useState('Monthly');

  // Sample data for stacked bar chart
  const chartData = [
    { month: 'Jan', values: [3.9, 1.5, 0.2, 0.1, 0.1, 0.1, 0.1] },
    { month: 'Feb', values: [3.9, 1.5, 0.2, 0.1, 0.1, 0.1, 0.1] },
    { month: 'Mar', values: [3.9, 1.5, 0.2, 0.1, 0.1, 0.1, 0.1] },
    { month: 'Apr', values: [3.9, 1.5, 0.2, 0.1, 0.1, 0.1, 0.1] },
    { month: 'May', values: [3.9, 1.5, 0.2, 0.1, 0.1, 0.1, 0.1] }
  ];

  const colors = ['#60a5fa', '#dc2626', '#fbbf24', '#10b981', '#000000', '#6b7280', '#e5e7eb'];

  const maxValue = 8; // $8M

  return (
    <div className="h-full bg-white p-6">
      {/* Control Bar */}
      <div className="mb-6 flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2">
          <BarChart3 size={18} className="text-black" />
          <select
            value="Forecast sheet"
            className="text-sm font-bold text-black border border-gray-200 rounded px-3 py-1.5 bg-white"
          >
            <option>Forecast sheet</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-black font-semibold">Data:</span>
          <select
            value={dataType}
            onChange={(e) => setDataType(e.target.value)}
            className="text-sm border border-gray-200 rounded px-3 py-1.5 text-black font-semibold bg-white"
          >
            <option>Compensation</option>
            <option>Headcount</option>
            <option>Cost</option>
          </select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-black font-semibold">Group:</span>
          <select
            value={groupBy}
            onChange={(e) => setGroupBy(e.target.value)}
            className="text-sm border border-gray-200 rounded px-3 py-1.5 text-black font-semibold bg-white"
          >
            <option>Color</option>
            <option>Department</option>
            <option>Role</option>
          </select>
        </div>

        <button className="px-3 py-1.5 text-sm text-black hover:bg-gray-100 rounded-lg flex items-center gap-2 font-semibold">
          <span>Filter</span>
        </button>

        <div className="flex items-center gap-2">
          <span className="text-sm text-black font-semibold">Scale:</span>
          <select
            value={scale}
            onChange={(e) => setScale(e.target.value)}
            className="text-sm border border-gray-200 rounded px-3 py-1.5 text-black font-semibold bg-white"
          >
            <option>Monthly</option>
            <option>Quarterly</option>
            <option>Yearly</option>
          </select>
        </div>

        <button className="p-2 hover:bg-gray-100 rounded-lg">
          <Eye size={18} className="text-black" />
        </button>

        <div className="flex items-center gap-2 ml-auto">
          <button className="px-3 py-1.5 text-sm text-black hover:bg-gray-100 rounded-lg flex items-center gap-2 font-semibold">
            <Save size={16} className="text-black" />
            Save for everyone
            <span className="text-xs">▼</span>
          </button>
          <button className="px-3 py-1.5 text-sm text-black hover:bg-gray-100 rounded-lg flex items-center gap-2 font-semibold">
            <RotateCcw size={16} className="text-black" />
            Reset
          </button>
        </div>
      </div>

      {/* Stacked Bar Chart */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="relative" style={{ height: '400px' }}>
          {/* Y-Axis Labels */}
          <div className="absolute left-0 top-0 bottom-0 w-12 flex flex-col justify-between text-sm text-black font-bold">
            <span>$8M</span>
            <span>$6M</span>
            <span>$4M</span>
            <span>$2M</span>
            <span>$0</span>
          </div>

          {/* Chart Area */}
          <div className="ml-16 h-full flex items-end gap-4">
            {chartData.map((data, index) => {
              const total = data.values.reduce((a, b) => a + b, 0);
              const heightPercent = (total / maxValue) * 100;

              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  {/* Stacked Bar */}
                  <div
                    className="w-full rounded-t flex flex-col-reverse"
                    style={{ height: `${heightPercent}%`, minHeight: '20px' }}
                  >
                    {data.values.map((value, i) => {
                      const segmentHeight = (value / total) * 100;
                      return (
                        <div
                          key={i}
                          className="w-full"
                          style={{
                            height: `${segmentHeight}%`,
                            backgroundColor: colors[i % colors.length],
                            minHeight: segmentHeight > 0 ? '2px' : '0'
                          }}
                        />
                      );
                    })}
                  </div>
                  {/* Month Label */}
                  <div className="mt-2 text-xs text-black font-bold">{data.month}</div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ForecastSheetView;
