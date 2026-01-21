# SuccessFactors $metadata Fetching Guide

## ✅ Fixed Issues

### **1. ImportError Fixed**
- ✅ Added missing `FunctionCategoryUpdate`, `FunctionUpdate`, `AccountabilityUpdate`, `AccountabilityAssignmentUpdate` models to `app/models.py`

### **2. 400 Bad Request Fixed**
- ✅ Changed `fetch-metadata` endpoint to use `CredentialsRequest` Pydantic model
- ✅ Changed `fetch-fields` endpoint to use `CredentialsRequest` Pydantic model
- ✅ Frontend now sends credentials correctly in request body

---

## 🔄 How $metadata Fetching Works

### **Step 1: Fetch All Entities**

**User Action:** Click "Fetch All Entities from SF"

**Backend Process:**
```
POST /api/v1/hris/connections/{id}/fetch-metadata
Body: {
  "company_id": "SFHUB003674",
  "username": "sfadmin",
  "password": "password",
  "api_url": "https://apisalesdemo2.successfactors.eu"
}
```

**Backend:**
1. Builds Basic Auth: `username@companyID:password` → Base64
2. Fetches: `{api_url}/odata/v2/$metadata`
3. Parses XML metadata
4. Extracts ALL EntityTypes
5. Returns list of entities

**Response:**
```json
{
  "success": true,
  "entities": [
    {"name": "OrgUnit", "display_name": "Org Unit", "fields_count": 15},
    {"name": "FOBusinessUnit", "display_name": "FO Business Unit", "fields_count": 12},
    {"name": "Position", "display_name": "Position", "fields_count": 20},
    ... (all entities from your SF instance)
  ],
  "total_entities": 150,
  "entity_sets": ["OrgUnit", "Position", "User", ...]
}
```

### **Step 2: Select Entity**

**User Action:** Click on an entity (e.g., "FOBusinessUnit")

### **Step 3: Fetch Fields for Entity**

**User Action:** Click "Fetch Fields from SF"

**Backend Process:**
```
POST /api/v1/hris/connections/{id}/entities/FOBusinessUnit/fetch-fields
Body: {
  "company_id": "SFHUB003674",
  "username": "sfadmin",
  "password": "password",
  "api_url": "https://apisalesdemo2.successfactors.eu"
}
```

**Backend:**
1. Fetches `$metadata` again
2. Finds EntityType with Name="FOBusinessUnit"
3. Extracts all Property elements (fields)
4. Returns all fields with types

**Response:**
```json
{
  "success": true,
  "entity_name": "FOBusinessUnit",
  "fields": [
    {"name": "externalCode", "type": "String", "nullable": false},
    {"name": "name", "type": "String", "nullable": false},
    {"name": "description", "type": "String", "nullable": true},
    {"name": "status", "type": "String", "nullable": true},
    ... (all fields from FOBusinessUnit)
  ],
  "fields_count": 12
}
```

---

## 🎯 Complete Flow

```
1. User opens Mapping tab
   ↓
2. User clicks "Fetch All Entities from SF"
   ↓
3. (If needed) Credentials modal appears
   User enters:
   - Company ID
   - Username
   - Password
   - API URL
   ↓
4. Backend fetches: {api_url}/odata/v2/$metadata
   ↓
5. MetadataParser parses XML
   ↓
6. Extracts ALL EntityTypes
   ↓
7. Frontend shows grid of ALL entities
   [OrgUnit] [Position] [User] [FOBusinessUnit] [CustomEntity1] ...
   ↓
8. User selects "FOBusinessUnit"
   ↓
9. User clicks "Fetch Fields from SF"
   ↓
10. Backend fetches $metadata again
    ↓
11. Parses fields for FOBusinessUnit
    ↓
12. Frontend shows table with ALL fields
    ┌─────────────────────────────────────────┐
    │ externalCode │ String │ → │ [Select...] │
    │ name         │ String │ → │ [Select...] │
    │ description  │ String │ → │ [Select...] │
    │ ...          │ ...    │ → │ ...         │
    └─────────────────────────────────────────┘
    ↓
13. User maps each field
    ↓
14. User clicks "Save Mapping"
    ↓
15. Mapping saved!
```

---

## 🔧 Metadata Parser Features

### **Namespace Handling**

The parser handles different OData namespace versions:
- `http://schemas.microsoft.com/ado/2008/09/edm` (OData v2)
- `http://schemas.microsoft.com/ado/2007/05/edm` (OData v1)
- No namespace (some implementations)

### **Field Type Cleaning**

- Removes namespace prefixes: `Edm.String` → `String`
- Handles complex types
- Preserves nullable information

### **Entity Discovery**

- Finds all EntityTypes
- Counts properties (fields)
- Detects navigation properties
- Identifies complex types

---

## 📝 API Endpoints

### **Fetch All Entities**
```http
POST /api/v1/hris/connections/{connection_id}/fetch-metadata
Content-Type: application/json

{
  "company_id": "SFHUB003674",
  "username": "sfadmin",
  "password": "your_password",
  "api_url": "https://apisalesdemo2.successfactors.eu"
}
```

### **Fetch Fields for Entity**
```http
POST /api/v1/hris/connections/{connection_id}/entities/{entity_name}/fetch-fields
Content-Type: application/json

{
  "company_id": "SFHUB003674",
  "username": "sfadmin",
  "password": "your_password",
  "api_url": "https://apisalesdemo2.successfactors.eu"
}
```

---

## ✅ What's Fixed

- ✅ ImportError for Update models
- ✅ 400 Bad Request on fetch-metadata (credentials handling)
- ✅ Metadata parser handles different namespace formats
- ✅ Frontend sends credentials correctly

**The system now fetches real entities and fields from your SuccessFactors $metadata!** 🚀
