import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Map, Database, Edit, CheckCircle, XCircle } from 'lucide-react';

interface SavedMappingsViewProps {
  connectionId: string;
  onSelectMapping: (targetEntity: string, sourceEntity: string) => void;
}

interface MappingConfig {
  target_entity_type: string;
  source_entity_name: string;
  field_count: number;
  last_updated?: string;
}

const SavedMappingsView: React.FC<SavedMappingsViewProps> = ({
  connectionId,
  onSelectMapping
}) => {
  const { data: mappingConfigs, isLoading } = useQuery<MappingConfig[]>({
    queryKey: ['hris-mapping-configs', connectionId],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/mapping/configs`
      );
      if (!response.ok) return [];
      return response.json();
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-8">
        <Database className="animate-spin text-gray-400" size={20} />
        <span className="ml-2 text-sm text-gray-600">Loading saved mappings...</span>
      </div>
    );
  }

  const configs = mappingConfigs || [];

  if (configs.length === 0) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <Map size={48} className="mx-auto mb-4 text-blue-400" />
        <p className="text-sm font-medium text-blue-900 mb-2">No saved mappings yet</p>
        <p className="text-xs text-blue-700">
          Create your first mapping by selecting a target entity and SuccessFactors entity above
        </p>
      </div>
    );
  }

  // Group by target entity
  const groupedByTarget = configs.reduce((acc, config) => {
    if (!acc[config.target_entity_type]) {
      acc[config.target_entity_type] = [];
    }
    acc[config.target_entity_type].push(config);
    return acc;
  }, {} as Record<string, MappingConfig[]>);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-900">
          Saved Mappings ({configs.length} total)
        </h4>
        <span className="text-xs text-gray-500">
          Click any mapping to edit it
        </span>
      </div>

      {Object.entries(groupedByTarget).map(([targetEntity, sourceConfigs]) => (
        <div key={targetEntity} className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-3">
            <h5 className="text-sm font-semibold text-gray-900 capitalize">
              {targetEntity.replace('_', ' ')}
            </h5>
            <span className="text-xs text-gray-500">
              {sourceConfigs.length} {sourceConfigs.length === 1 ? 'mapping' : 'mappings'}
            </span>
          </div>

          <div className="space-y-2">
            {sourceConfigs.map((config) => (
              <button
                key={`${config.target_entity_type}-${config.source_entity_name}`}
                onClick={() => onSelectMapping(config.target_entity_type, config.source_entity_name)}
                className="w-full flex items-center justify-between p-3 bg-gray-50 hover:bg-green-50 border border-gray-200 hover:border-green-300 rounded-lg transition-colors text-left"
              >
                <div className="flex items-center gap-3 flex-1">
                  <CheckCircle className="text-green-600" size={18} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-semibold text-gray-900 truncate">
                      {config.source_entity_name}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {config.field_count} {config.field_count === 1 ? 'field' : 'fields'} mapped
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {config.last_updated && (
                    <span className="text-xs text-gray-400">
                      {new Date(config.last_updated).toLocaleDateString()}
                    </span>
                  )}
                  <Edit size={14} className="text-gray-400" />
                </div>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default SavedMappingsView;
