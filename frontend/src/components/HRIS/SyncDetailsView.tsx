import React from 'react';
import { CheckCircle, XCircle, Clock, Database, Users, Briefcase, Building2, ExternalLink } from 'lucide-react';

interface SyncResult {
  success: boolean;
  entity_type: string;
  source_entity_name: string;
  records_fetched: number;
  error?: string;
}

interface SyncDetailsViewProps {
  syncStatus: {
    status: string;
    message: string;
    total_records: number;
    processed_records: number;
    failed_records: number;
    results?: SyncResult[];
    errors?: string[];
    entities_found?: string[];
    current_entity?: string;
  };
}

const SyncDetailsView: React.FC<SyncDetailsViewProps> = ({ syncStatus }) => {
  const getEntityIcon = (entityName: string) => {
    if (entityName.includes('Department') || entityName.includes('Division') || entityName.includes('BusinessUnit') || entityName.includes('LegalEntity') || entityName.includes('CostCenter')) {
      return <Building2 size={16} className="text-blue-600" />;
    }
    if (entityName === 'Position') {
      return <Briefcase size={16} className="text-purple-600" />;
    }
    if (entityName === 'PerPerson' || entityName === 'User') {
      return <Users size={16} className="text-green-600" />;
    }
    return <Database size={16} className="text-gray-600" />;
  };

  const getEntityTypeLabel = (entityName: string) => {
    const labels: Record<string, string> = {
      'FODepartment': 'Department',
      'FOCostCenter': 'Cost Center',
      'FOLegalEntity': 'Legal Entity',
      'FODivision': 'Division',
      'FOBusinessUnit': 'Business Unit',
      'Position': 'Position',
      'PerPerson': 'Person',
      'User': 'User'
    };
    return labels[entityName] || entityName;
  };

  const getTargetEntityType = (sourceEntity: string) => {
    if (['FODepartment', 'FOCostCenter', 'FOLegalEntity', 'FODivision', 'FOBusinessUnit'].includes(sourceEntity)) {
      return 'Org Unit';
    }
    if (sourceEntity === 'Position') {
      return 'Position';
    }
    if (['PerPerson', 'User'].includes(sourceEntity)) {
      return 'Employee';
    }
    return 'Unknown';
  };

  return (
    <div className="space-y-4">
      {/* Summary Card */}
      <div className={`p-4 rounded-lg border-2 ${
        syncStatus.status === 'completed' ? 'bg-green-50 border-green-300' :
        syncStatus.status === 'failed' ? 'bg-red-50 border-red-300' :
        'bg-blue-50 border-blue-300'
      }`}>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            {syncStatus.status === 'completed' && <CheckCircle size={20} className="text-green-600" />}
            {syncStatus.status === 'failed' && <XCircle size={20} className="text-red-600" />}
            {(syncStatus.status === 'syncing' || syncStatus.status === 'pending' || syncStatus.status === 'mapping' || syncStatus.status === 'discovering') && <Clock size={20} className="text-blue-600 animate-pulse" />}
            <h3 className="font-bold text-black capitalize">{syncStatus.status}</h3>
          </div>
          {syncStatus.status === 'completed' && syncStatus.processed_records > 0 && (
            <a
              href="/#org-chart"
              className="flex items-center gap-1 text-sm text-blue-600 hover:text-blue-800 font-semibold"
            >
              View in Org Chart
              <ExternalLink size={14} />
            </a>
          )}
        </div>
        
        <p className="text-sm font-semibold text-black mb-3">{syncStatus.message}</p>
        
        {/* Stats */}
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white rounded p-2 border border-gray-200">
            <p className="text-xs text-gray-600 font-semibold">Total Records</p>
            <p className="text-lg font-bold text-black">{syncStatus.total_records || 0}</p>
          </div>
          <div className="bg-white rounded p-2 border border-gray-200">
            <p className="text-xs text-gray-600 font-semibold">Processed</p>
            <p className="text-lg font-bold text-green-600">{syncStatus.processed_records || 0}</p>
          </div>
          <div className="bg-white rounded p-2 border border-gray-200">
            <p className="text-xs text-gray-600 font-semibold">Failed</p>
            <p className="text-lg font-bold text-red-600">{syncStatus.failed_records || 0}</p>
          </div>
        </div>
      </div>

      {/* Current Entity Being Synced */}
      {syncStatus.current_entity && (
        <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-xs text-gray-600 font-semibold mb-1">Currently Syncing:</p>
          <div className="flex items-center gap-2">
            {getEntityIcon(syncStatus.current_entity)}
            <span className="text-sm font-bold text-black">
              {getEntityTypeLabel(syncStatus.current_entity)}
            </span>
            <span className="text-xs text-gray-600">({syncStatus.current_entity})</span>
          </div>
        </div>
      )}

      {/* Entities Found */}
      {syncStatus.entities_found && syncStatus.entities_found.length > 0 && (
        <div className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
          <p className="text-xs text-gray-600 font-semibold mb-2">Entities Discovered:</p>
          <div className="flex flex-wrap gap-2">
            {syncStatus.entities_found.map((entity, idx) => (
              <span key={idx} className="px-2 py-1 bg-white border border-gray-300 rounded text-xs font-semibold text-black">
                {getEntityTypeLabel(entity)}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Results */}
      {syncStatus.results && Array.isArray(syncStatus.results) && syncStatus.results.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-bold text-black">Entity Sync Results:</h4>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {syncStatus.results.map((result, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border ${
                  result.success
                    ? 'bg-green-50 border-green-200'
                    : 'bg-red-50 border-red-200'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-2 flex-1">
                    {getEntityIcon(result.source_entity_name || result.entity_type)}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-sm font-bold text-black">
                          {getEntityTypeLabel(result.source_entity_name || result.entity_type)}
                        </span>
                        <span className="text-xs text-gray-600">
                          ({result.source_entity_name || result.entity_type})
                        </span>
                        <span className="text-xs text-purple-600 font-semibold">
                          → {getTargetEntityType(result.source_entity_name || result.entity_type)}
                        </span>
                      </div>
                      {result.error && (
                        <p className="text-xs text-red-600 mt-1">{result.error}</p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    {result.success ? (
                      <CheckCircle size={18} className="text-green-600" />
                    ) : (
                      <XCircle size={18} className="text-red-600" />
                    )}
                    <p className={`text-sm font-bold mt-1 ${
                      result.success ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {result.records_fetched || 0}
                    </p>
                    <p className="text-xs text-gray-600">records</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Errors */}
      {syncStatus.errors && Array.isArray(syncStatus.errors) && syncStatus.errors.length > 0 && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-xs font-bold text-red-700 mb-2">Errors:</p>
          <div className="space-y-1">
            {syncStatus.errors.map((error, idx) => (
              <p key={idx} className="text-xs text-red-600">{error}</p>
            ))}
          </div>
        </div>
      )}

      {/* Where Data Appears */}
      {syncStatus.status === 'completed' && syncStatus.processed_records > 0 && (
        <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
          <h4 className="text-sm font-bold text-black mb-2">Where to View Your Data:</h4>
          <ul className="space-y-2 text-xs text-black">
            <li className="flex items-start gap-2">
              <span className="font-bold">•</span>
              <span>
                <strong>Org Chart View:</strong> Go to "Org chart" in the left sidebar to see the hierarchical structure
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">•</span>
              <span>
                <strong>People & Positions:</strong> View all synced employees and positions in a table format
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">•</span>
              <span>
                <strong>Data Breakdown:</strong>
                <ul className="ml-4 mt-1 space-y-1">
                  {syncStatus.results?.map((r, idx) => (
                    <li key={idx} className="text-gray-700">
                      {getEntityTypeLabel(r.source_entity_name || r.entity_type)}: {r.records_fetched || 0} records → {getTargetEntityType(r.source_entity_name || r.entity_type)}
                    </li>
                  ))}
                </ul>
              </span>
            </li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default SyncDetailsView;
