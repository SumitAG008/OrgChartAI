# SuccessFactors Integration Setup Guide

**Date:** 2026-01-21
**Application:** OrgChartAI
**HRIS System:** SAP SuccessFactors

---

## Overview

Your OrgChartAI application has a **fully built SuccessFactors integration** ready to use! This guide will walk you through:

1. Starting the HRIS service
2. Configuring your SuccessFactors connection
3. Setting up field mappings
4. Running your first sync
5. Viewing synced data

---

## Architecture

### What's Already Built ✅

Your HRIS integration includes:

**Backend Service (`/backend/hris-service/`):**
- ✅ SuccessFactors OData API client
- ✅ Basic Auth & OAuth support
- ✅ Data transformation engine
- ✅ Field mapping system (visual + AI-powered)
- ✅ Sync engine with history tracking
- ✅ Comprehensive error handling

**Frontend Components (`/frontend/src/components/HRIS/`):**
- ✅ Connection manager UI
- ✅ Field mapping editor (visual)
- ✅ Sync history viewer
- ✅ Connection test interface

**Database Tables:**
- ✅ `hris_field_mapping` - Field mappings
- ✅ `hris_mapping_config` - Mapping configurations
- ✅ HRIS connection storage
- ✅ Sync history tracking

**Supported SuccessFactors Entities:**
- User (employees)
- Position
- OrgUnit (generic)
- FOLegalEntity
- FODepartment
- FODivision
- FOBusinessUnit
- FOCostCenter
- PerPerson
- Custom MDF objects

---

## Prerequisites

### 1. SuccessFactors Credentials

You'll need:
- **Company ID** - Your SuccessFactors company identifier (e.g., "COMPANY123")
- **Username** - API user (format: `username@companyID`)
- **Password** - API user password
- **API URL** - SuccessFactors API endpoint (e.g., `https://api.successfactors.eu`)

### 2. SuccessFactors API Access

Ensure your SuccessFactors user has:
- OData API access enabled
- Read permissions on User, Position, OrgUnit entities
- Access to Foundation Objects (FO*)

### 3. API Endpoint URL

Determine your SuccessFactors data center:
- **EU**: `https://api.successfactors.eu`
- **US**: `https://api.successfactors.com`
- **Preview**: `https://apipreview.sapsf.com`
- **Custom**: Your specific instance URL

---

## Step 1: Start the HRIS Service

### Option A: Start All Services
```bash
cd /home/user/OrgChartAI

# Start all services (Windows)
start-all.ps1

# OR start individually
cd backend/hris-service
python main.py
```

### Option B: Start HRIS Service Only
```bash
cd /home/user/OrgChartAI/backend/hris-service

# Activate virtual environment
source ../venv/bin/activate  # Linux/Mac
# OR
../venv/Scripts/activate  # Windows

# Start service
python main.py
```

**Verify Service Running:**
```bash
# Should return service status
curl http://localhost:8002/

# Should return health check
curl http://localhost:8002/health
```

Expected response:
```json
{
  "service": "HRIS Integration Service",
  "version": "1.0.0",
  "status": "running",
  "supported_systems": [
    "SuccessFactors",
    "Workday",
    "BambooHR",
    "ADP",
    "Oracle HCM"
  ]
}
```

---

## Step 2: Configure Database Tables

Ensure HRIS mapping tables exist:

```bash
cd /home/user/OrgChartAI/backend/hris-service

# Run table setup
python setup_mapping_tables.py
```

Or manually:
```bash
cd /home/user/OrgChartAI/database

# Run HRIS schema
psql $DATABASE_URL -f hris_mapping_schema.sql
```

**Verify tables created:**
```sql
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
  AND tablename LIKE 'hris%';
```

Should show:
- `hris_field_mapping`
- `hris_mapping_config`

---

## Step 3: Configure SuccessFactors Connection

### Using the UI (Recommended)

1. **Start Frontend:**
```bash
cd /home/user/OrgChartAI/frontend
npm run dev
```

