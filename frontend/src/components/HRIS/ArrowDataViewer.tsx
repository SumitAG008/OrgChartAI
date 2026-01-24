/**
 * Apache Arrow Data Viewer Component
 *
 * Displays Arrow data with:
 * - Performance statistics
 * - Data table view
 * - Format comparison (JSON vs Arrow)
 */

import React, { useState, useEffect } from 'react';

interface ArrowStats {
  num_rows: number;
  num_columns: number;
  column_names: string[];
  memory_bytes: number;
  memory_mb: number;
  schema: string;
}

interface ArrowStore {
  num_tables: number;
  total_memory_mb: number;
  tables: Record<string, ArrowStats>;
}

interface BenchmarkResult {
  test_records: number;
  results: {
    json: {
      serialize_ms: number;
      deserialize_ms: number;
      total_ms: number;
      size_bytes: number;
    };
    arrow: {
      serialize_ms: number;
      deserialize_ms: number;
      total_ms: number;
      size_bytes: number;
    };
  };
  speedup: {
    arrow_faster_by: string;
    time_saved_ms: number;
    size_reduction_percent: number;
  };
}

const HRIS_API = 'http://localhost:8002/api/v1/hris';

export const ArrowDataViewer: React.FC = () => {
  const [stores, setStores] = useState<ArrowStore | null>(null);
  const [selectedStore, setSelectedStore] = useState<string | null>(null);
  const [storeData, setStoreData] = useState<any[]>([]);
  const [benchmark, setBenchmark] = useState<BenchmarkResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch Arrow stores
  const fetchStores = async () => {
    try {
      const response = await fetch(`${HRIS_API}/arrow/stores`);
      const data = await response.json();
      setStores(data);
    } catch (err) {
      setError('Failed to fetch Arrow stores');
    }
  };

  // Fetch data from a specific store
  const fetchStoreData = async (storeKey: string) => {
    setLoading(true);
    try {
      const response = await fetch(`${HRIS_API}/arrow/data/${storeKey}?format=json`);
      const data = await response.json();
      setStoreData(data.data || []);
      setSelectedStore(storeKey);
    } catch (err) {
      setError('Failed to fetch store data');
    } finally {
      setLoading(false);
    }
  };

  // Run benchmark
  const runBenchmark = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${HRIS_API}/arrow/benchmark`);
      const data = await response.json();
      setBenchmark(data);
    } catch (err) {
      setError('Failed to run benchmark');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStores();
  }, []);

  return (
    <div className="p-6 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <svg className="w-6 h-6 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Apache Arrow Data Viewer
      </h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
          {error}
          <button onClick={() => setError(null)} className="ml-2 text-sm underline">Dismiss</button>
        </div>
      )}

      {/* Benchmark Section */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Performance Benchmark</h3>
          <button
            onClick={runBenchmark}
            disabled={loading}
            className="px-4 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 disabled:opacity-50"
          >
            {loading ? 'Running...' : 'Run Benchmark'}
          </button>
        </div>

        {benchmark && (
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="p-3 bg-white rounded border">
              <div className="text-sm text-gray-500">Speed Improvement</div>
              <div className="text-2xl font-bold text-green-600">{benchmark.speedup.arrow_faster_by}</div>
              <div className="text-xs text-gray-400">faster than JSON</div>
            </div>
            <div className="p-3 bg-white rounded border">
              <div className="text-sm text-gray-500">Time Saved</div>
              <div className="text-2xl font-bold text-blue-600">{benchmark.speedup.time_saved_ms}ms</div>
              <div className="text-xs text-gray-400">per 10,000 records</div>
            </div>
            <div className="p-3 bg-white rounded border">
              <div className="text-sm text-gray-500">Size Reduction</div>
              <div className="text-2xl font-bold text-purple-600">{benchmark.speedup.size_reduction_percent}%</div>
              <div className="text-xs text-gray-400">smaller than JSON</div>
            </div>
          </div>
        )}

        {benchmark && (
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div className="p-3 bg-yellow-50 rounded">
              <div className="font-medium text-yellow-800">JSON Performance</div>
              <div className="text-sm mt-1">
                <div>Serialize: {benchmark.results.json.serialize_ms}ms</div>
                <div>Deserialize: {benchmark.results.json.deserialize_ms}ms</div>
                <div>Size: {(benchmark.results.json.size_bytes / 1024).toFixed(1)} KB</div>
              </div>
            </div>
            <div className="p-3 bg-green-50 rounded">
              <div className="font-medium text-green-800">Arrow Performance</div>
              <div className="text-sm mt-1">
                <div>Serialize: {benchmark.results.arrow.serialize_ms}ms</div>
                <div>Deserialize: {benchmark.results.arrow.deserialize_ms}ms</div>
                <div>Size: {(benchmark.results.arrow.size_bytes / 1024).toFixed(1)} KB</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Stored Data Section */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Arrow Data Stores</h3>
          <button
            onClick={fetchStores}
            className="px-3 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
          >
            Refresh
          </button>
        </div>

        {stores && stores.num_tables > 0 ? (
          <div className="space-y-2">
            <div className="text-sm text-gray-500 mb-2">
              {stores.num_tables} tables, {stores.total_memory_mb} MB total
            </div>
            {Object.entries(stores.tables).map(([key, stats]) => (
              <div
                key={key}
                onClick={() => fetchStoreData(key)}
                className={`p-3 border rounded cursor-pointer transition-colors ${
                  selectedStore === key ? 'border-orange-500 bg-orange-50' : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex justify-between items-center">
                  <div className="font-medium">{key}</div>
                  <div className="text-sm text-gray-500">
                    {stats.num_rows} rows | {stats.memory_mb} MB
                  </div>
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Columns: {stats.column_names.slice(0, 5).join(', ')}
                  {stats.column_names.length > 5 && ` +${stats.column_names.length - 5} more`}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-gray-500 text-center py-8">
            No Arrow data stores yet. Sync some data first.
          </div>
        )}
      </div>

      {/* Data Table */}
      {selectedStore && storeData.length > 0 && (
        <div className="mt-6">
          <h3 className="font-semibold mb-3">
            Data Preview: {selectedStore} ({storeData.length} records)
          </h3>
          <div className="overflow-x-auto max-h-96 overflow-y-auto border rounded">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50 sticky top-0">
                <tr>
                  {Object.keys(storeData[0] || {}).slice(0, 8).map((col) => (
                    <th
                      key={col}
                      className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase"
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {storeData.slice(0, 100).map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    {Object.values(row).slice(0, 8).map((val: any, i) => (
                      <td key={i} className="px-3 py-2 text-sm text-gray-900 whitespace-nowrap">
                        {val === null ? <span className="text-gray-400">null</span> : String(val).slice(0, 50)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {storeData.length > 100 && (
            <div className="text-sm text-gray-500 mt-2 text-center">
              Showing first 100 of {storeData.length} records
            </div>
          )}
        </div>
      )}

      {/* How to Use */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-semibold text-blue-800 mb-2">How to Use Apache Arrow</h3>
        <div className="text-sm text-blue-700 space-y-2">
          <p><strong>1. Sync data to Arrow store:</strong></p>
          <code className="block bg-blue-100 p-2 rounded text-xs">
            POST /api/v1/hris/arrow/sync/Position?connection_id=...
          </code>
          <p><strong>2. Retrieve as JSON (for UI):</strong></p>
          <code className="block bg-blue-100 p-2 rounded text-xs">
            GET /api/v1/hris/arrow/data/conn-123:Position?format=json
          </code>
          <p><strong>3. Retrieve as Arrow IPC (for Arrow clients):</strong></p>
          <code className="block bg-blue-100 p-2 rounded text-xs">
            GET /api/v1/hris/arrow/data/conn-123:Position?format=arrow
          </code>
        </div>
      </div>
    </div>
  );
};

export default ArrowDataViewer;
