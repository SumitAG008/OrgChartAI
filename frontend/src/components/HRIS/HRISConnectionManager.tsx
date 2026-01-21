import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Settings, CheckCircle, XCircle, RefreshCw, 
  Database, Key, Globe, AlertCircle, Plus,
  Trash2, Play, Pause, Clock
} from 'lucide-react';
import ConnectionCard from './ConnectionCard';

interface HRISConnection {
  id: string;
  name: string;
  system: string;
  status: 'active' | 'inactive' | 'error' | 'testing';
  last_sync_at?: string;
  last_sync_status?: string;
  description?: string;
}

const HRISConnectionManager: React.FC = () => {
  const [connections, setConnections] = useState<HRISConnection[]>([]);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedSystem, setSelectedSystem] = useState<string>('successfactors');
  const [authMethod, setAuthMethod] = useState<'basic' | 'oauth'>('basic');
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    company_id: '',
    username: '',
    password: '',
    api_url: 'https://api.successfactors.eu',
    // OAuth fields
    client_id: '',
    client_secret: '',
    token_url: ''
  });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{success: boolean; message: string} | null>(null);

  const systems = [
    { id: 'successfactors', name: 'SAP SuccessFactors', icon: '🔵' },
    { id: 'workday', name: 'Workday', icon: '🟠' },
    { id: 'bamboohr', name: 'BambooHR', icon: '🟢' },
    { id: 'adp', name: 'ADP Workforce Now', icon: '🔴' },
    { id: 'oracle_hcm', name: 'Oracle HCM Cloud', icon: '🟣' }
  ];

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    
    try {
      const requestBody: any = {
        api_url: formData.api_url,
        auth_method: authMethod
      };

      if (authMethod === 'basic') {
        requestBody.company_id = formData.company_id;
        requestBody.username = formData.username;
        requestBody.password = formData.password;
      } else {
        requestBody.client_id = formData.client_id;
        requestBody.client_secret = formData.client_secret;
        requestBody.token_url = formData.token_url || `${formData.api_url}/oauth/token`;
      }

      const response = await fetch('http://localhost:8002/api/v1/hris/successfactors/test-connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      
      const result = await response.json();
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        message: `Connection error: ${error}`
      });
    } finally {
      setTesting(false);
    }
  };

  const handleSaveConnection = async () => {
    if (!testResult?.success) {
      alert('Please test connection first');
      return;
    }

    // Save connection with credentials
    const newConnection: HRISConnection = {
      id: `conn-${Date.now()}`,
      name: formData.name,
      system: selectedSystem,
      status: 'active',
      description: formData.description,
      credentials: {
        company_id: formData.company_id,
        username: formData.username,
        password: formData.password,
        api_url: formData.api_url,
        auth_method: authMethod
      }
    };

    setConnections([...connections, newConnection]);
    setShowAddModal(false);
    setFormData({
      name: '',
      description: '',
      company_id: '',
      username: '',
      password: '',
      api_url: 'https://api.successfactors.eu',
      client_id: '',
      client_secret: '',
      token_url: ''
    });
    setAuthMethod('basic');
    setTestResult(null);
  };

  const handleSync = async (connectionId: string) => {
    // TODO: Start sync
    console.log('Starting sync for:', connectionId);
  };

  return (
    <div className="p-6 bg-white rounded-lg shadow-lg">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">HRIS Connections</h2>
          <p className="text-gray-600 mt-1">Connect and sync data from your HRIS system</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg transition-all"
        >
          <Plus size={20} />
          Add Connection
        </button>
      </div>

      {/* Connections List */}
      {connections.length === 0 ? (
        <div className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg">
          <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-700 mb-2">No Connections</h3>
          <p className="text-gray-500 mb-4">Get started by adding your first HRIS connection</p>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Add Connection
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {connections.map((conn) => (
            <ConnectionCard
              key={conn.id}
              connection={conn}
              onSync={handleSync}
              onDelete={(id) => {
                setConnections(connections.filter(c => c.id !== id));
              }}
            />
          ))}
        </div>
      )}

      {/* Add Connection Modal */}
      <AnimatePresence>
        {showAddModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
            onClick={() => setShowAddModal(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-white rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            >
              <div className="p-6 border-b border-gray-200">
                <h3 className="text-xl font-bold text-gray-900">Add HRIS Connection</h3>
                <p className="text-sm text-gray-600 mt-1">Connect to your HRIS system to sync organizational data</p>
              </div>

              <div className="p-6 space-y-6">
                {/* System Selection */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    HRIS System
                  </label>
                  <div className="grid grid-cols-2 gap-3">
                    {systems.map((system) => (
                      <button
                        key={system.id}
                        onClick={() => setSelectedSystem(system.id)}
                        className={`p-4 border-2 rounded-lg text-left transition-all ${
                          selectedSystem === system.id
                            ? 'border-green-500 bg-green-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className="text-2xl">{system.icon}</span>
                          <span className="font-medium text-gray-900">{system.name}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Connection Details */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Connection Name *
                    </label>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({...formData, name: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="e.g., Production SuccessFactors"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Description
                    </label>
                    <textarea
                      value={formData.description}
                      onChange={(e) => setFormData({...formData, description: e.target.value})}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      rows={2}
                      placeholder="Optional description"
                    />
                  </div>

                  {/* SuccessFactors Specific Fields */}
                  {selectedSystem === 'successfactors' && (
                    <>
                      {/* Authentication Method Selection */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Authentication Method *
                        </label>
                        <select
                          value={authMethod}
                          onChange={(e) => {
                            setAuthMethod(e.target.value as 'basic' | 'oauth');
                            setTestResult(null); // Clear previous test results
                          }}
                          className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white text-base font-semibold text-gray-900"
                          style={{ color: '#111827', fontWeight: '600' }}
                        >
                          <option value="basic" style={{ color: '#111827', fontWeight: '600' }}>
                            🔐 Basic Authentication (Recommended)
                          </option>
                          <option value="oauth" style={{ color: '#111827', fontWeight: '600' }}>
                            🔑 OAuth 2.0
                          </option>
                        </select>
                        <p className="text-xs text-gray-600 mt-2 font-medium">
                          {authMethod === 'basic' 
                            ? '✓ Uses username@companyID:password format (standard for SuccessFactors OData API)'
                            : '✓ Uses OAuth 2.0 client credentials flow'}
                        </p>
                      </div>

                      {/* Basic Authentication Fields */}
                      {authMethod === 'basic' && (
                        <>
                          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-300 rounded-lg p-5">
                            <div className="flex items-start gap-3">
                              <AlertCircle className="w-6 h-6 text-blue-600 mt-0.5 flex-shrink-0" />
                              <div className="flex-1">
                                <p className="font-bold text-blue-900 mb-2 text-base">How SuccessFactors Authentication Works</p>
                                
                                {/* Visual Explanation */}
                                <div className="bg-white rounded-lg p-4 mb-3 border border-blue-200">
                                  <p className="text-xs font-semibold text-gray-700 mb-2">Step 1: Fill in these THREE separate fields:</p>
                                  <div className="space-y-2 text-sm">
                                    <div className="flex items-center gap-2">
                                      <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded font-mono text-xs font-bold">1</span>
                                      <span className="text-gray-700"><strong>Company ID:</strong> <code className="bg-gray-100 px-1 rounded">SFHUB003674</code></span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded font-mono text-xs font-bold">2</span>
                                      <span className="text-gray-700"><strong>Username:</strong> <code className="bg-gray-100 px-1 rounded">sfadmin</code></span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                      <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded font-mono text-xs font-bold">3</span>
                                      <span className="text-gray-700"><strong>Password:</strong> <code className="bg-gray-100 px-1 rounded">your_password</code></span>
                                    </div>
                                  </div>
                                </div>

                                <div className="bg-white rounded-lg p-4 mb-3 border border-blue-200">
                                  <p className="text-xs font-semibold text-gray-700 mb-2">Step 2: System automatically combines them:</p>
                                  <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-sm font-bold text-center">
                                    <span className="text-yellow-300">sfadmin</span>
                                    <span className="text-white">@</span>
                                    <span className="text-yellow-300">SFHUB003674</span>
                                    <span className="text-white">:</span>
                                    <span className="text-yellow-300">your_password</span>
                                  </div>
                                  <p className="text-xs text-gray-600 mt-2 text-center">
                                    Format: <code className="bg-gray-100 px-1 rounded">username@companyID:password</code>
                                  </p>
                                </div>

                                <div className="bg-white rounded-lg p-4 border border-blue-200">
                                  <p className="text-xs font-semibold text-gray-700 mb-2">Step 3: System Base64 encodes it:</p>
                                  <div className="bg-gray-900 text-green-400 p-3 rounded font-mono text-xs break-all">
                                    c2ZhZG1pbkBTSEhVQjAwMzY3NDp5b3VyX3Bhc3N3b3Jk
                                  </div>
                                  <p className="text-xs text-gray-600 mt-2">
                                    This encoded string is sent as: <code className="bg-gray-100 px-1 rounded">Authorization: Basic [encoded_string]</code>
                                  </p>
                                </div>

                                <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded">
                                  <p className="text-xs text-yellow-800">
                                    <strong>💡 Why three fields?</strong> SuccessFactors requires this specific format. 
                                    We keep them separate so you can easily update individual values without retyping everything.
                                  </p>
                                </div>
                              </div>
                            </div>
                          </div>

                          <div className="bg-white border-2 border-blue-200 rounded-lg p-4">
                            <h4 className="font-bold text-gray-900 mb-4 text-base">Enter Your Credentials:</h4>
                            
                            <div className="space-y-4">
                              <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                  <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs mr-2">1</span>
                                  Company ID *
                                </label>
                                <input
                                  type="text"
                                  value={formData.company_id}
                                  onChange={(e) => setFormData({...formData, company_id: e.target.value})}
                                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base"
                                  placeholder="SFHUB003674"
                                />
                                <div className="mt-2 p-2 bg-gray-50 rounded">
                                  <p className="text-xs text-gray-600">
                                    <strong>Example:</strong> <code className="bg-white px-2 py-0.5 rounded border">SFHUB003674</code>
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    Found in SuccessFactors → Company Settings → Company Information
                                  </p>
                                </div>
                              </div>

                              <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                  <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs mr-2">2</span>
                                  API Username *
                                </label>
                                <input
                                  type="text"
                                  value={formData.username}
                                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base"
                                  placeholder="sfadmin"
                                />
                                <div className="mt-2 p-2 bg-gray-50 rounded">
                                  <p className="text-xs text-gray-600">
                                    <strong>Example:</strong> <code className="bg-white px-2 py-0.5 rounded border">sfadmin</code>
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    The username of your SuccessFactors API user account (created in Admin Center)
                                  </p>
                                </div>
                              </div>

                              <div>
                                <label className="block text-sm font-bold text-gray-700 mb-2">
                                  <span className="bg-blue-100 text-blue-700 px-2 py-0.5 rounded text-xs mr-2">3</span>
                                  API Password *
                                </label>
                                <input
                                  type="password"
                                  value={formData.password}
                                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-base"
                                  placeholder="Enter your password"
                                />
                                <div className="mt-2 p-2 bg-gray-50 rounded">
                                  <p className="text-xs text-gray-600">
                                    <strong>Example:</strong> <code className="bg-white px-2 py-0.5 rounded border">MySecurePassword123</code>
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    The password for your SuccessFactors API user account
                                  </p>
                                </div>
                              </div>
                            </div>

                            {/* Live Preview */}
                            {(formData.company_id || formData.username || formData.password) && (
                              <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                                <p className="text-xs font-semibold text-green-800 mb-2">📋 Preview (what will be sent):</p>
                                <div className="bg-gray-900 text-green-400 p-2 rounded font-mono text-xs break-all">
                                  {formData.username || 'username'}@{formData.company_id || 'companyID'}:{formData.password ? '••••••••' : 'password'}
                                </div>
                                <p className="text-xs text-green-700 mt-2">
                                  This will be Base64 encoded automatically when you test the connection
                                </p>
                              </div>
                            )}
                          </div>
                        </>
                      )}

                      {/* OAuth Fields */}
                      {authMethod === 'oauth' && (
                        <>
                          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                            <div className="flex items-start gap-2">
                              <AlertCircle className="w-5 h-5 text-amber-600 mt-0.5 flex-shrink-0" />
                              <div className="text-sm text-amber-800">
                                <p className="font-medium mb-1">OAuth 2.0 Configuration</p>
                                <p className="text-xs">
                                  Requires OAuth 2.0 client credentials configured in SuccessFactors Admin Center
                                </p>
                              </div>
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Client ID *
                            </label>
                            <input
                              type="text"
                              value={formData.client_id}
                              onChange={(e) => setFormData({...formData, client_id: e.target.value})}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                              placeholder="OAuth client ID"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Client Secret *
                            </label>
                            <input
                              type="password"
                              value={formData.client_secret}
                              onChange={(e) => setFormData({...formData, client_secret: e.target.value})}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                              placeholder="••••••••"
                            />
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Token URL
                            </label>
                            <input
                              type="text"
                              value={formData.token_url || `${formData.api_url}/oauth/token`}
                              onChange={(e) => setFormData({...formData, token_url: e.target.value})}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                              placeholder="https://api.successfactors.eu/oauth/token"
                            />
                          </div>
                        </>
                      )}

                      {/* API URL (Common for both methods) */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          API URL *
                        </label>
                        <input
                          type="text"
                          value={formData.api_url}
                          onChange={(e) => setFormData({...formData, api_url: e.target.value})}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                          placeholder="https://api.successfactors.eu"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          <strong>Europe:</strong> api.successfactors.eu | <strong>North America:</strong> api.successfactors.com
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          For demo instances: apisalesdemo2.successfactors.eu
                        </p>
                      </div>
                    </>
                  )}
                </div>

                {/* Test Connection */}
                <div className="border-t border-gray-200 pt-4">
                  <button
                    onClick={handleTestConnection}
                    disabled={
                      testing || 
                      !formData.api_url ||
                      (authMethod === 'basic' && (!formData.company_id || !formData.username || !formData.password)) ||
                      (authMethod === 'oauth' && (!formData.client_id || !formData.client_secret))
                    }
                    className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {testing ? (
                      <>
                        <RefreshCw size={18} className="animate-spin" />
                        Testing Connection...
                      </>
                    ) : (
                      <>
                        <Key size={18} />
                        Test Connection
                      </>
                    )}
                  </button>

                  {testResult && (
                    <div className={`mt-3 p-3 rounded-lg flex items-center gap-2 ${
                      testResult.success ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                    }`}>
                      {testResult.success ? (
                        <CheckCircle size={20} />
                      ) : (
                        <XCircle size={20} />
                      )}
                      <span className="text-sm">{testResult.message}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Modal Footer */}
              <div className="p-6 border-t border-gray-200 flex items-center justify-end gap-3">
                <button
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveConnection}
                  disabled={!testResult?.success}
                  className="px-4 py-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  Save Connection
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};


export default HRISConnectionManager;