2. **Open Browser:**
Navigate to `http://localhost:5173`

3. **Go to HRIS Integration:**
- Click on HRIS menu
- Or navigate to `/hris/connections`

4. **Add New Connection:**
- Click "Add Connection" button
- Select "SAP SuccessFactors"

5. **Fill in Connection Details:**
```
Connection Name: My SuccessFactors Connection
Description: Production SF instance
Auth Method: Basic Auth

Company ID: YOUR_COMPANY_ID
Username: YOUR_USERNAME
Password: YOUR_PASSWORD
API URL: https://api.successfactors.eu
```

6. **Test Connection:**
- Click "Test Connection" button
- Wait for response
- Should see: ✅ "Connection successful - SuccessFactors API is accessible"

7. **Save Connection:**
- Click "Save Connection"
- Connection appears in list with "Active" status

### Using API (Alternative)

```bash
# Test connection first
curl -X POST http://localhost:8002/api/v1/hris/successfactors/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "YOUR_COMPANY_ID",
    "username": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "api_url": "https://api.successfactors.eu"
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Connection successful - SuccessFactors API is accessible",
  "api_version": "v2"
}
```

---

## Step 4: Fetch SuccessFactors Data (Test)

### Test Fetching Users
```bash
curl "http://localhost:8002/api/v1/hris/successfactors/users?company_id=YOUR_COMPANY_ID&username=YOUR_USERNAME&password=YOUR_PASSWORD&api_url=https://api.successfactors.eu&limit=10"
```

Expected response:
```json
{
  "count": 10,
  "users": [
    {
      "userId": "emp001",
      "username": "john.doe",
      "firstName": "John",
      "lastName": "Doe",
      "email": "john.doe@company.com",
      "department": "Engineering",
      "division": "Product Development"
    }
    // ... more users
  ]
}
```

### Test Fetching Org Units
```bash
curl "http://localhost:8002/api/v1/hris/successfactors/org-units?company_id=YOUR_COMPANY_ID&username=YOUR_USERNAME&password=YOUR_PASSWORD&api_url=https://api.successfactors.eu&limit=10"
```

### Test Fetching Positions
```bash
curl "http://localhost:8002/api/v1/hris/successfactors/positions?company_id=YOUR_COMPANY_ID&username=YOUR_USERNAME&password=YOUR_PASSWORD&api_url=https://api.successfactors.eu&limit=10"
```

---

## Step 5: Set Up Field Mappings

Field mappings tell OrgChartAI how to map SuccessFactors fields to your internal schema.

### Using Visual Mapping UI (Recommended)

1. **Go to Field Mapping:**
- In HRIS Connection Manager
- Click on your connection
- Click "Configure Field Mapping"

2. **Select Entity Type:**
- Choose: Org Units, Positions, or Employees

3. **Map Fields:**

**For Org Units:**
| SuccessFactors Field | OrgChartAI Field | Type |
|---------------------|------------------|------|
| `externalCode` | `code` | Direct |
| `name_defaultValue` | `name` | Direct |
| `parent` | `parent_org_unit_id` | Direct |
| `status` | `status` | Transform |

**For Positions:**
| SuccessFactors Field | OrgChartAI Field | Type |
|---------------------|------------------|------|
| `code` | `position_code` | Direct |
| `externalName_defaultValue` | `position_title` | Direct |
| `department` | `org_unit_id` | Lookup |
| `incumbent` | `employee_id` | Lookup |

**For Employees:**
| SuccessFactors Field | OrgChartAI Field | Type |
|---------------------|------------------|------|
| `userId` | `employee_number` | Direct |
| `firstName` | `first_name` | Direct |
| `lastName` | `last_name` | Direct |
| `email` | `email` | Direct |
| `department` | `org_unit_id` | Lookup |

4. **Save Mappings:**
- Click "Save Mapping Configuration"
- Mappings stored in `hris_field_mapping` table

