import React, { useState, useEffect, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Save, RefreshCw, RotateCcw, Check, X, Sparkles, AlertCircle, ChevronDown, ChevronRight, Database, Search, Table, GitBranch } from 'lucide-react';
import SavedMappingsView from './SavedMappingsView';
import VisualMappingView from './VisualMappingView';

interface FieldMapping {
  id?: string;
  entity_type: string;
  source_field: string;
  target_field: string;
  mapping_type: 'direct' | 'transform' | 'custom';
  transform_function?: string;
  source_entity_name?: string; // SF entity name (e.g., 'FODepartment', 'FOBusinessUnit')
  confidence?: number; // For AI suggestions
}

interface SuccessFactorsEntity {
  name: string;
  display_name: string;
  description?: string;
  fields_count?: number;
}

interface EntityField {
  name: string;
  type: string;
  nullable: boolean;
  description?: string;
}

interface ConnectionCredentials {
  company_id?: string;
  username?: string;
  password?: string;
  api_url?: string;
  auth_method?: 'basic' | 'oauth';
}

interface FieldMappingEditorProps {
  connectionId: string;
  entityTypes?: ('org_unit' | 'position' | 'employee')[];
  connectionCredentials?: ConnectionCredentials;
}

// Target entities in OrgChartAI (what we're mapping TO)
// Required fields are marked with required: true
// Parent-child relationship fields are marked with isParentChild: true
const TARGET_ENTITIES = [
  {
    id: 'org_unit',
    name: 'Organizational Unit',
    description: 'Organizational structure units',
    fields: [
      { name: 'hris_id', required: false, description: 'HRIS system ID', isParentChild: false },
      { name: 'code', required: true, description: 'Unique organizational unit code', isParentChild: false },
      { name: 'name', required: true, description: 'Organizational unit name', isParentChild: false },
      { name: 'type', required: true, description: 'Unit type (Division, Department, Team, etc.)', isParentChild: false },
      { name: 'parent_hris_id', required: false, description: 'Parent org unit HRIS ID (for hierarchy)', isParentChild: true },
      { name: 'status', required: true, description: 'Status (Active, Planned, Inactive)', isParentChild: false },
      { name: 'effective_start_date', required: true, description: 'Effective start date', isParentChild: false },
      { name: 'effective_end_date', required: false, description: 'Effective end date', isParentChild: false },
      { name: 'description', required: false, description: 'Unit description', isParentChild: false }
    ]
  },
  {
    id: 'position',
    name: 'Position',
    description: 'Job positions',
    fields: [
      { name: 'hris_id', required: false, description: 'HRIS system ID', isParentChild: false },
      { name: 'position_code', required: true, description: 'Unique position code', isParentChild: false },
      { name: 'position_title', required: true, description: 'Position title', isParentChild: false },
      { name: 'reports_to_hris_id', required: false, description: 'Reporting position HRIS ID (for hierarchy)', isParentChild: true },
      { name: 'org_unit_hris_id', required: true, description: 'Organizational unit HRIS ID', isParentChild: false },
      { name: 'job_code', required: false, description: 'Job profile code', isParentChild: false },
      { name: 'status', required: true, description: 'Status (Active, Planned, Frozen, etc.)', isParentChild: false },
      { name: 'position_type', required: true, description: 'Position type (Permanent, FixedTerm, etc.)', isParentChild: false },
      { name: 'fte', required: false, description: 'Full-time equivalent (0.0-1.0)', isParentChild: false },
      { name: 'grade', required: false, description: 'Position grade', isParentChild: false },
      { name: 'level', required: false, description: 'Position level', isParentChild: false },
      { name: 'is_managerial', required: false, description: 'Is managerial position', isParentChild: false },
      { name: 'effective_start_date', required: true, description: 'Effective start date', isParentChild: false },
      { name: 'effective_end_date', required: false, description: 'Effective end date', isParentChild: false }
    ]
  },
  {
    id: 'employee',
    name: 'Employee',
    description: 'Employee records',
    fields: [
      { name: 'employee_number', required: true, description: 'Unique employee number', isParentChild: false },
      { name: 'first_name', required: true, description: 'First name', isParentChild: false },
      { name: 'last_name', required: true, description: 'Last name', isParentChild: false },
      { name: 'preferred_name', required: false, description: 'Preferred name', isParentChild: false },
      { name: 'email', required: true, description: 'Email address', isParentChild: false },
      { name: 'phone', required: false, description: 'Phone number', isParentChild: false },
      { name: 'position_hris_id', required: false, description: 'Primary position HRIS ID', isParentChild: false },
      { name: 'status', required: true, description: 'Status (Active, OnLeave, Terminated)', isParentChild: false },
      { name: 'hire_date', required: true, description: 'Hire date', isParentChild: false },
      { name: 'employment_type', required: true, description: 'Employment type (Permanent, FixedTerm, etc.)', isParentChild: false },
      { name: 'photo_url', required: false, description: 'Photo URL (for employee photo import)', isParentChild: false },
      { name: 'photo_base64', required: false, description: 'Photo as Base64 (for employee photo import)', isParentChild: false }
    ]
  }
];

