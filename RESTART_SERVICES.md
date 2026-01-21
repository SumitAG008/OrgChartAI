# 🔄 Restart Services to See Database Tables

## Problem

The org-service is showing "relation does not exist" errors even though tables were created. This happens because:

1. **Service started before tables existed** - Connection pool was initialized with old schema
2. **Stale connection cache** - SQLAlchemy cached the schema information
3. **Connection pool needs refresh** - Old connections don't see new tables

## Solution: Restart Both Services

### Step 1: Stop Org Service

In the terminal where org-service is running:
- Press `Ctrl+C` to stop

### Step 2: Restart Org Service

```powershell
cd backend\org-service
uvicorn main:app --reload --port 8000
```

### Step 3: Stop HRIS Service (if running)

In the terminal where HRIS service is running:
- Press `Ctrl+C` to stop

### Step 4: Restart HRIS Service

```powershell
cd backend\hris-service
uvicorn main:app --reload --port 8002
```

## Expected Output After Restart

**Org Service:**
```
[32mINFO[0m:     Application startup complete.
[32mINFO[0m:     127.0.0.1:xxxxx - "[1mGET /api/v1/org-chart HTTP/1.1[0m" [32m200 OK[0m
```

**No more errors like:**
- ❌ "relation 'position' does not exist"
- ❌ "relation 'function_category' does not exist"
- ❌ "Returning mock org chart data..."

## Verify Tables Are Detected

After restart, test the API:

```bash
# Test org chart endpoint
curl http://localhost:8000/api/v1/org-chart

# Test functional chart endpoint
curl http://localhost:8000/api/v1/functional-chart/chart
```

**Expected:** Should return data (or empty arrays if no data yet), but NO errors about missing tables.

## Connection Pool Improvements Added

I've added these improvements to help with connection issues:

1. **`pool_pre_ping=True`** - Verifies connections before using them
2. **`pool_recycle=3600`** - Recycles connections after 1 hour
3. **`search_path: "public"`** - Explicitly sets PostgreSQL search path

These will help prevent stale connection issues in the future.

## If Still Seeing Errors

If you still see "relation does not exist" after restart:

1. **Check database connection:**
   ```python
   python verify_tables.py
   ```
   Should show all tables exist.

2. **Verify connection string:**
   - Check `backend/org-service/app/config.py`
   - Should point to Neon database, not localhost

3. **Clear Python cache:**
   ```powershell
   # Delete __pycache__ folders
   Remove-Item -Recurse -Force backend\org-service\__pycache__
   Remove-Item -Recurse -Force backend\org-service\app\__pycache__
   ```

4. **Restart again** - Sometimes Python caches need clearing

---

**After restart, both services should see all 33 tables in the database!** ✅