### Using AI-Powered Field Matching

Your system includes AI field matching:

```bash
# Use AI to suggest field mappings
curl -X POST http://localhost:8001/api/v1/ai/match-fields \
  -H "Content-Type: application/json" \
  -d '{
    "source_fields": ["userId", "firstName", "lastName", "email"],
    "target_schema": "employee",
    "source_system": "successfactors"
  }'
```

Response includes AI suggestions with confidence scores:
```json
{
  "mappings": [
    {
      "source_field": "userId",
      "target_field": "employee_number",
      "confidence": 0.98,
      "mapping_type": "direct"
    },
    {
      "source_field": "firstName",
      "target_field": "first_name",
      "confidence": 0.99,
      "mapping_type": "direct"
    }
    // ... more mappings
  ]
}
```

---

## Step 6: Run Data Sync

### Using UI (Recommended)

1. **Go to Sync Tab:**
- In HRIS Connection Manager
- Click "Sync" tab

2. **Configure Sync:**
```
Entity Type: Org Units
Sync Mode: Full (fetch all)
Batch Size: 100
```

3. **Start Sync:**
- Click "Start Sync" button
- Progress bar shows sync status
- View real-time logs

4. **Monitor Sync:**
- See records synced count
- View any errors
- Check sync history

### Using API (Alternative)

**Full Sync (All Entities):**
```bash
curl -X POST http://localhost:8002/api/v1/hris/sync/full \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "YOUR_CONNECTION_ID",
    "entities": ["org_units", "positions", "employees"],
    "sync_mode": "full"
  }'
```

**Incremental Sync (Changes Only):**
```bash
curl -X POST http://localhost:8002/api/v1/hris/sync/incremental \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "YOUR_CONNECTION_ID",
    "entities": ["employees"],
    "since": "2026-01-01T00:00:00Z"
  }'
```

**Check Sync Status:**
```bash
curl http://localhost:8002/api/v1/hris/sync/status/{sync_id}
```

---

## Step 7: Verify Synced Data

### Check Database

**Org Units:**
```sql
SELECT id, code, name, parent_org_unit_id, status, created_at
FROM org_unit
WHERE created_by IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;
```

**Positions:**
```sql
SELECT id, position_code, position_title, org_unit_id, status
FROM position
WHERE created_by IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;
```

**Employees:**
```sql
SELECT id, employee_number, first_name, last_name, email, primary_position_id
FROM employee
WHERE created_by IS NOT NULL
ORDER BY created_at DESC
LIMIT 10;
```

### Check Sync History

```sql
SELECT
  id,
  sync_type,
  entity_type,
  records_fetched,
  records_synced,
  records_failed,
  status,
  started_at,
  completed_at
FROM hris_sync_history
ORDER BY started_at DESC
LIMIT 10;
```

### Using API

```bash
# Get sync history
curl http://localhost:8002/api/v1/hris/sync/history?limit=10
```

---

## Step 8: View in Org Chart

1. **Go to Org Chart View:**
Navigate to `http://localhost:5173/org-chart`

2. **Select Tree:**
Choose the tree/scenario that was synced

3. **Verify Data:**
- Org units appear in hierarchy
- Positions are populated
- Employees are assigned to positions
- Reporting lines are correct

---

## Advanced Configuration

### Custom MDF Objects

If you use custom MDF objects in SuccessFactors:

```bash
curl "http://localhost:8002/api/v1/hris/successfactors/custom-object?company_id=YOUR_COMPANY_ID&username=YOUR_USERNAME&password=YOUR_PASSWORD&api_url=https://api.successfactors.eu&object_name=cust_CustomOrgUnit&limit=100"
```

### Specific Foundation Objects

**Legal Entities:**
```bash
curl "http://localhost:8002/api/v1/hris/successfactors/legal-entities?..."
```

**Departments:**
```bash
curl "http://localhost:8002/api/v1/hris/successfactors/departments?..."
```

