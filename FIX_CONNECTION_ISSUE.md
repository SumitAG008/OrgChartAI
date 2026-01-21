# Fix: Service Not Seeing Database Tables

## Problem

The org-service is showing errors that tables don't exist, even though we just created them. This happens because:

1. **Service started before tables were created** - The connection pool was initialized before tables existed
2. **Connection pool caching** - SQLAlchemy may have cached the schema

## Solution: Restart the Service

### Step 1: Stop the Current Service

In the terminal where `uvicorn` is running:
- Press `Ctrl+C` to stop the server

### Step 2: Restart the Service

```powershell
cd backend\org-service
uvicorn main:app --reload --port 8000
```

### Step 3: Verify Tables Are Detected

After restart, the service should:
- ✅ Connect to database successfully
- ✅ See all 11 tables
- ✅ Stop showing "relation does not exist" errors
- ✅ Return real data instead of mock data

## Alternative: Force Connection Refresh

If restart doesn't work, the connection pool might need to be cleared. The service will automatically reconnect on the next request.

## Expected Behavior After Fix

**Before (with errors):**
```
Database error: relation "position" does not exist
Returning mock org chart data...
```

**After (working):**
```
[INFO] Application startup complete.
[INFO] GET /api/v1/org-chart HTTP/1.1 200 OK
```

No more "relation does not exist" errors!
