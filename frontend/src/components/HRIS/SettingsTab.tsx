import React, { useState } from 'react';
import { Settings, Save, RefreshCw, Database, Key, Globe } from 'lucide-react';

interface ConnectionCredentials {
  company_id?: string;
  username?: string;
  password?: string;
  api_url?: string;
  auth_method?: 'basic' | 'oauth';
}

interface SettingsTabProps {
  connectionId: string;
  connectionName: string;
  credentials?: ConnectionCredentials;
  onUpdate?: () => void;
}

const SettingsTab: React.FC<SettingsTabProps> = ({
  connectionId,
  connectionName,
  credentials,
  onUpdate
}) => {
  const [formData, setFormData] = useState({
    name: connectionName,
    api_url: credentials?.api_url || '',
    company_id: credentials?.company_id || '',
    username: credentials?.username || '',
    password: credentials?.password || '',
    auth_method: credentials?.auth_method || 'basic',
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      // TODO: Implement update endpoint
      await new Promise(resolve => setTimeout(resolve, 1000));
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Connection Settings */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Settings size={20} className="text-gray-700" />
          <h4 className="text-sm font-semibold text-gray-900">Connection Settings</h4>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Connection Name
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              API URL
            </label>
            <div className="relative">
              <Globe size={16} className="absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                value={formData.api_url}
                onChange={(e) => setFormData({ ...formData, api_url: e.target.value })}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg text-sm"
                placeholder="https://api.successfactors.eu"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Authentication Settings */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <Key size={20} className="text-gray-700" />
          <h4 className="text-sm font-semibold text-gray-900">Authentication</h4>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Authentication Method
            </label>
            <select
              value={formData.auth_method}
              onChange={(e) => setFormData({ ...formData, auth_method: e.target.value as 'basic' | 'oauth' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
            >
              <option value="basic">Basic Authentication</option>
              <option value="oauth">OAuth 2.0</option>
            </select>
          </div>

          {formData.auth_method === 'basic' && (
            <>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Company ID
                </label>
                <input
                  type="text"
                  value={formData.company_id}
                  onChange={(e) => setFormData({ ...formData, company_id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  placeholder="SFHUB003674"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Username
                </label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  placeholder="API username"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">
                  Password
                </label>
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm"
                  placeholder="••••••••"
                />
              </div>
            </>
          )}
        </div>
      </div>

      {/* Sync Settings */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <div className="flex items-center gap-2 mb-4">
          <RefreshCw size={20} className="text-gray-700" />
          <h4 className="text-sm font-semibold text-gray-900">Sync Configuration</h4>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Sync Frequency
            </label>
            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm">
              <option value="manual">Manual Only</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <input type="checkbox" id="auto-sync" className="rounded" />
            <label htmlFor="auto-sync" className="text-xs text-gray-700">
              Enable automatic sync
            </label>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 text-sm font-medium"
        >
          <Save size={16} />
          {saving ? 'Saving...' : 'Save Settings'}
        </button>
      </div>
    </div>
  );
};

export default SettingsTab;