**Cost Centers:**
```bash
curl "http://localhost:8002/api/v1/hris/successfactors/cost-centers?..."
```

### Filtering Data

Use OData `$filter` parameter:

```bash
# Fetch only active employees
curl "...&filter=status eq 'active'"

# Fetch specific department
curl "...&filter=department eq 'Engineering'"

# Fetch by date range
curl "...&filter=lastModifiedDateTime gt datetime'2026-01-01T00:00:00'"
```

### Pagination

For large datasets:

```bash
# First page (skip 0, take 100)
curl "...&top=100&skip=0"

# Second page (skip 100, take 100)
curl "...&top=100&skip=100"

# Third page (skip 200, take 100)
curl "...&top=100&skip=200"
```

---

## Automated Sync

### Set Up Auto-Sync

**Daily Sync at 2 AM:**
```bash
curl -X POST http://localhost:8002/api/v1/hris/auto-sync/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "YOUR_CONNECTION_ID",
    "schedule": "0 2 * * *",
    "entities": ["org_units", "positions", "employees"],
    "sync_mode": "incremental"
  }'
```

**Schedule Formats (Cron):**
- `0 2 * * *` - Daily at 2:00 AM
- `0 */6 * * *` - Every 6 hours
- `0 0 * * 1` - Every Monday at midnight
- `*/15 * * * *` - Every 15 minutes (testing)

### Check Auto-Sync Status

```bash
curl http://localhost:8002/api/v1/hris/auto-sync/status
```

---

## Troubleshooting

### Issue: Connection Fails with 401

**Cause:** Invalid credentials

**Solution:**
1. Verify Company ID is correct
2. Ensure username format: `username@COMPANYID` (not just `username`)
3. Check password is correct
4. Verify user has API access in SuccessFactors

### Issue: Connection Fails with 406 Not Acceptable

**Cause:** Content negotiation error

**Solution:**
The client automatically handles this by trying different Accept headers. If still failing:
1. Check API URL is correct
2. Verify OData API is enabled in your SuccessFactors instance

### Issue: No Data Returned

**Cause:** User lacks permissions or entity doesn't exist

**Solution:**
1. Check user has read permissions on entities
2. Verify entity name is correct (case-sensitive)
3. Try different entity (e.g., `User` instead of `EmpJob`)

### Issue: Sync Fails Partway Through

**Cause:** Network timeout or rate limiting

**Solution:**
1. Reduce batch size: `"batch_size": 50`
2. Enable retry logic (already built-in)
3. Use incremental sync instead of full sync

### Issue: Field Mapping Errors

**Cause:** Source field doesn't exist or type mismatch

**Solution:**
1. Check SuccessFactors metadata: `GET /odata/v2/$metadata`
2. Verify field names are correct (case-sensitive)
3. Use transform function for type conversions

---

## API Endpoints Reference

### SuccessFactors Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/hris/successfactors/test-connection` | Test connection |
| GET | `/api/v1/hris/successfactors/users` | Fetch users |
| GET | `/api/v1/hris/successfactors/positions` | Fetch positions |
| GET | `/api/v1/hris/successfactors/org-units` | Fetch org units |
| GET | `/api/v1/hris/successfactors/legal-entities` | Fetch legal entities |
| GET | `/api/v1/hris/successfactors/departments` | Fetch departments |
| GET | `/api/v1/hris/successfactors/divisions` | Fetch divisions |
| GET | `/api/v1/hris/successfactors/business-units` | Fetch business units |
| GET | `/api/v1/hris/successfactors/cost-centers` | Fetch cost centers |

### Sync Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/hris/sync/full` | Full sync |
| POST | `/api/v1/hris/sync/incremental` | Incremental sync |
| GET | `/api/v1/hris/sync/status/{id}` | Check sync status |
| GET | `/api/v1/hris/sync/history` | Sync history |
| POST | `/api/v1/hris/sync/cancel/{id}` | Cancel sync |

