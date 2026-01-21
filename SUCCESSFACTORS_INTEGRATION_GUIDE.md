# SuccessFactors Integration Guide

Complete guide for integrating OrgChartAI with SAP SuccessFactors.

## Overview

This guide explains how to connect your SuccessFactors instance to OrgChartAI to automatically pull employee, position, and organizational data.

## Prerequisites

1. **SuccessFactors API Access**
   - Admin access to SuccessFactors
   - API user account created
   - OData API enabled

2. **Required Information**
   - Company ID
   - API Username
   - API Password
   - API URL (e.g., `https://api.successfactors.eu`)

## Step 1: Create API User in SuccessFactors

1. Log in to SuccessFactors Admin Center
2. Navigate to **Manage Users** → **Create New User**
3. Create a technical user with:
   - User Type: **API User**
   - Permissions:
     - Read access to **User (Employee)** data
     - Read access to **Position** data
     - Read access to **OrgUnit** data
     - OData API access enabled

4. Note down:
   - Company ID (found in Company Settings)
   - API Username
   - API Password

## Step 2: Configure API URL

SuccessFactors API URLs vary by region:
- **Europe**: `https://api.successfactors.eu`
- **North America**: `https://api.successfactors.com`
- **Asia Pacific**: `https://api.successfactors.com` (APAC)

Check your SuccessFactors instance URL to determine the correct API endpoint.

## Step 3: Test Connection

### Using the API

```bash
# Test connection
curl -X POST http://localhost:8002/api/v1/hris/successfactors/test-connection \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": "YOUR_COMPANY_ID",
    "username": "api_user",
    "password": "api_password",
    "api_url": "https://api.successfactors.eu"
  }'
```

### Expected Response

```json
{
  "success": true,
  "message": "Connection successful",
  "api_version": "v2"
}
```

## Step 4: Fetch Data

### Fetch Users (Employees)

```bash
curl "http://localhost:8002/api/v1/hris/successfactors/users?company_id=YOUR_ID&username=api_user&password=api_pass&limit=100"
```

### Fetch Positions

```bash
curl "http://localhost:8002/api/v1/hris/successfactors/positions?company_id=YOUR_ID&username=api_user&password=api_pass&limit=100"
```

### Fetch Org Units

```bash
curl "http://localhost:8002/api/v1/hris/successfactors/org-units?company_id=YOUR_ID&username=api_user&password=api_pass&limit=100"
```

## Step 5: Start Full Sync

Once connection is verified, start a full synchronization:

```bash
curl -X POST http://localhost:8002/api/v1/hris/sync/start \
  -H "Content-Type: application/json" \
  -d '{
    "connection_id": "connection-uuid",
    "sync_type": "full",
    "entities": ["employees", "positions", "org_units"]
  }'
```

## Data Mapping

### SuccessFactors → OrgChartAI

| SuccessFactors | OrgChartAI | Notes |
|---------------|------------|-------|
| `User.userId` | `employee.employee_number` | Employee identifier |
| `User.firstName` | `employee.first_name` | |
| `User.lastName` | `employee.last_name` | |
| `User.displayName` | `employee.preferred_name` | |
| `User.email` | `employee.email` | |
| `User.status` | `employee.status` | Active/Inactive |
| `Position.positionId` | `position.hris_id` | Position identifier |
| `Position.positionCode` | `position.position_code` | |
| `Position.positionTitle` | `position.position_title` | |
| `Position.reportsToPositionId` | `position.reports_to_position_id` | Hierarchy |
| `OrgUnit.orgUnitId` | `org_unit.hris_id` | Org unit identifier |
| `OrgUnit.orgUnitCode` | `org_unit.code` | |
| `OrgUnit.orgUnitName` | `org_unit.name` | |
| `OrgUnit.parentOrgUnitId` | `org_unit.parent_org_unit_id` | Hierarchy |

## Sync Schedule

Recommended sync frequencies:
- **Full Sync**: Daily (overnight)
- **Incremental Sync**: Every 4-6 hours
- **Real-time**: Via webhooks (if available)

## Troubleshooting

### Authentication Errors

**Error**: `401 Unauthorized`
- Check username/password
- Verify API user has correct permissions
- Ensure OData API is enabled

**Error**: `403 Forbidden`
- Check API user permissions
- Verify data access rights

### Data Issues

**Missing Data**:
- Check field mappings
- Verify SuccessFactors has data in those fields
- Review API response for available fields

**Hierarchy Issues**:
- Ensure `reportsToPositionId` is populated
- Check for circular references
- Verify parent-child relationships

## Security Best Practices

1. **Credential Storage**
   - Never store credentials in code
   - Use encrypted storage
   - Rotate API passwords regularly

2. **API Access**
   - Use dedicated API user (not personal account)
   - Limit permissions to read-only
   - Monitor API usage

3. **Network Security**
   - Use HTTPS for all API calls
   - Implement IP whitelisting if possible
   - Monitor for suspicious activity

## Next Steps

1. **Frontend Integration**: Create UI for connection management
2. **Automated Sync**: Set up scheduled sync jobs
3. **Change Detection**: Implement incremental sync
4. **Error Handling**: Add retry logic and error notifications
5. **Monitoring**: Set up alerts for sync failures

## Support

For issues or questions:
- Check SuccessFactors API documentation
- Review logs in `backend/hris-service`
- Test connection using the test endpoint first
