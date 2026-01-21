import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Map, Plus, Edit, Trash2, CheckCircle, Database } from 'lucide-react';

interface MappingConfig {
  target_entity_type: string;
  source_entity_name: string;
  field_count: number;
  last_updated?: string;
}

interface MappingManagerProps {
  connectionId: string;
  targetEntity: string;
  onSelectMapping: (sourceEntity: string) => void;
  onCreateNew: () => void;
}

const MappingManager: React.FC<MappingManagerProps> = ({
  connectionId,
  targetEntity,
  onSelectMapping,
  onCreateNew
}) => {
  const { data: mappingConfigs, isLoading } = useQuery<MappingConfig[]>({
    queryKey: ['hris-mapping-configs', connectionId, targetEntity],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/mapping/configs?target_entity_type=${targetEntity}`
      );
      if (!response.ok) return [];
      return response.json();
    },
    enabled: !!targetEntity
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-4">
        <Database className="animate-spin text-gray-400" size={20} />
        <span className="ml-2 text-sm text-gray-600">Loading mappings...</span>
      </div>
    );
  }

  const configs = mappingConfigs || [];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between mb-4">
        <h4 className="text-sm font-semibold text-gray-900">
          Existing Mappings ({configs.length})
        </h4>
        <button
          onClick={onCreateNew}
          className="flex items-center gap-1 px-3 py-1.5 text-xs bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          <Plus size={14} />
          New Mapping
        </button>
      </div>

      {configs.length === 0 ? (
        <div className="text-center py-6 bg-gray-50 border border-gray-200 rounded-lg">
          <Map size={32} className="mx-auto mb-2 text-gray-400" />
          <p className="text-xs text-gray-600 mb-3">No mappings yet</p>
          <button
            onClick={onCreateNew}
            className="text-xs text-green-600 hover:text-green-700 font-medium"
          >
            Create your first mapping
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          {configs.map((config) => (
            <div
              key={`${config.target_entity_type}-${config.source_entity_name}`}
              className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
              onClick={() => onSelectMapping(config.source_entity_name)}
            >
              <div className="flex items-center gap-3 flex-1">
                <CheckCircle className="text-green-600" size={18} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-gray-900 truncate">
                    {config.source_entity_name}
                  </div>
                  <div className="text-xs text-gray-500">
                    {config.field_count} fields mapped
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onSelectMapping(config.source_entity_name);
                  }}
                  className="p-1.5 text-gray-600 hover:bg-gray-100 rounded"
                  title="Edit mapping"
                >
                  <Edit size={14} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MappingManager;
