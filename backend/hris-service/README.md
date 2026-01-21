# HRIS Integration Service

Microservice for integrating with HRIS systems (SuccessFactors, Workday, BambooHR, etc.)

## Features

- **SuccessFactors Integration**: OData API connector with OAuth authentication
- **Data Transformation**: Convert HRIS data to internal format
- **Synchronization**: Full and incremental sync capabilities
- **Connection Management**: Secure credential storage and management
- **Multi-HRIS Support**: Extensible architecture for multiple HRIS systems

## Setup

1. Install dependencies:
```bash
cd backend/hris-service
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
# Create .env file
DATABASE_URL=postgresql+asyncpg://user:password@host/database
SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
SUCCESSFACTORS_BASE_URL=https://api.successfactors.eu
```

3. Run the service:
```bash
uvicorn main:app --reload --port 8002
```

## API Endpoints

### Connection Management
- `GET /api/v1/hris/connections` - List all connections
- `POST /api/v1/hris/connections` - Create new connection
- `GET /api/v1/hris/connections/{id}` - Get connection details
- `PUT /api/v1/hris/connections/{id}` - Update connection
- `DELETE /api/v1/hris/connections/{id}` - Delete connection

### SuccessFactors
- `POST /api/v1/hris/successfactors/test-connection` - Test connection
- `GET /api/v1/hris/successfactors/users` - Fetch users
- `GET /api/v1/hris/successfactors/positions` - Fetch positions
- `GET /api/v1/hris/successfactors/org-units` - Fetch org units

### Synchronization
- `POST /api/v1/hris/sync/start` - Start sync job
- `GET /api/v1/hris/sync/{sync_id}` - Get sync status
- `GET /api/v1/hris/sync/` - List sync jobs

## SuccessFactors Integration

### Authentication

SuccessFactors uses OAuth 2.0 with password grant:

```python
from app.services.successfactors_client import SuccessFactorsClient

client = SuccessFactorsClient(
    company_id="your-company-id",
    username="api-user",
    password="api-password",
    api_url="https://api.successfactors.eu"
)

# Authenticate
await client.authenticate()

# Fetch data
users = await client.get_all_users()
positions = await client.get_all_positions()
org_units = await client.get_all_org_units()
```

### Required SuccessFactors Permissions

Your SuccessFactors API user needs:
- Read access to User (Employee) data
- Read access to Position data
- Read access to OrgUnit data
- OData API access enabled

## Next Steps

1. Implement database models for connections
2. Add credential encryption
3. Implement full sync pipeline
4. Add incremental sync support
5. Create frontend UI for connection management
