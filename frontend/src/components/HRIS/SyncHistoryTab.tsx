import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { History, CheckCircle, XCircle, Clock, RefreshCw } from 'lucide-react';

interface SyncHistoryItem {
  id: string;
  connection_id: string;
  sync_type: string;
  status: 'success' | 'failed' | 'partial';
  records_synced: {
    org_units?: number;
    positions?: number;
    employees?: number;
    created?: number;
    updated?: number;
    deleted?: number;
  };
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  error_message?: string;
}

interface SyncHistoryTabProps {
  connectionId: string;
}

const SyncHistoryTab: React.FC<SyncHistoryTabProps> = ({ connectionId }) => {
  const { data: history, isLoading } = useQuery<SyncHistoryItem[]>({
    queryKey: ['sync-history', connectionId],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/sync-history`
      );
      if (!response.ok) return [];
      return response.json();
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <RefreshCw className="animate-spin text-gray-400" size={24} />
        <span className="ml-2 text-gray-600">Loading sync history...</span>
      </div>
    );
  }

  if (!history || history.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        <History size={48} className="mx-auto mb-4 text-gray-400" />
        <p className="text-sm">No sync history available</p>
        <p className="text-xs text-gray-400 mt-2">
          Sync history will appear here after you perform your first sync
        </p>
      </div>
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="text-green-600" size={20} />;
      case 'failed':
        return <XCircle className="text-red-600" size={20} />;
      case 'partial':
        return <Clock className="text-yellow-600" size={20} />;
      default:
        return <Clock className="text-gray-400" size={20} />;
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return 'N/A';
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-900">Sync History</h4>
        <span className="text-xs text-gray-500">
          {history.length} sync{history.length !== 1 ? 'es' : ''}
        </span>
      </div>

      <div className="space-y-3">
        {history.map((item) => (
          <div
            key={item.id}
            className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start gap-3 flex-1">
                {getStatusIcon(item.status)}
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`text-sm font-medium capitalize ${
                      item.status === 'success' ? 'text-green-700' :
                      item.status === 'failed' ? 'text-red-700' :
                      'text-yellow-700'
                    }`}>
                      {item.status}
                    </span>
                    <span className="text-xs text-gray-500 capitalize">
                      {item.sync_type} sync
                    </span>
                    {item.duration_seconds && (
                      <span className="text-xs text-gray-400">
                        • {formatDuration(item.duration_seconds)}
                      </span>
                    )}
                  </div>

                  {item.records_synced && (
                    <div className="flex items-center gap-4 text-xs text-gray-600 mb-2">
                      {item.records_synced.org_units !== undefined && (
                        <span>Org Units: {item.records_synced.org_units}</span>
                      )}
                      {item.records_synced.positions !== undefined && (
                        <span>Positions: {item.records_synced.positions}</span>
                      )}
                      {item.records_synced.employees !== undefined && (
                        <span>Employees: {item.records_synced.employees}</span>
                      )}
                      {item.records_synced.created !== undefined && (
                        <span className="text-green-600">+{item.records_synced.created} created</span>
                      )}
                      {item.records_synced.updated !== undefined && (
                        <span className="text-blue-600">~{item.records_synced.updated} updated</span>
                      )}
                      {item.records_synced.deleted !== undefined && (
                        <span className="text-red-600">-{item.records_synced.deleted} deleted</span>
                      )}
                    </div>
                  )}

                  <div className="text-xs text-gray-500">
                    {new Date(item.started_at).toLocaleString()}
                    {item.completed_at && (
                      <span> → {new Date(item.completed_at).toLocaleString()}</span>
                    )}
                  </div>

                  {item.error_message && (
                    <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
                      <strong>Error:</strong> {item.error_message}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SyncHistoryTab;
