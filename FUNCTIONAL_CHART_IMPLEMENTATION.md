# Functional Chart Implementation Guide

## Overview

The Functional Chart feature allows users to manage organizational functions, accountabilities, and their assignments. Users can add new accountabilities using the "+" button, which saves data to the backend.

## Data Structure

### Backend Database Schema

The functional chart uses 4 main tables:

1. **function_category** - Top-level categories (e.g., "People and Culture", "Governance")
   - `id` (UUID)
   - `name` (TEXT, unique)
   - `description` (TEXT)
   - `icon` (TEXT) - Emoji or icon identifier
   - `display_order` (INTEGER)
   - `is_active` (BOOLEAN)
   - Audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`, `version`

2. **function** - Functions within categories (e.g., "Compensation", "Recruitment")
   - `id` (UUID)
   - `category_id` (UUID, FK to function_category)
   - `name` (TEXT)
   - `description` (TEXT)
   - `icon` (TEXT)
   - `display_order` (INTEGER)
   - `is_active` (BOOLEAN)
   - Audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`, `version`

3. **accountability** - Specific responsibilities within functions
   - `id` (UUID)
   - `function_id` (UUID, FK to function)
   - `accountability_code` (TEXT, optional) - Accountability ID
   - `objective` (TEXT, required) - The accountability description
   - `display_order` (INTEGER)
   - `is_active` (BOOLEAN)
   - Audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`, `version`

4. **accountability_assignment** - Links accountabilities to positions/employees
   - `id` (UUID)
   - `accountability_id` (UUID, FK to accountability)
   - `position_id` (UUID, FK to position, optional)
   - `employee_id` (UUID, FK to employee, optional)
   - `assignment_type` (TEXT) - "Primary", "Secondary", or "Shared"
   - `start_date` (TIMESTAMP)
   - `end_date` (TIMESTAMP, optional)
   - `status` (TEXT) - "Active", "Completed", "Cancelled"
   - `notes` (TEXT, optional)
   - Audit fields: `created_at`, `updated_at`, `created_by`, `updated_by`, `version`

## Setup Instructions

### 1. Database Setup

Run the functional chart schema SQL:

```bash
# Connect to your PostgreSQL database
psql 'postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require'