### Mapping Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/hris/mapping` | Get mappings |
| POST | `/api/v1/hris/mapping` | Create mapping |
| PUT | `/api/v1/hris/mapping/{id}` | Update mapping |
| DELETE | `/api/v1/hris/mapping/{id}` | Delete mapping |

---

## Best Practices

### 1. Credential Security
- Never commit credentials to git
- Use environment variables
- Rotate passwords regularly
- Use API-specific users (not personal accounts)

### 2. Sync Strategy
- Start with full sync to populate data
- Switch to incremental sync for daily updates
- Schedule sync during off-peak hours
- Monitor sync failures and retry

### 3. Field Mapping
- Use AI suggestions as starting point
- Validate mappings with sample data
- Document custom transform functions
- Version control mapping configurations

### 4. Performance
- Use batching for large datasets
- Enable connection pooling
- Cache metadata (entity definitions)
- Use incremental sync for updates

### 5. Monitoring
- Check sync history regularly
- Set up alerts for sync failures
- Monitor API rate limits
- Track sync duration trends

---

## Sample Workflow

Here's a complete end-to-end workflow:

```bash
# 1. Start HRIS service
cd /home/user/OrgChartAI/backend/hris-service
python main.py

# 2. Test connection
curl -X POST http://localhost:8002/api/v1/hris/successfactors/test-connection \
  -H "Content-Type: application/json" \
  -d @connection.json

# 3. Fetch sample data (test)
curl "http://localhost:8002/api/v1/hris/successfactors/users?company_id=MYCOMPANY&username=apiuser&password=pass123&limit=10"

# 4. Set up field mappings
curl -X POST http://localhost:8002/api/v1/hris/mapping \
  -H "Content-Type: application/json" \
  -d @employee_mapping.json

# 5. Run full sync
curl -X POST http://localhost:8002/api/v1/hris/sync/full \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "conn-123",
    "entities": ["org_units", "positions", "employees"]
  }'

# 6. Check sync status
curl http://localhost:8002/api/v1/hris/sync/status/sync-123

# 7. View sync history
curl http://localhost:8002/api/v1/hris/sync/history?limit=10

# 8. Verify in database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM employee;"
```

---

## Next Steps

After successful SuccessFactors integration:

1. **Explore Data**
   - View org chart in UI
   - Check position hierarchy
   - Validate employee assignments

2. **Refine Mappings**
   - Adjust field mappings based on data quality
   - Add custom transform functions
   - Handle edge cases

3. **Set Up Automation**
   - Schedule daily sync
   - Enable sync monitoring
   - Set up failure alerts

4. **Extend Integration**
   - Add custom MDF objects
   - Integrate additional entities (Skills, Competencies)
   - Build custom reports

5. **AI Features**
   - Use AI field matching
   - Enable AI org chart generation
   - Try OrgPilot AI recommendations

---

## Support & Resources

### Internal Documentation
- `/docs/FEATURE_GAP_ANALYSIS.md` - Feature roadmap
- `/docs/IMPLEMENTATION_SUMMARY.md` - Technical overview
- `/backend/hris-service/README.md` - HRIS service docs

### SuccessFactors Documentation
- [OData API Guide](https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM/d599f15995d348a1b45ba5603e2aba9b/03e1fc3791684367a6a76a614a2916de.html)
- [Entity Definitions](https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM/d599f15995d348a1b45ba5603e2aba9b/6e1e8b6e7c5b4c6e93ab58b95f0a0f0a.html)
- [Authentication](https://help.sap.com/docs/SAP_SUCCESSFACTORS_PLATFORM/d599f15995d348a1b45ba5603e2aba9b/3c3e8f6e7c5b4c6e93ab58b95f0a0f0a.html)

### Contact
- GitHub Issues: https://github.com/SumitAG008/OrgChartAI/issues
- Email: support@orgchartai.com

---

**Document Version:** 1.0
**Last Updated:** 2026-01-21
**Status:** Ready to Use ✅

