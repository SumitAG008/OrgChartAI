# Where to Provide SuccessFactors Connection Details

## 🎯 Quick Answer

**Location:** HRIS Connections Page → "Add Connection" or "Auto Sync" Button

## Step-by-Step Guide

### Option 1: Add New Connection (Recommended First Time)

1. **Navigate to HRIS Connections**
   - Click on "HRIS" or "Connections" in the main navigation
   - Or go to: `http://localhost:3000/#/hris` (if you have routing)

2. **Click "Add Connection" Button**
   - Usually a prominent button at the top of the connections list
   - Or a "+" icon/button

3. **Fill in Connection Form:**
   ```
   Connection Name: My SuccessFactors Connection
   System: SuccessFactors
   Company ID: [Your Company ID]
   Username: [Your Username]
   Password: [Your Password]
   API URL: https://api.successfactors.eu (or your region URL)
   Authentication Method: Basic Auth
   ```

4. **Click "Test Connection"** to verify
5. **Click "Save"** to create the connection

### Option 2: One-Click Auto Sync (Easiest!)

1. **Find Your Connection Card**
   - Look for the connection you created
   - Each connection has a card with connection details

2. **Click "Auto Sync" Button**
   - Purple/Blue gradient button with ⚡ icon
   - Located on the connection card header

3. **Enter Credentials in Modal:**
   ```
   Company ID: [Your Company ID]
   Username: [Your Username]  
   Password: [Your Password]
   API URL: https://api.successfactors.eu
   ```

4. **Click "Start Auto Sync"**
   - Backend automatically:
     - Discovers all entities
     - Creates mappings
     - Syncs all data

## Visual Guide

```
┌─────────────────────────────────────────────────┐
│  HRIS Connections                                │
│  ┌───────────────────────────────────────────┐  │
│  │ [+ Add Connection]  [🔍 Search]          │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  ┌───────────────────────────────────────────┐  │
│  │ 🔵 My SuccessFactors Connection            │  │
│  │    SuccessFactors                         │  │
│  │    Last sync: Never                       │  │
│  │                                            │  │
│  │    [⚡ Auto Sync] [🔄] [🗑️]                │  │
│  └───────────────────────────────────────────┘  │
│                                                   │
│  When you click "Auto Sync":                    │
│  ┌───────────────────────────────────────────┐  │
│  │ ⚡ One-Click Auto Sync                     │  │
│  │                                            │  │
│  │ Company ID: [________________]            │  │
│  │ Username:   [________________]            │  │
│  │ Password:   [________________]            │  │
│  │ API URL:    [________________]            │  │
│  │                                            │  │
│  │        [Cancel]  [Start Auto Sync]        │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

## API Endpoint (If Using API Directly)

**POST** `/api/v1/hris/auto-sync/start?connection_id={connection_id}`

**Request Body:**
```json
{
  "company_id": "your-company-id",
  "username": "your-username",
  "password": "your-password",
  "api_url": "https://api.successfactors.eu"
}
```

## What Happens After You Provide Credentials

1. ✅ **Entity Discovery** - Fetches all available entities from SuccessFactors
2. ✅ **Mapping Creation** - Creates default field mappings automatically
3. ✅ **Data Sync** - Syncs all org structure data:
   - FOLegalEntity, FODepartment, FODivision, FOBusinessUnit, FOCostCenter
   - Position
   - PerPerson, User
4. ✅ **Visualization** - Data appears in org chart automatically

## Troubleshooting

**Can't find the connection page?**
- Check main navigation menu
- Look for "HRIS", "Connections", or "Integrations"

**Auto Sync button not showing?**
- Make sure you have at least one connection created
- Check if connection status is "active"

**Credentials not working?**
- Verify format: `username@companyID:password` for Basic Auth
- Check API URL matches your SuccessFactors region
- Ensure user has API access permissions
