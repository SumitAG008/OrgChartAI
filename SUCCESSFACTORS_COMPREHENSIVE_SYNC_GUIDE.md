# SuccessFactors Comprehensive Sync Guide

## Overview

This guide explains how to sync all SuccessFactors org structure entities into OrgChartAI for complete organizational visualization.

## Supported SuccessFactors Entities

### Org Unit Entities (→ `org_unit`)
- **FOLegalEntity**: Legal entities in the organization
- **FODepartment**: Departments
- **FODivision**: Divisions
- **FOBusinessUnit**: Business units
- **FOCostCenter**: Cost centers
- **Custom MDF Objects**: Any custom Metadata Framework objects

### Position Entities (→ `position`)
- **Position**: Job positions

### Employee Entities (→ `employee`)
- **PerPerson**: Person master data
- **User**: User accounts

## Comprehensive Sync Endpoint

### Start Comprehensive Sync

**Endpoint:** `POST /api/v1/hris/comprehensive-sync/start`

**Request Body:**
```json
{
  "connection_id": "your-connection-id",
  "include_custom_mdf": false,
  "custom_mdf_objects": ["CustomOrgUnit", "CustomPosition"],
  "limit_per_entity": 1000
}
```

**Response:**
```json
{
  "sync_id": "uuid",
  "status": "PENDING",
  "started_at": "2024-01-01T00:00:00Z",
  "connection_id": "your-connection-id",
  "message": "Comprehensive sync started...",
  "entities_to_sync": {
    "org_units": ["FOLegalEntity", "FODepartment", "FODivision", "FOBusinessUnit", "FOCostCenter"],
    "positions": ["Position"],
    "employees": ["PerPerson", "User"],
    "custom_mdf": []
  }
}
```

### Check Sync Status

**Endpoint:** `GET /api/v1/hris/comprehensive-sync/{sync_id}`

**Response:**
```json
{
  "sync_id": "uuid",
  "status": "COMPLETED",
  "started_at": "2024-01-01T00:00:00Z",
  "completed_at": "2024-01-01T00:05:00Z",
  "connection_id": "your-connection-id",
  "total_records": 5000,
  "processed_records": 4950,
  "failed_records": 50,
  "errors": [],
  "results": [
    {
      "success": true,
      "entity_type": "org_unit",
      "source_entity_name": "FOLegalEntity",
      "records_fetched": 10,
      "data": [...]
    },
    ...
  ]
}
```

### List All Syncs

**Endpoint:** `GET /api/v1/hris/comprehensive-sync/`

**Query Parameters:**
- `connection_id` (optional): Filter by connection
- `limit` (default: 50): Number of results to return

## Sync Process Flow

1. **Authentication**: Authenticates with SuccessFactors using Basic Auth
2. **Entity Fetching**: Fetches data from each SuccessFactors entity
3. **Data Transformation**: Applies field mappings and transformations
4. **Data Validation**: Validates transformed data
5. **Bulk Upload**: Sends data to org-service via bulk endpoints
6. **Status Tracking**: Tracks progress and errors

## Field Mapping Requirements

Before running comprehensive sync, ensure you have configured field mappings for:

### Org Units (FOLegalEntity, FODepartment, etc.)
- `hris_id` → Unique identifier from SF
- `name` → Organization unit name
- `type` → Org unit type (Legal Entity, Department, etc.)
- `parent_id` → Parent org unit reference
- `hierarchy_level` → Calculated hierarchy level
- `status` → Active/Inactive status

### Positions
- `hris_id` → Position ID from SF
- `title` → Position title
- `org_unit_id` → Associated org unit
- `status` → Position status
- `is_vacant` → Vacancy indicator

### Employees
- `hris_id` → Employee ID from SF
- `name` → Employee name
- `email` → Email address
- `position_id` → Assigned position
- `status` → Employment status

## AI Agent Integration

### Vacant Position Filling
- Positions marked as `is_vacant: true` can be filled with AI Agents
- AI Agents are treated as replaceable entities
- Cost tracking for AI Agent assignments

### Merger & Acquisition Scenarios
- Sync multiple SuccessFactors instances
- Merge org structures from different sources
- Handle duplicate entities and relationships

## Custom MDF Objects

To sync custom MDF objects:

1. Identify the MDF object name in SuccessFactors
2. Configure field mappings for the custom object
3. Include in comprehensive sync:
   ```json
   {
     "include_custom_mdf": true,
     "custom_mdf_objects": ["CustomOrgUnit", "CustomPosition"]
   }
   ```

## Visualization

After sync, all entities are available in the org chart visualization:
- Hierarchical org structure from all org units
- Positions with employee assignments
- Vacant positions (can be filled with AI Agents)
- Business functions integration
- Cost center visualization

## Best Practices

1. **Initial Sync**: Run comprehensive sync without limits to get all data
2. **Incremental Sync**: Use filters to sync only changed records
3. **Mapping Validation**: Verify mappings before full sync
4. **Error Handling**: Monitor sync status and fix errors promptly
5. **Data Quality**: Validate transformed data matches expectations

## Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify credentials format: `username@companyID:password`
   - Check API URL is correct

2. **No Mappings Found**
   - Configure field mappings before sync
   - Verify `source_entity_name` matches SF entity name

3. **Data Not Appearing in Org Chart**
   - Check org-service bulk endpoints are working
   - Verify `hris_id` is properly mapped
   - Check parent-child relationships are correct

4. **Custom MDF Objects Not Found**
   - Verify object name in SuccessFactors
   - Check object is accessible via OData API
   - Ensure proper permissions

## Next Steps

1. Configure field mappings for all entities
2. Run comprehensive sync
3. Verify data in org chart visualization
4. Set up scheduled syncs for ongoing updates
5. Configure AI Agent assignments for vacant positions