# Run the schema file
\i database/functional_chart_schema.sql
```

This will:
- Create the 4 tables
- Add indexes for performance
- Add triggers for `updated_at` timestamps
- Insert sample data (categories and functions)

### 2. Backend Setup

The backend is already configured with:
- **Models**: `backend/org-service/app/models_db.py` (SQLAlchemy models)
- **Pydantic Models**: `backend/org-service/app/models.py` (API validation)
- **Service**: `backend/org-service/app/services/functional_chart_service.py` (Business logic)
- **Router**: `backend/org-service/app/routers/functional_chart.py` (API endpoints)
- **Main App**: Router is included in `backend/org-service/main.py`

### 3. Frontend Setup

The frontend component is located at:
- **Component**: `frontend/src/components/FunctionalChart/FunctionalChartView.tsx`
- **API Service**: `frontend/src/services/functionalChartApi.ts`
- **Integration**: Added to `frontend/src/components/OrgChart/OrgChartView.tsx`

**Note**: You need to install `@tanstack/react-query` if not already installed:

```bash
cd frontend
npm install @tanstack/react-query
```

## API Endpoints

All endpoints are prefixed with `/api/v1/functional-chart`:

### Categories
- `GET /categories` - Get all categories
- `GET /categories/{id}` - Get specific category
- `POST /categories` - Create category
- `PUT /categories/{id}` - Update category
- `DELETE /categories/{id}` - Delete category

### Functions
- `GET /functions` - Get all functions (optional `category_id` filter)
- `GET /functions/{id}` - Get specific function
- `POST /functions` - Create function
- `PUT /functions/{id}` - Update function
- `DELETE /functions/{id}` - Delete function

### Accountabilities
- `GET /accountabilities` - Get all accountabilities (optional `function_id` filter)
- `GET /accountabilities/{id}` - Get specific accountability
- `POST /accountabilities` - **Create accountability** (used by "+" button)
- `PUT /accountabilities/{id}` - Update accountability
- `DELETE /accountabilities/{id}` - Delete accountability

### Assignments
- `GET /assignments` - Get all assignments
- `POST /assignments` - Create assignment
- `PUT /assignments/{id}` - Update assignment
- `DELETE /assignments/{id}` - Delete assignment

### Full Chart
- `GET /chart` - Get complete functional chart with all categories, functions, and accountabilities

## How the "+" Button Works

### Frontend Flow

1. **User clicks "+ Add accountability" button** in `FunctionalChartView.tsx`
2. **Modal opens** with form fields:
   - Accountability ID (optional)
   - Objective (required)
3. **User fills form and clicks "Save Accountability"**
4. **`createAccountabilityMutation` is triggered**:
   ```typescript
   createAccountabilityMutation.mutate({
     function_id: selectedFunction.id,
     objective: newAccountability.objective,
     accountability_code: newAccountability.accountability_code || undefined
   });
   ```
5. **API call is made** to `POST /api/v1/functional-chart/accountabilities`
6. **On success**:
   - Query cache is invalidated
   - Modal closes
   - Functional chart refreshes to show new accountability

### Backend Flow

1. **Request received** at `POST /api/v1/functional-chart/accountabilities`
2. **Router** (`functional_chart.py`) validates request with Pydantic model
3. **Service** (`functional_chart_service.py`) creates accountability:
   ```python
   db_accountability = Accountability(**accountability.model_dump())
   db.add(db_accountability)
   await db.commit()
   ```
4. **Database** inserts new record with:
   - Auto-generated UUID
   - `created_at` = current timestamp
   - `created_by` = user ID from request
   - `version` = 1
5. **Response** returns created accountability with all fields

### Data Saved

When a user adds an accountability, the following is saved:

```json
{
  "id": "uuid-generated",
  "function_id": "uuid-of-function",
  "accountability_code": "optional-id",
  "objective": "The accountability description",
  "display_order": 0,
  "is_active": true,
  "created_at": "2025-01-XX...",
  "updated_at": "2025-01-XX...",
  "created_by": "user-uuid",
  "updated_by": null,
  "version": 1
}
```

## Example: Adding an Accountability

1. User navigates to "Functional Chart" view
2. Expands "People and Culture" category
3. Clicks "+ Add accountability" button
4. Modal opens showing:
   - Function: "Compensation"
   - Accountability ID field (optional)
   - Objective field (required)
5. User enters:
   - Objective: "Operate remuneration, incentives and benefit programs to attract, compensate and retain quality employees"
6. Clicks "Save Accountability"
7. Backend saves to `accountability` table
8. Frontend refreshes and shows the new accountability

## Sample Data

The schema includes sample data:

- **5 Categories**: People and Culture, Governance, Brand and Communications, Account Management, Commercial/Compliance/Legal
- **16 Functions** in "People and Culture": Compensation, Recruitment, Talent Development, etc.
- **1 Sample Accountability** for Compensation function

## Testing

### Test via API

```bash
# Get full chart
curl http://localhost:8000/api/v1/functional-chart/chart

# Create accountability
curl -X POST http://localhost:8000/api/v1/functional-chart/accountabilities \
  -H "Content-Type: application/json" \
  -d '{
    "function_id": "uuid-here",
    "objective": "Test accountability",
    "created_by": "00000000-0000-0000-0000-000000000000"
  }'
```

### Test via Frontend

1. Start backend: `cd backend/org-service && uvicorn main:app --reload --port 8000`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to Functional Chart view
4. Click "+ Add accountability"
5. Fill form and save
6. Verify data appears in database

## Next Steps

- Add AI suggestions for accountabilities (using "✨ Suggest" button)
- Add ability to assign accountabilities to positions/employees
- Add drag-and-drop to move accountabilities between functions
- Add bulk import from CSV
- Add export functionality