const FieldMappingEditor: React.FC<FieldMappingEditorProps> = ({
  connectionId,
  entityTypes = ['org_unit', 'position', 'employee'],
  connectionCredentials
}) => {
  const [selectedTargetEntity, setSelectedTargetEntity] = useState<string | null>(null);
  const [selectedSFEntity, setSelectedSFEntity] = useState<string | null>(null);
  const [sfEntitySearch, setSfEntitySearch] = useState<string>('');
  const [isSFEntityDropdownOpen, setIsSFEntityDropdownOpen] = useState<boolean>(false);
  const sfEntityDropdownRef = useRef<HTMLDivElement>(null);
  const [mappings, setMappings] = useState<Record<string, FieldMapping[]>>({});
  const [hasChanges, setHasChanges] = useState(false);
  const [fetchingFields, setFetchingFields] = useState(false);
  const [viewMode, setViewMode] = useState<'table' | 'visual'>('visual'); // Default to visual view
  const queryClient = useQueryClient();

  // Use credentials from connection if available, otherwise show modal
  const [credentials, setCredentials] = useState<ConnectionCredentials | null>(
    connectionCredentials?.company_id && connectionCredentials?.username && connectionCredentials?.password
      ? {
          company_id: connectionCredentials.company_id,
          username: connectionCredentials.username,
          password: connectionCredentials.password,
          api_url: connectionCredentials.api_url || 'https://api.successfactors.eu'
        }
      : null
  );
  const [showCredentialsModal, setShowCredentialsModal] = useState(false);

  const [entitiesFromSF, setEntitiesFromSF] = useState<SuccessFactorsEntity[]>([]);
  const [hasFetchedEntities, setHasFetchedEntities] = useState(false);
  const [isAutoFetching, setIsAutoFetching] = useState(false);

  // Fetch available SuccessFactors entities (only common ones initially)
  const { data: commonEntities = [], isLoading: loadingCommonEntities } = useQuery<SuccessFactorsEntity[]>({
    queryKey: ['hris-common-entities', connectionId],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/entities`
      );
      if (!response.ok) throw new Error('Failed to fetch entities');
      return response.json();
    },
    enabled: true
  });

  // Use entities from SF if fetched, otherwise use common entities
  const sfEntities = hasFetchedEntities ? entitiesFromSF : commonEntities;
  
  // Filter entities based on search
  const filteredSFEntities = React.useMemo(() => {
    if (!sfEntitySearch.trim()) {
      return sfEntities;
    }
    const searchLower = sfEntitySearch.toLowerCase();
    return sfEntities.filter(entity => 
      entity.name.toLowerCase().includes(searchLower) ||
      (entity.display_name && entity.display_name.toLowerCase().includes(searchLower)) ||
      (entity.description && entity.description.toLowerCase().includes(searchLower))
    );
  }, [sfEntities, sfEntitySearch]);
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (sfEntityDropdownRef.current && !sfEntityDropdownRef.current.contains(event.target as Node)) {
        setIsSFEntityDropdownOpen(false);
      }
    };
    
    if (isSFEntityDropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isSFEntityDropdownOpen]);

  // Auto-fetch entities when component mounts if credentials are available
  useEffect(() => {
    if (credentials && !hasFetchedEntities && !isAutoFetching) {
      handleFetchAllEntities();
    }
  }, [credentials]);

  // Fetch fields for selected SF entity
  const { data: entityFields, isLoading: loadingFields, refetch: refetchFields } = useQuery<{entity_name: string; fields: EntityField[]}>({
    queryKey: ['hris-entity-fields', connectionId, selectedSFEntity],
    queryFn: async () => {
      if (!selectedSFEntity) return null;
      
      // If credentials available, fetch from SF
      if (credentials && credentials.company_id && credentials.username && credentials.password) {
        const response = await fetch(
          `http://localhost:8002/api/v1/hris/connections/${connectionId}/entities/${selectedSFEntity}/fetch-fields`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              company_id: credentials.company_id,
              username: credentials.username,
              password: credentials.password,
              api_url: credentials.api_url || 'https://api.successfactors.eu'
            })
          }
        );
        if (response.ok) {
          return response.json();
        }
      }
      
      // Fallback: get cached/mock fields
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/entities/${selectedSFEntity}/fields`
      );
      if (!response.ok) throw new Error('Failed to fetch fields');
      return response.json();
    },
    enabled: !!selectedSFEntity && !!credentials
  });

  // Fetch ALL mappings for this connection (to show counts on target entity cards)
  const { data: allMappingsData } = useQuery({
    queryKey: ['hris-mapping-all', connectionId],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/mapping`
      );
      if (!response.ok) {
        if (response.status === 404) return { mappings: {} };
        throw new Error('Failed to fetch mappings');
      }
      return response.json();
    },
    staleTime: 30000,
  });

  // Fetch existing mappings for selected target entity - load when target entity OR SF entity changes
  const { data: existingMappings, isLoading: loadingMappings, refetch: refetchMappings } = useQuery({
    queryKey: ['hris-mapping', connectionId, selectedTargetEntity, selectedSFEntity],
    queryFn: async () => {
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/mapping${selectedTargetEntity ? `?entity_type=${selectedTargetEntity}` : ''}`
      );
      if (!response.ok) {
        if (response.status === 404) return { mappings: {} };
        throw new Error('Failed to fetch mappings');
      }
      return response.json();
    },
    enabled: !!selectedTargetEntity,
    staleTime: 30000, // Cache for 30 seconds
  });

  // Use allMappingsData for showing counts when no target selected
  const existingMappingsForDisplay = selectedTargetEntity ? existingMappings : allMappingsData;
  
  // Get current mappings count for display
  const getMappingCountForEntity = (entityId: string) => {
    const targetMappings = existingMappingsForDisplay?.mappings?.[entityId];
    if (!targetMappings) return 0;
    if (typeof targetMappings === 'object' && !Array.isArray(targetMappings)) {
      return Object.values(targetMappings).reduce((sum: number, list: any) => 
        sum + (Array.isArray(list) ? list.length : 0), 0
      );
    }
    return Array.isArray(targetMappings) ? targetMappings.length : 0;
  };
  
  const getSourceEntitiesForEntity = (entityId: string) => {
    const targetMappings = existingMappingsForDisplay?.mappings?.[entityId];
    if (!targetMappings) return [];
    if (typeof targetMappings === 'object' && !Array.isArray(targetMappings)) {
      return Object.keys(targetMappings);
    }
    return [];
  };

  // Load mappings when they're fetched or when SF entity changes
  useEffect(() => {
    if (!existingMappings?.mappings || !selectedTargetEntity) {
      return;
    }

    const targetMappings = existingMappings.mappings[selectedTargetEntity];
    
    if (!targetMappings) {
      setMappings({});
      return;
    }

    // Backend returns: {entity_type: {source_entity: [mappings]}}
    if (typeof targetMappings === 'object' && !Array.isArray(targetMappings)) {
      if (selectedSFEntity) {
        // Get mappings for the selected SF entity
        const sfEntityMappings = targetMappings[selectedSFEntity] || [];
        if (sfEntityMappings.length > 0) {
          setMappings({
            [selectedTargetEntity]: sfEntityMappings
          });
          setHasChanges(false); // Mark as loaded, no changes yet
        } else {
          // No mappings for this SF entity, start fresh
          setMappings({});
          setHasChanges(false);
        }
      } else {
        // No SF entity selected, show all mappings flattened
        const allMappings: FieldMapping[] = [];
        Object.values(targetMappings).forEach((mappingList: any) => {
          if (Array.isArray(mappingList)) {
            allMappings.push(...mappingList);
          }
        });
        if (allMappings.length > 0) {
          setMappings({
            [selectedTargetEntity]: allMappings
          });
        } else {
          setMappings({});
        }
      }
    } else if (Array.isArray(targetMappings)) {
      // Legacy format: flat list
      setMappings({
        [selectedTargetEntity]: targetMappings
      });
    } else {
      setMappings({});
    }
  }, [existingMappings, selectedTargetEntity, selectedSFEntity]);

  // Fetch fields from SuccessFactors
  const handleFetchFromSF = async (entityName?: string) => {
    const entityToFetch = entityName || selectedSFEntity;
    if (!entityToFetch) return;
    
    if (!credentials || !credentials.company_id || !credentials.username || !credentials.password) {
      setShowCredentialsModal(true);
      return;
    }

    setFetchingFields(true);
    try {
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/entities/${entityToFetch}/fetch-fields`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            company_id: credentials.company_id,
            username: credentials.username,
            password: credentials.password,
            api_url: credentials.api_url || 'https://api.successfactors.eu'
          })
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch fields from SuccessFactors');
      }
      
      const data = await response.json();
      // Update the fields in the query cache
      queryClient.setQueryData(
        ['hris-entity-fields', connectionId, entityToFetch],
        { entity_name: entityToFetch, fields: data.fields }
      );
      // Refetch to update UI
      refetchFields();
    } catch (error: any) {
      alert(`Error fetching fields: ${error.message}`);
    } finally {
      setFetchingFields(false);
    }
  };

  // Save mappings
  const saveMutation = useMutation({
    mutationFn: async (mappingsToSave: Record<string, FieldMapping[]>) => {
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/mapping`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ mappings: mappingsToSave })
        }
      );
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to save mappings');
      }
      return response.json();
    },
    onSuccess: (data) => {
      // Invalidate all mapping queries to refresh the UI
      queryClient.invalidateQueries({ queryKey: ['hris-mapping', connectionId] });
      queryClient.invalidateQueries({ queryKey: ['hris-mapping-all', connectionId] });
      // Refetch mappings to show updated data
      refetchMappings();
      setHasChanges(false);
      // Show success message with storage location
      alert(
        `✅ Mappings saved successfully!\n\n` +
        `📊 ${data.mappings_saved || 0} mappings saved\n` +
        `💾 Storage: ${data.storage_location || 'PostgreSQL database'}\n` +
        `🔗 Connection: ${connectionId}\n` +
        `📁 Entity Types: ${data.entity_types?.join(', ') || 'N/A'}\n` +
        `📌 Source Entity: ${selectedSFEntity || 'N/A'}\n\n` +
        `💡 Tip: Your mappings are now saved. When you select this target entity and SF entity again, your mappings will automatically load.`
      );
    },
    onError: (error: Error) => {
      alert(`❌ Error saving mappings: ${error.message}`);
    }
  });

  const handleTargetEntitySelect = (targetEntityId: string) => {
    setSelectedTargetEntity(targetEntityId);
    setSelectedSFEntity(null); // Reset SF entity when target changes
    setSfEntitySearch(''); // Reset search
    setIsSFEntityDropdownOpen(false); // Close dropdown
    setMappings({});
    setHasChanges(false);
  };

  const handleSFEntitySelect = (sfEntityName: string) => {
    setSelectedSFEntity(sfEntityName);
    // Update search to show selected entity
    const selectedEntity = sfEntities.find(e => e.name === sfEntityName);
    if (selectedEntity) {
      setSfEntitySearch(selectedEntity.display_name || selectedEntity.name);
    }
    setIsSFEntityDropdownOpen(false);
    // Auto-fetch fields when SF entity is selected
    if (credentials && credentials.company_id && credentials.username && credentials.password) {
      handleFetchFromSF(sfEntityName);
    }
    // Refetch mappings for this specific SF entity
    if (selectedTargetEntity) {
      refetchMappings();
    }
  };

  const handleMappingChange = (
    sourceField: string,
    targetField: string,
    transformFunction?: string
  ) => {
    if (!selectedTargetEntity || !selectedSFEntity) return;
    
    setMappings(prev => {
      const updated = { ...prev };
      if (!updated[selectedTargetEntity]) updated[selectedTargetEntity] = [];

      const index = updated[selectedTargetEntity].findIndex(
        m => m.source_field === sourceField
      );

      const mappingType = transformFunction ? 'transform' : 'direct';

      if (index >= 0) {
        updated[selectedTargetEntity][index].target_field = targetField;
        updated[selectedTargetEntity][index].mapping_type = mappingType;
        updated[selectedTargetEntity][index].transform_function = transformFunction;
      } else {
        updated[selectedTargetEntity].push({
          entity_type: selectedTargetEntity,
          source_field: sourceField,
          target_field: targetField,
          mapping_type: mappingType,
          transform_function: transformFunction,
          source_entity_name: selectedSFEntity // Include source entity name
        });
      }

      return updated;
    });
    setHasChanges(true);
  };

  const handleRemoveMapping = (sourceField: string) => {
    if (!selectedTargetEntity) return;
    
    setMappings(prev => {
      const updated = { ...prev };
      if (updated[selectedTargetEntity]) {
        updated[selectedTargetEntity] = updated[selectedTargetEntity].filter(
          m => m.source_field !== sourceField
        );
      }
      return updated;
    });
    setHasChanges(true);
  };

  const handleFetchAllEntities = async () => {
    if (!credentials || !credentials.company_id || !credentials.username || !credentials.password) {
      setShowCredentialsModal(true);
      return;
    }
    
    try {
      setIsAutoFetching(true);
      const response = await fetch(
        `http://localhost:8002/api/v1/hris/connections/${connectionId}/fetch-metadata`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            company_id: credentials.company_id,
            username: credentials.username,
            password: credentials.password,
            api_url: credentials.api_url || 'https://api.successfactors.eu'
          })
        }
      );
      
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to fetch entities from SuccessFactors');
      }
      
      const data = await response.json();
      if (data.success && data.entities) {
        setEntitiesFromSF(data.entities);
        setHasFetchedEntities(true);
      }
    } catch (error: any) {
      console.error('Error fetching entities:', error);
      // Only show alert if user manually triggered, not auto-fetch
      if (!isAutoFetching) {
        alert(`Error fetching entities: ${error.message}`);
      }
    } finally {
      setIsAutoFetching(false);
    }
  };

  const handleSave = () => {
    if (!selectedTargetEntity || !selectedSFEntity) {
      alert('Please select both a target entity and a SuccessFactors entity before saving.');
      return;
    }
    
    // Check if there are any mappings to save
    const mappingsToSave: Record<string, FieldMapping[]> = {};
    if (mappings[selectedTargetEntity] && mappings[selectedTargetEntity].length > 0) {
      mappingsToSave[selectedTargetEntity] = mappings[selectedTargetEntity]
        .filter(m => m.target_field && m.target_field !== '') // Only save mappings with target fields
        .map(m => ({
          ...m,
          source_entity_name: m.source_entity_name || selectedSFEntity // Ensure source_entity_name is set
        }));
    }
    
    if (Object.keys(mappingsToSave).length === 0 || mappingsToSave[selectedTargetEntity].length === 0) {
      alert('Please map at least one field before saving.');
      return;
    }
    
    saveMutation.mutate(mappingsToSave);
  };

  const handleReset = () => {
    setMappings({});
    setHasChanges(true);
  };

  // Get target fields for selected target entity
  const getTargetFields = () => {
    if (!selectedTargetEntity) return [];
    const targetEntity = TARGET_ENTITIES.find(e => e.id === selectedTargetEntity);
    return targetEntity?.fields || [];
  };

  const currentMappings = selectedTargetEntity ? mappings[selectedTargetEntity] || [] : [];
  const currentFields = entityFields?.fields || [];
  const targetFields = getTargetFields();

  // Helper to detect parent-child relationship fields in SF
  const isParentChildField = (fieldName: string): boolean => {
    const parentChildPatterns = [
      /parent/i,
      /reportsTo/i,
      /reports_to/i,
      /parentId/i,
      /parent_id/i,
      /parentOrgUnit/i,
      /parent_org_unit/i,
      /superior/i,
      /manager/i,
      /headOf/i,
      /head_of/i
    ];
    return parentChildPatterns.some(pattern => pattern.test(fieldName));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Field Mapping Configuration</h3>
          <p className="text-sm text-gray-600 mt-1">
            Select a target entity (OrgChartAI), then choose a SuccessFactors entity to map fields
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleFetchAllEntities}
            disabled={!credentials && !showCredentialsModal}
            className="flex items-center gap-2 px-3 py-2 text-sm text-blue-700 bg-blue-50 border border-blue-300 rounded-lg hover:bg-blue-100 disabled:opacity-50"
            title="Fetch all entities from SuccessFactors $metadata"
          >
            <Database size={16} />
            {hasFetchedEntities ? `Entities from SF (${sfEntities.length})` : 'Fetch All Entities from SF'}
          </button>
          {isAutoFetching && (
            <span className="text-sm text-gray-500">Auto-fetching entities...</span>
          )}
          <button
            onClick={handleReset}
            className="flex items-center gap-2 px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            <RotateCcw size={16} />
            Reset to Default
          </button>
          <button
            onClick={handleSave}
            disabled={saveMutation.isPending || !selectedTargetEntity || !selectedSFEntity}
            className="flex items-center gap-2 px-3 py-2 text-sm text-white bg-green-600 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save size={16} />
            {saveMutation.isPending ? 'Saving...' : 'Save Mapping'}
          </button>
        </div>
      </div>

      {/* Saved Mappings Overview */}
      {!selectedTargetEntity && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-sm font-semibold text-gray-900 mb-4">Your Saved Mappings</h4>
          <SavedMappingsView
            connectionId={connectionId}
            onSelectMapping={(targetEntity, sourceEntity) => {
              handleTargetEntitySelect(targetEntity);
              // Auto-select the SF entity after a short delay
              setTimeout(() => {
                handleSFEntitySelect(sourceEntity);
              }, 100);
            }}
          />
        </div>
      )}

      {/* Step 1: Select Target Entity (OrgChartAI) */}
      <div className="bg-white border border-gray-200 rounded-lg p-6">
        <label className="block text-sm font-semibold text-gray-900 mb-3">
          {selectedTargetEntity ? '1. Target Entity Selected' : '1. Select Target Entity (OrgChartAI)'}
        </label>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {TARGET_ENTITIES.map((targetEntity) => {
            const mappingCount = getMappingCountForEntity(targetEntity.id);
            const sourceEntities = getSourceEntitiesForEntity(targetEntity.id);
            
            return (
              <button
                key={targetEntity.id}
                onClick={() => handleTargetEntitySelect(targetEntity.id)}
                className={`p-4 border-2 rounded-lg text-left transition-all ${
                  selectedTargetEntity === targetEntity.id
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between mb-1">
                  <div className="font-medium text-gray-900">{targetEntity.name}</div>
                  {mappingCount > 0 && (
                    <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded">
                      {mappingCount} mapped
                    </span>
                  )}
                </div>
                <div className="text-xs text-gray-600 mt-1">{targetEntity.description}</div>
                <div className="text-xs text-gray-400 mt-2">
                  {targetEntity.fields.length} target fields
                </div>
                {sourceEntities.length > 0 && (
                  <div className="mt-2 pt-2 border-t border-gray-200">
                    <p className="text-xs text-gray-500 mb-1">Mapped from:</p>
                    <div className="flex flex-wrap gap-1">
                      {sourceEntities.slice(0, 3).map((source) => (
                        <span key={source} className="px-1.5 py-0.5 bg-blue-50 text-blue-700 text-xs rounded font-mono">
                          {source}
                        </span>
                      ))}
                      {sourceEntities.length > 3 && (
                        <span className="px-1.5 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                          +{sourceEntities.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Step 2: Select SuccessFactors Entity */}
      {selectedTargetEntity && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <label className="block text-sm font-semibold text-gray-900">
              2. Select SuccessFactors Entity/API
            </label>
            {hasFetchedEntities && (
              <span className="text-xs text-green-600 font-medium">
                ✓ Fetched from SuccessFactors ({sfEntities.length} entities)
              </span>
            )}
          </div>
          
          {!hasFetchedEntities ? (
            <div className="text-center py-8 bg-blue-50 border border-blue-200 rounded-lg">
              <Database size={48} className="mx-auto mb-4 text-blue-500" />
              <p className="text-sm font-medium text-blue-900 mb-2">
                {credentials ? 'Fetching entities...' : 'Credentials needed'}
              </p>
              <p className="text-xs text-blue-700 mb-4">
                {credentials 
                  ? 'Auto-fetching entities from your SuccessFactors instance...'
                  : 'Click "Fetch All Entities from SF" to retrieve entities from your SuccessFactors $metadata endpoint.'}
              </p>
              {!credentials && (
                <button
                  onClick={() => setShowCredentialsModal(true)}
                  className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Enter Credentials
                </button>
              )}
            </div>
          ) : sfEntities.length === 0 ? (
            <div className="text-center py-8 bg-yellow-50 border border-yellow-200 rounded-lg">
              <AlertCircle size={48} className="mx-auto mb-4 text-yellow-400" />
              <p className="text-sm font-medium text-yellow-900 mb-2">No entities found</p>
              <p className="text-xs text-yellow-700">
                No entities were found in your SuccessFactors metadata.
              </p>
            </div>
          ) : (
            <div className="relative" ref={sfEntityDropdownRef}>
              {/* Searchable Dropdown */}
              <div className="relative">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={18} />
                  <input
                    type="text"
                    value={sfEntitySearch}
                    onChange={(e) => {
                      setSfEntitySearch(e.target.value);
                      setIsSFEntityDropdownOpen(true);
                    }}
                    onFocus={() => setIsSFEntityDropdownOpen(true)}
                    placeholder="Search SuccessFactors entities..."
                    className="w-full pl-10 pr-10 py-3 border-2 border-gray-300 rounded-lg focus:border-green-500 focus:ring-2 focus:ring-green-200 bg-white text-gray-900 font-medium text-sm placeholder-gray-400"
                  />
                  <ChevronDown 
                    className={`absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 transition-transform ${isSFEntityDropdownOpen ? 'rotate-180' : ''}`}
                    size={18}
                    onClick={() => setIsSFEntityDropdownOpen(!isSFEntityDropdownOpen)}
                  />
                </div>
                
                {/* Dropdown List */}
                {isSFEntityDropdownOpen && (
                  <div className="absolute z-50 w-full mt-2 bg-white border-2 border-gray-300 rounded-lg shadow-lg max-h-96 overflow-y-auto">
                    {filteredSFEntities.length === 0 ? (
                      <div className="p-4 text-center text-sm text-gray-500">
                        No entities found matching "{sfEntitySearch}"
                      </div>
                    ) : (
                      <div className="py-2">
                        {filteredSFEntities.map((entity) => (
                          <button
                            key={entity.name}
                            onClick={() => {
                              handleSFEntitySelect(entity.name);
                              setSfEntitySearch(entity.display_name || entity.name);
                              setIsSFEntityDropdownOpen(false);
                            }}
                            className={`w-full text-left px-4 py-2 hover:bg-green-50 transition-colors ${
                              selectedSFEntity === entity.name ? 'bg-green-100 border-l-4 border-green-500' : ''
                            }`}
                          >
                            <div className="flex items-center justify-between">
                              <div className="flex-1 min-w-0">
                                <div className="text-sm font-semibold text-gray-900 truncate">
                                  {entity.display_name || entity.name}
                                </div>
                                <div className="text-xs text-gray-600 font-mono truncate">
                                  {entity.name}
                                </div>
                              </div>
                              {entity.fields_count && (
                                <div className="ml-2 text-xs text-gray-500 whitespace-nowrap">
                                  {entity.fields_count} fields
                                </div>
                              )}
                            </div>
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
              
              {selectedSFEntity && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <div>
                      <span className="text-sm font-semibold text-blue-900">Selected Entity:</span>
                      <span className="ml-2 font-mono text-sm text-blue-700 font-bold">{selectedSFEntity}</span>
                    </div>
                    {loadingFields && (
                      <span className="text-xs text-blue-600 flex items-center gap-1">
                        <Database size={14} className="animate-spin" />
                        Loading fields...
                      </span>
                    )}
                  </div>
                  {entityFields && entityFields.fields && (
                    <div className="text-xs text-blue-700 font-medium mb-2">
                      <strong className="text-blue-900">{entityFields.fields.length}</strong> fields available for mapping
                    </div>
                  )}
                  {currentMappings.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-blue-200">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-semibold text-green-700">✓ Loaded:</span>
                        <span className="text-xs text-green-700 font-medium">
                          {currentMappings.length} saved {currentMappings.length === 1 ? 'mapping' : 'mappings'} for {selectedSFEntity}
                        </span>
                      </div>
                      <p className="text-xs text-blue-600 mt-1">
                        You can edit these mappings below or add new ones
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Step 3: Field Mapping Table */}
      {selectedTargetEntity && selectedSFEntity && (
        <div className="space-y-4">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-md font-semibold text-gray-900">
                3. Map Fields: <span className="text-blue-600">{selectedSFEntity}</span> → <span className="text-green-600">{TARGET_ENTITIES.find(e => e.id === selectedTargetEntity)?.name}</span>
              </h4>
              <div className="flex items-center gap-2">
                {loadingFields && (
                  <span className="text-sm text-gray-500">Loading fields...</span>
                )}
                {/* View Mode Toggle */}
                <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1">
                  <button
                    onClick={() => setViewMode('visual')}
                    className={`flex items-center gap-1 px-3 py-1.5 text-xs rounded transition-colors ${
                      viewMode === 'visual'
                        ? 'bg-green-600 text-white'
                        : 'text-gray-600 hover:bg-gray-200'
                    }`}
                    title="Visual mapping view (click to connect)"
                  >
                    <GitBranch size={14} />
                    Visual
                  </button>
                  <button
                    onClick={() => setViewMode('table')}
                    className={`flex items-center gap-1 px-3 py-1.5 text-xs rounded transition-colors ${
                      viewMode === 'table'
                        ? 'bg-green-600 text-white'
                        : 'text-gray-600 hover:bg-gray-200'
                    }`}
                    title="Table mapping view"
                  >
                    <Table size={14} />
                    Table
                  </button>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm font-bold text-white bg-blue-600 border-2 border-blue-700 p-3 rounded-lg shadow-md">
              <div className="flex items-center gap-2">
                <span className="w-4 h-4 bg-white border-2 border-blue-800 rounded"></span>
                <span className="text-white">Parent-child relationship fields (hierarchy)</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-white font-bold text-lg">*</span>
                <span className="text-white">Required fields (must be mapped)</span>
              </div>
              <div className="flex items-center gap-2">
                <ChevronRight size={16} className="text-white" />
                <span className="text-white">Hierarchy fields (for org structure)</span>
              </div>
            </div>
          </div>

          {currentFields.length === 0 ? (
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <AlertCircle size={20} className="text-yellow-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-yellow-900 mb-1">
                    No fields found
                  </p>
                  <p className="text-sm text-yellow-700">
                    Click "Fetch from SuccessFactors" to retrieve fields from your instance.
                  </p>
                </div>
              </div>
            </div>
          ) : viewMode === 'visual' ? (
            /* Visual Mapping View */
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden" style={{ minHeight: '600px' }}>
              <VisualMappingView
                sourceFields={currentFields.map(f => ({
                  name: f.name,
                  type: f.type || 'String',
                  description: f.description,
                  required: false,
                  isParentChild: isParentChildField(f.name)
                }))}
                targetFields={targetFields.map(f => {
                  const fieldName = typeof f === 'object' ? f.name : f;
                  const fieldInfo = typeof f === 'object' ? f : null;
                  return {
                    name: fieldName,
                    type: 'String', // Default type
                    description: fieldInfo?.description,
                    required: fieldInfo?.required || false,
                    isParentChild: fieldInfo?.isParentChild || false
                  };
                })}
                existingMappings={currentMappings.map(m => ({
                  source_field: m.source_field,
                  target_field: m.target_field,
                  transform_function: m.transform_function
                }))}
                onMappingChange={handleMappingChange}
                onRemoveMapping={handleRemoveMapping}
              />
            </div>
          ) : (
            /* Table Mapping View */
            <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-blue-600 border-b-2 border-blue-700">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-bold text-white uppercase bg-blue-600 border-b-2 border-blue-700">
                      SuccessFactors Field
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-bold text-white uppercase bg-blue-600 border-b-2 border-blue-700">
                      Type
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-bold text-white uppercase bg-blue-600 border-b-2 border-blue-700">
                      →
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-bold text-white uppercase bg-blue-600 border-b-2 border-blue-700">
                      → {TARGET_ENTITIES.find(e => e.id === selectedTargetEntity)?.name} Field
                      <span className="ml-2 text-white font-bold" title="Fields marked with * are required">* Required</span>
                    </th>
                    <th className="px-4 py-3 text-left text-sm font-bold text-white uppercase bg-blue-600 border-b-2 border-blue-700">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {currentFields.map((field, index) => {
                    const existingMapping = currentMappings.find(m => m.source_field === field.name);
                    const mapped = existingMapping && existingMapping.target_field;
                    const isConstantMapping = existingMapping?.transform_function?.startsWith('constant(') || false;
                    // For constant mappings, don't show source field as "mapped" since constant ignores source
                    const showAsMapped = mapped && !isConstantMapping;
                    const targetFieldInfo = mapped ? targetFields.find(f => {
                      const fieldName = typeof f === 'object' ? f.name : f;
                      return fieldName === mapped;
                    }) : null;
                    const isSFParentChild = isParentChildField(field.name);

                    return (
                      <tr 
                        key={index} 
                        className={`hover:bg-gray-50 ${
                          isSFParentChild ? 'bg-green-50/30' : ''
                        }`}
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-gray-900 font-mono">{field.name}</span>
                            {isSFParentChild && (
                              <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-bold bg-blue-600 text-white rounded border border-blue-700" title="Parent-child relationship field (for org hierarchy)">
                                <ChevronRight size={12} />
                                Hierarchy
                              </span>
                            )}
                            {field.description && (
                              <span className="text-xs text-gray-400 cursor-help" title={field.description}>
                                ℹ️
                              </span>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <span className="text-xs font-bold text-white bg-blue-600 px-2 py-1 rounded border-2 border-blue-700">
                            {field.type || 'String'}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-center text-gray-400">
                          →
                        </td>
                        <td className="px-4 py-3">
                          <div className="space-y-2">
                            <select
                              value={mapped || ''}
                              onChange={(e) => {
                                const existingMapping = currentMappings.find(m => m.source_field === field.name);
                                handleMappingChange(field.name, e.target.value, existingMapping?.transform_function);
                              }}
                              className={`w-full px-3 py-2 text-sm font-bold border-2 rounded-lg focus:outline-none focus:ring-2 ${
                                showAsMapped
                                  ? 'border-blue-600 bg-blue-100 focus:ring-blue-500 text-gray-900'
                                  : isConstantMapping
                                  ? 'border-yellow-500 bg-yellow-100 focus:ring-yellow-500 text-gray-900'
                                  : targetFieldInfo && typeof targetFieldInfo === 'object' && targetFieldInfo.required
                                  ? 'border-blue-500 focus:ring-blue-500 text-gray-900 bg-yellow-50'
                                  : 'border-gray-400 focus:ring-blue-500 text-gray-900 bg-white'
                              }`}
                            >
                              <option value="">-- Select field --</option>
                              {targetFields.map((targetField) => {
                                const fieldName = typeof targetField === 'object' ? targetField.name : targetField;
                                const fieldInfo = typeof targetField === 'object' ? targetField : null;
                                const isRequired = fieldInfo?.required || false;
                                const isParentChild = fieldInfo?.isParentChild || false;
                                const description = fieldInfo?.description || '';
                                
                                return (
                                  <option 
                                    key={fieldName} 
                                    value={fieldName}
                                    title={description}
                                  >
                                    {fieldName}
                                    {isRequired && ' *'}
                                    {isParentChild && ' (Hierarchy)'}
                                  </option>
                                );
                              })}
                            </select>
                            
                            {/* Transformation Function Selector */}
                            {mapped && !isConstantMapping && (
                              <div className="mt-1 text-xs font-bold text-blue-800 bg-blue-50 px-2 py-1 rounded border border-blue-200">
                                ⚠️ Note: When using constant transformation, the source field value is ignored
                              </div>
                            )}
                            {mapped && (
                              <div>
                                <label className="block text-xs font-bold text-gray-900 mb-1">
                                  Data Transformation (Optional):
                                </label>
                                <select
                                  value={existingMapping?.transform_function?.startsWith('constant(') ? 'constant' : (existingMapping?.transform_function || '')}
                                  onChange={(e) => {
                                    if (e.target.value === 'constant') {
                                      // When constant is selected, show input field
                                      // Set a default constant value
                                      handleMappingChange(field.name, mapped, "constant('')");
                                    } else {
                                      handleMappingChange(field.name, mapped, e.target.value || undefined);
                                    }
                                  }}
                                  className="w-full px-3 py-2 text-sm font-bold border-2 border-gray-400 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-900"
                                >
                                  <option value="">-- No transformation (direct) --</option>
                                  <optgroup label="String Transformations">
                                    <option value="uppercase">uppercase - Convert to UPPERCASE</option>
                                    <option value="lowercase">lowercase - Convert to lowercase</option>
                                    <option value="title_case">title_case - Convert to Title Case</option>
                                    <option value="trim">trim - Remove whitespace</option>
                                    <option value="map_org_unit_type">map_org_unit_type - Map SF type to internal type</option>
                                  </optgroup>
                                  <optgroup label="Date Transformations">
                                    <option value="date_format('ISO','YYYY-MM-DD')">date_format - Change date format</option>
                                  </optgroup>
                                  <optgroup label="Status Transformations">
                                    <option value="status_active">status_active - Convert to Active/Inactive</option>
                                    <option value="boolean">boolean - Convert to true/false</option>
                                  </optgroup>
                                  <optgroup label="Number Transformations">
                                    <option value="round(2)">round - Round number</option>
                                  </optgroup>
                                  <optgroup label="Constant Value">
                                    <option value="constant">constant - Set constant value (enter below)</option>
                                  </optgroup>
                                </select>
                                
                                {/* Constant Value Input Field */}
                                {(existingMapping?.transform_function?.startsWith('constant(') || 
                                    (existingMapping?.transform_function === 'constant')) && (
                                  <div className="mt-2 p-3 bg-yellow-50 border-2 border-yellow-400 rounded-lg">
                                    <label className="block text-xs font-bold text-gray-900 mb-1">
                                      Constant Value (Source Field "{field.name}" Will Be Ignored):
                                    </label>
                                    <input
                                      type="text"
                                      value={
                                        existingMapping?.transform_function?.startsWith('constant(')
                                          ? existingMapping.transform_function.replace('constant(', '').replace(')', '').replace(/'/g, '')
                                          : ''
                                      }
                                      onChange={(e) => {
                                        const constantValue = e.target.value;
                                        const transformFunc = constantValue ? `constant('${constantValue}')` : 'constant(\'\')';
                                        handleMappingChange(field.name, mapped, transformFunc);
                                      }}
                                      placeholder="Enter constant value (e.g., Active, Department, etc.)"
                                      className="w-full px-3 py-2 text-sm font-bold border-2 border-yellow-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white text-gray-900 placeholder-gray-500"
                                    />
                                    <p className="mt-2 text-xs font-bold text-yellow-900 bg-yellow-100 px-2 py-1 rounded border border-yellow-300">
                                      ⚠️ IMPORTANT: The source field "{field.name}" value will be IGNORED. The target field will always be set to the constant value above.
                                    </p>
                                  </div>
                                )}
                                
                                {existingMapping?.transform_function && 
                                 !existingMapping.transform_function.startsWith('constant(') && (
                                  <p className="mt-1 text-xs font-bold text-blue-800 bg-blue-50 px-2 py-1 rounded border border-blue-200">
                                    ✓ Will apply: {existingMapping.transform_function}
                                  </p>
                                )}
                              </div>
                            )}
                            
                            {mapped && targetFieldInfo && typeof targetFieldInfo === 'object' && (
                              <div className="mt-1 text-xs font-bold text-gray-800 bg-gray-50 px-2 py-1 rounded border border-gray-200">
                                {targetFieldInfo.description}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          {isConstantMapping ? (
                            <div className="flex flex-col gap-1">
                              <span className="inline-flex items-center gap-1 text-xs font-bold text-white bg-yellow-600 px-2 py-1 rounded border border-yellow-700">
                                Constant
                              </span>
                              <span className="text-xs font-bold text-yellow-800">
                                Source ignored
                              </span>
                              {targetFieldInfo && typeof targetFieldInfo === 'object' && targetFieldInfo.required && (
                                <span className="inline-flex items-center gap-1 text-xs font-bold text-white bg-blue-600 px-2 py-1 rounded border border-blue-700">
                                  <AlertCircle size={12} />
                                  Required
                                </span>
                              )}
                            </div>
                          ) : mapped ? (
                            <div className="flex flex-col gap-1">
                              <span className="inline-flex items-center gap-1 text-xs font-bold text-white bg-green-600 px-2 py-1 rounded border border-green-700">
                                <Check size={14} />
                                Mapped
                              </span>
                              {targetFieldInfo && typeof targetFieldInfo === 'object' && targetFieldInfo.required && (
                                <span className="inline-flex items-center gap-1 text-xs font-bold text-white bg-blue-600 px-2 py-1 rounded border border-blue-700">
                                  <AlertCircle size={12} />
                                  Required
                                </span>
                              )}
                              {targetFieldInfo && typeof targetFieldInfo === 'object' && targetFieldInfo.isParentChild && (
                                <span className="inline-flex items-center gap-1 text-xs font-bold text-white bg-purple-600 px-2 py-1 rounded border border-purple-700">
                                  <ChevronRight size={12} />
                                  Hierarchy
                                </span>
                              )}
                            </div>
                          ) : (
                            <span className="text-xs font-bold text-gray-600 bg-gray-100 px-2 py-1 rounded border border-gray-300">Unmapped</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!selectedTargetEntity && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <Database size={48} className="mx-auto mb-4 text-gray-400" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">
            Select a Target Entity
          </h4>
          <p className="text-sm text-gray-600 max-w-md mx-auto">
            Choose a target entity (OrgChartAI) above to start mapping fields from SuccessFactors.
          </p>
        </div>
      )}
      
      {selectedTargetEntity && !selectedSFEntity && hasFetchedEntities && (
        <div className="text-center py-12 bg-gray-50 rounded-lg border border-gray-200">
          <Database size={48} className="mx-auto mb-4 text-gray-400" />
          <h4 className="text-lg font-medium text-gray-900 mb-2">
            Select a SuccessFactors Entity
          </h4>
          <p className="text-sm text-gray-600 max-w-md mx-auto">
            Choose a SuccessFactors entity from the dropdown above to view and map its fields.
          </p>
        </div>
      )}

      {/* Info Box */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <Sparkles size={20} className="text-blue-600 mt-0.5" />
          <div className="flex-1">
            <h4 className="text-sm font-semibold text-blue-900 mb-1">
              How Field Mapping Works
            </h4>
            <ol className="text-sm text-blue-700 space-y-1 list-decimal list-inside">
              <li><strong>Click "Fetch All Entities from SF"</strong> - This fetches ALL entities from your SuccessFactors $metadata endpoint</li>
              <li><strong>Select an entity</strong> - Choose any entity from the list (these are the REAL entities from your SF instance)</li>
              <li><strong>Click "Fetch Fields from SF"</strong> - Gets ALL fields for that entity from your SuccessFactors metadata</li>
              <li><strong>Map each field</strong> - Map SuccessFactors fields to OrgChartAI target fields</li>
              <li><strong>Save the mapping</strong> - Your mapping configuration is saved</li>
            </ol>
            <div className="mt-3 p-2 bg-blue-100 rounded text-xs text-blue-800">
              <strong>Note:</strong> The entities shown are fetched directly from your SuccessFactors $metadata endpoint ({credentials?.api_url || 'your-api-url'}/odata/v2/$metadata). 
              You'll see whatever entities exist in your instance, not a hardcoded list.
            </div>
          </div>
        </div>
      </div>

      {/* Credentials Modal */}
      {showCredentialsModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h3 className="text-lg font-semibold mb-4">Enter SuccessFactors Credentials</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Company ID</label>
                <input
                  type="text"
                  value={credentials?.company_id || ''}
                  onChange={(e) => setCredentials({...credentials || {} as any, company_id: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="SFHUB003674"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Username</label>
                <input
                  type="text"
                  value={credentials?.username || ''}
                  onChange={(e) => setCredentials({...credentials || {} as any, username: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="sfadmin"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Password</label>
                <input
                  type="password"
                  value={credentials?.password || ''}
                  onChange={(e) => setCredentials({...credentials || {} as any, password: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">API URL</label>
                <input
                  type="text"
                  value={credentials?.api_url || 'https://api.successfactors.eu'}
                  onChange={(e) => setCredentials({...credentials || {} as any, api_url: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg"
                  placeholder="https://api.successfactors.eu"
                />
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <button
                onClick={() => setShowCredentialsModal(false)}
                className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (credentials?.company_id && credentials?.username && credentials?.password) {
                    setShowCredentialsModal(false);
                    if (selectedSFEntity) {
                      handleFetchFromSF();
                    } else {
                      handleFetchAllEntities();
                    }
                  }
                }}
                className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
              >
                Fetch
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FieldMappingEditor;
