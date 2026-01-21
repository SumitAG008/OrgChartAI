import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw, Trash2, Settings, FileText, History, Map, Zap } from 'lucide-react';
import FieldMappingEditor from './FieldMappingEditor';
import SyncHistoryTab from './SyncHistoryTab';
import SettingsTab from './SettingsTab';
import SyncDetailsView from './SyncDetailsView';
import { useMutation } from '@tanstack/react-query';

interface HRISConnection {
  id: string;
  name: string;
  system: string;
  status: 'active' | 'inactive' | 'error' | 'testing';
  last_sync_at?: string;
  last_sync_status?: string;
  description?: string;
  credentials?: {
    company_id?: string;
    username?: string;
    password?: string;
    api_url?: string;
    auth_method?: 'basic' | 'oauth';
  };
}

interface ConnectionCardProps {
  connection: HRISConnection;
  onSync: (id: string) => void;
  onDelete: (id: string) => void;
}

const ConnectionCard: React.FC<ConnectionCardProps> = ({
  connection,
  onSync,
  onDelete
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeTab, setActiveTab] = useState<'overview' | 'mapping' | 'history' | 'settings'>('overview');
  const [autoSyncStatus, setAutoSyncStatus] = useState<any>(null);
  const [showAutoSyncModal, setShowAutoSyncModal] = useState(false);
  const [autoSyncCredentials, setAutoSyncCredentials] = useState({
    company_id: connection.credentials?.company_id || '',
    username: connection.credentials?.username || '',
    password: '',
    api_url: connection.credentials?.api_url || 'https://api.successfactors.eu'
  });

  // Auto Sync Mutation
  const autoSyncMutation = useMutation({
    mutationFn: async (creds: typeof autoSyncCredentials) => {
      const response = await fetch(`http://localhost:8002/api/v1/hris/auto-sync/start?connection_id=${connection.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: creds.company_id,
          username: creds.username,
          password: creds.password,
          api_url: creds.api_url
        })
      });
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Auto sync failed' }));
        throw new Error(error.detail || 'Auto sync failed');
      }
      return response.json();
    },
    onSuccess: (data) => {
      setAutoSyncStatus(data);
      setShowAutoSyncModal(false);
      // Poll for status updates
      pollAutoSyncStatus(data.sync_id);
    }
  });

  const pollAutoSyncStatus = async (syncId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8002/api/v1/hris/auto-sync/${syncId}`);
        if (response.ok) {
          const status = await response.json();
          setAutoSyncStatus(status);
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(interval);
            // Refresh connection data
            onSync(connection.id);
          }
        }
      } catch (error) {
        console.error('Error polling sync status:', error);
        clearInterval(interval);
      }
    }, 2000); // Poll every 2 seconds

    // Stop polling after 5 minutes
    setTimeout(() => clearInterval(interval), 300000);
  };

  const tabs = [
    { id: 'overview', label: 'Overview', icon: FileText },
    { id: 'mapping', label: 'Mapping', icon: Map },
    { id: 'history', label: 'Sync History', icon: History },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow">
      {/* Card Header */}
      <div 
        className="p-4 cursor-pointer"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">
              {connection.system === 'successfactors' ? '🔵' : '📊'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{connection.name}</h3>
              <p className="text-sm text-gray-600 capitalize">{connection.system}</p>
              {connection.last_sync_at && (
                <p className="text-xs text-gray-500 mt-1">
                  Last sync: {new Date(connection.last_sync_at).toLocaleString()}
                </p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${
              connection.status === 'active' ? 'bg-green-100 text-green-700' :
              connection.status === 'error' ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-gray-700'
            }`}>
              {connection.status}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setShowAutoSyncModal(true);
              }}
              className="px-3 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all flex items-center gap-2 text-sm font-semibold shadow-md"
              title="One-Click Auto Sync"
            >
              <Zap size={16} />
              Auto Sync
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onSync(connection.id);
              }}
              className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
              title="Sync Now"
            >
              <RefreshCw size={18} />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(connection.id);
              }}
              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              title="Delete"
            >
              <Trash2 size={18} />
            </button>
          </div>
        </div>
      </div>

      {/* Expanded Content with Tabs */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="border-t border-gray-200"
          >
            {/* Tabs */}
            <div className="flex border-b border-gray-200 bg-gray-50">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                      activeTab === tab.id
                        ? 'text-green-600 border-b-2 border-green-600 bg-white'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon size={16} />
                    {tab.label}
                  </button>
                );
              })}
            </div>

            {/* Tab Content */}
            <div className="p-6 bg-white">
              {activeTab === 'overview' && (
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Connection Details</h4>
                    <dl className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <dt className="text-gray-500">Status</dt>
                        <dd className="font-medium text-gray-900 capitalize">{connection.status}</dd>
                      </div>
                      <div>
                        <dt className="text-gray-500">System</dt>
                        <dd className="font-medium text-gray-900 capitalize">{connection.system}</dd>
                      </div>
                      {connection.credentials?.api_url && (
                        <div className="col-span-2">
                          <dt className="text-gray-500">API URL</dt>
                          <dd className="font-medium text-gray-900 font-mono text-xs break-all">
                            {connection.credentials.api_url}
                          </dd>
                        </div>
                      )}
                      {connection.credentials?.company_id && (
                        <div>
                          <dt className="text-gray-500">Company ID</dt>
                          <dd className="font-medium text-gray-900 font-mono text-xs">
                            {connection.credentials.company_id}
                          </dd>
                        </div>
                      )}
                      {connection.credentials?.username && (
                        <div>
                          <dt className="text-gray-500">Username</dt>
                          <dd className="font-medium text-gray-900">
                            {connection.credentials.username}
                          </dd>
                        </div>
                      )}
                      {connection.last_sync_at && (
                        <div>
                          <dt className="text-gray-500">Last Sync</dt>
                          <dd className="font-medium text-gray-900">
                            {new Date(connection.last_sync_at).toLocaleString()}
                          </dd>
                        </div>
                      )}
                      {connection.last_sync_status && (
                        <div>
                          <dt className="text-gray-500">Last Sync Status</dt>
                          <dd className="font-medium text-gray-900 capitalize">{connection.last_sync_status}</dd>
                        </div>
                      )}
                    </dl>
                  </div>
                  {connection.description && (
                    <div>
                      <h4 className="text-sm font-semibold text-gray-700 mb-2">Description</h4>
                      <p className="text-sm text-gray-600">{connection.description}</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'mapping' && (
                <FieldMappingEditor 
                  connectionId={connection.id}
                  connectionCredentials={connection.credentials}
                />
              )}

                  {activeTab === 'history' && (
                    <div className="space-y-4">
                      {/* Show detailed sync status if available */}
                      {autoSyncStatus && (
                        <div className="mb-4">
                          <h4 className="text-sm font-bold text-black mb-2">Current Sync Status:</h4>
                          <SyncDetailsView syncStatus={autoSyncStatus} />
                        </div>
                      )}
                      <SyncHistoryTab connectionId={connection.id} />
                    </div>
                  )}

              {activeTab === 'settings' && (
                <SettingsTab
                  connectionId={connection.id}
                  connectionName={connection.name}
                  credentials={connection.credentials}
                />
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Auto Sync Modal */}
      <AnimatePresence>
        {showAutoSyncModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowAutoSyncModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
                      <Zap size={20} className="text-white" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-black">One-Click Auto Sync</h3>
                      <p className="text-sm text-gray-600 font-semibold">Automatically discover entities, create mappings, and sync data</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowAutoSyncModal(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg"
                  >
                    <span className="text-2xl text-black">×</span>
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-black font-bold">
                    ✨ <strong>No manual configuration needed!</strong> Just provide your SuccessFactors credentials and we'll:
                  </p>
                  <ul className="mt-2 space-y-1 text-sm text-black ml-6 list-disc font-semibold">
                    <li>Discover all available entities (FOLegalEntity, FODepartment, etc.)</li>
                    <li>Create intelligent default field mappings</li>
                    <li>Sync all org structure data automatically</li>
                  </ul>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-bold text-black mb-2">Company ID</label>
                    <input
                      type="text"
                      value={autoSyncCredentials.company_id}
                      onChange={(e) => setAutoSyncCredentials({...autoSyncCredentials, company_id: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-semibold"
                      placeholder="Your Company ID"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-black mb-2">Username</label>
                    <input
                      type="text"
                      value={autoSyncCredentials.username}
                      onChange={(e) => setAutoSyncCredentials({...autoSyncCredentials, username: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-semibold"
                      placeholder="Your Username"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-black mb-2">Password</label>
                    <input
                      type="password"
                      value={autoSyncCredentials.password}
                      onChange={(e) => setAutoSyncCredentials({...autoSyncCredentials, password: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-semibold"
                      placeholder="Your Password"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-black mb-2">API URL</label>
                    <input
                      type="text"
                      value={autoSyncCredentials.api_url}
                      onChange={(e) => setAutoSyncCredentials({...autoSyncCredentials, api_url: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black font-semibold"
                      placeholder="https://api.successfactors.eu"
                    />
                  </div>
                </div>

                {autoSyncStatus && (
                  <div className={`p-4 rounded-lg ${
                    autoSyncStatus.status === 'completed' ? 'bg-green-50 border border-green-200' :
                    autoSyncStatus.status === 'failed' ? 'bg-red-50 border border-red-200' :
                    'bg-blue-50 border border-blue-200'
                  }`}>
                    <p className={`text-sm font-bold ${
                      autoSyncStatus.status === 'completed' ? 'text-green-700' :
                      autoSyncStatus.status === 'failed' ? 'text-red-700' :
                      'text-blue-700'
                    }`}>
                      {autoSyncStatus.message || autoSyncStatus.status}
                    </p>
                    {autoSyncStatus.processed_records !== undefined && (
                      <p className="text-xs text-black mt-1 font-semibold">
                        Processed: {autoSyncStatus.processed_records} / {autoSyncStatus.total_records} records
                      </p>
                    )}
                    
                    {/* Detailed Entity Results */}
                    {autoSyncStatus.results && Array.isArray(autoSyncStatus.results) && autoSyncStatus.results.length > 0 && (
                      <div className="mt-4 space-y-2">
                        <p className="text-xs font-bold text-black mb-2">Entity Sync Details:</p>
                        {autoSyncStatus.results.map((result: any, idx: number) => (
                          <div key={idx} className="bg-white rounded p-2 border border-gray-200">
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-semibold text-black">
                                {result.source_entity_name || result.entity_type || 'Unknown'} →
                                <span className="text-purple-600 ml-1">{result.entity_type || 'N/A'}</span>
                              </span>
                              <span className={`text-xs font-bold ${
                                result.success ? 'text-green-600' : 'text-red-600'
                              }`}>
                                {result.records_fetched || 0} records
                              </span>
                            </div>
                            {result.error && (
                              <p className="text-xs text-red-600 mt-1">{result.error}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                    
                    {/* Errors */}
                    {autoSyncStatus.errors && Array.isArray(autoSyncStatus.errors) && autoSyncStatus.errors.length > 0 && (
                      <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded">
                        <p className="text-xs font-bold text-red-700 mb-1">Errors:</p>
                        {autoSyncStatus.errors.map((error: string, idx: number) => (
                          <p key={idx} className="text-xs text-red-600">{error}</p>
                        ))}
                      </div>
                    )}
                    
                    {/* View in Org Chart Link */}
                    {autoSyncStatus.status === 'completed' && autoSyncStatus.processed_records > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-300">
                        <a
                          href="/#org-chart"
                          className="text-xs text-blue-600 hover:text-blue-800 font-semibold underline"
                        >
                          → View synced data in Org Chart
                        </a>
                      </div>
                    )}
                  </div>
                )}
              </div>

              <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
                <button
                  onClick={() => setShowAutoSyncModal(false)}
                  className="px-4 py-2 text-black hover:bg-gray-100 rounded-lg font-semibold transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => autoSyncMutation.mutate(autoSyncCredentials)}
                  disabled={autoSyncMutation.isPending || !autoSyncCredentials.company_id || !autoSyncCredentials.username || !autoSyncCredentials.password}
                  className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all font-semibold shadow-md disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                >
                  {autoSyncMutation.isPending ? (
                    <>
                      <RefreshCw size={16} className="animate-spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <Zap size={16} />
                      Start Auto Sync
                    </>
                  )}
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ConnectionCard;
