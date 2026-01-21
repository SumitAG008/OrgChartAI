# One-Click Auto Sync Guide

## Overview

The **One-Click Auto Sync** feature allows you to sync all SuccessFactors org structure data with just your connection credentials. No manual mapping configuration required!

## How It Works

1. **Click "Auto Sync"** button on any SuccessFactors connection
2. **Enter your credentials** (Company ID, Username, Password, API URL)
3. **Backend automatically:**
   - Discovers all available SuccessFactors entities
   - Creates intelligent default field mappings
   - Syncs all org structure data

## What Gets Synced

### Automatically Discovered Entities

**Org Units:**
- FOLegalEntity → `org_unit`
- FODepartment → `org_unit`
- FODivision → `org_unit`
- FOBusinessUnit → `org_unit`
- FOCostCenter → `org_unit`

**Positions:**
- Position → `position`

**Employees:**
- PerPerson → `employee`
- User → `employee`

## Default Field Mappings

The system automatically creates mappings for:

### Org Units (FOLegalEntity, FODepartment, etc.)
- `externalCode` → `hris_id`
- `name` → `name`
- `status` → `status` (with `status_active` transformation)
- `parent` → `parent_id`
- `externalCode` → `code`

### Positions
- `positionId` → `hris_id`
- `positionTitle` → `title`
- `positionCode` → `code`
- `status` → `status` (with `status_active` transformation)
- `orgUnit` → `org_unit_id`

### Employees (PerPerson, User)
- `personIdExternal` / `userId` → `hris_id`
- `firstName` → `first_name`
- `lastName` → `last_name`
- `email` → `email` (with `lowercase` transformation)
- `status` → `status` (with `status_active` transformation)

## Using Auto Sync

### From UI

1. Navigate to **HRIS Connections**
2. Find your SuccessFactors connection
3. Click the **"Auto Sync"** button (purple/blue gradient button with ⚡ icon)
4. Enter your credentials in the modal
5. Click **"Start Auto Sync"**
6. Monitor progress in real-time

### From API

**Endpoint:** `POST /api/v1/hris/auto-sync/start?connection_id={connection_id}`

**Request Body:**
```json
{
  "company_id": "your-company-id",
  "username": "your-username",
  "password": "your-password",
  "api_url": "https://api.successfactors.eu"
}
```

**Response:**
```json
{
  "sync_id": "uuid",
  "status": "pending",
  "message": "Auto sync started. Discovering entities and creating mappings...",
  "connection_id": "your-connection-id",
  "connection_name": "My SuccessFactors Connection",
  "started_at": "2024-01-01T00:00:00Z"
}
```

### Check Status

**Endpoint:** `GET /api/v1/hris/auto-sync/{sync_id}`

**Response:**
```json
{
  "sync_id": "uuid",
  "status": "syncing",
  "message": "Starting data sync...",
  "connection_id": "your-connection-id",
  "entities_found": ["FOLegalEntity", "FODepartment", "Position", "PerPerson"],
  "total_records": 0,
  "processed_records": 0,
  "failed_records": 0,
  "errors": []
}
```

## Sync Process Stages

1. **Pending** - Sync job created
2. **Discovering** - Fetching $metadata from SuccessFactors
3. **Mapping** - Creating default field mappings
4. **Syncing** - Fetching and transforming data
5. **Completed** - All data synced successfully
6. **Failed** - Error occurred (check errors array)

## Benefits

✅ **No Manual Configuration** - Everything is automatic  
✅ **Intelligent Defaults** - Smart field mappings based on entity types  
✅ **Complete Coverage** - Syncs all org structure entities  
✅ **Real-time Progress** - Monitor sync status as it happens  
✅ **Error Handling** - Clear error messages if something goes wrong  

## Customization After Auto Sync

After auto sync completes, you can:
- Review created mappings in the **Mapping** tab
- Adjust field mappings as needed
- Add custom transformations
- Configure custom MDF objects

## Troubleshooting

### Authentication Failed
- Verify credentials format: `username@companyID:password`
- Check API URL is correct for your region

### No Entities Found
- Verify your SuccessFactors instance has the entities enabled
- Check API permissions for your user

### Mapping Errors
- Review created mappings in the Mapping tab
- Adjust mappings manually if needed
- Default mappings work for standard SF configurations

## Next Steps

After auto sync:
1. ✅ View your org structure in the org chart
2. ✅ Verify data looks correct
3. ✅ Adjust mappings if needed
4. ✅ Set up scheduled syncs for ongoing updates
5. ✅ Configure AI Agent assignments for vacant positions
