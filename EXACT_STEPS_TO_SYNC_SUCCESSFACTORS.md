# EXACT STEPS: How to Sync SuccessFactors - ONE TIME SETUP

## 🎯 WHERE TO GO IN THE UI

### Step 1: Navigate to HRIS Connections Page

**Option A: From Left Sidebar**
1. Look at the **LEFT SIDEBAR** of the application
2. Find **"HRIS"** or **"Connections"** menu item
3. Click on it

**Option B: Direct URL**
- Go to: `http://localhost:3000` and look for HRIS/Connections in navigation

### Step 2: Add SuccessFactors Connection

**You will see:**
```
┌─────────────────────────────────────────────┐
│  HRIS Connections                            │
│  Connect and sync data from your HRIS system │
│                                               │
│  [+ Add Connection]  ← CLICK THIS BUTTON     │
└─────────────────────────────────────────────┘
```

**Click the GREEN "Add Connection" button**

### Step 3: Fill in SuccessFactors Details

**A modal will open. Fill in:**

```
┌─────────────────────────────────────────────┐
│  Add HRIS Connection                         │
│                                               │
│  Connection Name: [My SuccessFactors]        │
│  System: [SAP SuccessFactors ▼]             │
│  Authentication: [Basic Auth ▼]               │
│                                               │
│  Company ID: [________________]  ← REQUIRED   │
│  Username:   [________________]  ← REQUIRED   │
│  Password:   [________________]  ← REQUIRED   │
│  API URL:    [https://api.successfactors.eu] │
│                                               │
│  [Test Connection]  [Cancel]  [Save]         │
└─────────────────────────────────────────────┘
```

**Fill in:**
- **Company ID**: Your SuccessFactors company ID
- **Username**: Your SuccessFactors username
- **Password**: Your SuccessFactors password
- **API URL**: Usually `https://api.successfactors.eu` (or your region)

### Step 4: Test Connection

1. Click **"Test Connection"** button
2. Wait for success message: ✅ "Connection successful"
3. Click **"Save"** button

### Step 5: Auto Sync (ONE CLICK!)

**After saving, you'll see your connection card:**

```
┌─────────────────────────────────────────────┐
│  🔵 My SuccessFactors Connection             │
│     SuccessFactors                          │
│     Last sync: Never                        │
│                                              │
│     [⚡ Auto Sync] [🔄] [🗑️]                 │
│     ↑                                        │
│     CLICK THIS PURPLE BUTTON!                │
└─────────────────────────────────────────────┘
```

**Click the PURPLE "Auto Sync" button (⚡ icon)**

### Step 6: Enter Credentials Again (One Time)

**Modal opens - enter credentials:**

```
┌─────────────────────────────────────────────┐
│  ⚡ One-Click Auto Sync                      │
│                                               │
│  Company ID: [________________]               │
│  Username:   [________________]               │
│  Password:   [________________]               │
│  API URL:    [https://api.successfactors.eu] │
│                                               │
│  [Cancel]  [Start Auto Sync]                 │
└─────────────────────────────────────────────┘
```

**Click "Start Auto Sync"**

### Step 7: Done! ✅

**The backend will automatically:**
1. ✅ Discover all SuccessFactors entities
2. ✅ Create field mappings
3. ✅ Sync all org structure data
4. ✅ Show data in org chart

**You'll see progress updates:**
- "Discovering entities..."
- "Creating mappings..."
- "Syncing data..."
- "Completed! Processed X records"

---

## 📍 VISUAL LOCATION IN UI

```
┌─────────────────────────────────────────────────────────┐
│  [Browser Bar]                                            │
├─────────────────────────────────────────────────────────┤
│  [M] OrgChart with AI Intelligence  [Add tag] [Template] │
│                                    [⚡ meldra AI] [👤]    │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ LEFT     │         CENTER CANVAS                       │
│ SIDEBAR  │         (Org Chart View)                     │
│          │                                              │
│ • Org    │                                              │
│   chart  │                                              │
│ • People │                                              │
│   & pos  │                                              │
│ • Func   │                                              │
│   chart  │                                              │
│ • Fore-  │                                              │
│   cast   │                                              │
│ • Change │                                              │
│   plan   │                                              │
│          │                                              │
│ 🔍 FIND  │                                              │
│ "HRIS"   │                                              │
│ HERE!    │                                              │
│          │                                              │
│ Click    │                                              │
│ "HRIS"   │                                              │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

**When you click "HRIS" in left sidebar:**
- The center canvas changes to show "HRIS Connections" page
- You see the "Add Connection" button
- Follow steps above

---

## 🚀 QUICK REFERENCE

**Navigation Path:**
```
Left Sidebar → "HRIS" → "Add Connection" → Fill Form → Test → Save → "Auto Sync" → Enter Credentials → Done!
```

**Total Steps:** 7 steps (one-time setup)

**After First Sync:**
- Data appears in org chart automatically
- Future syncs: Just click "Auto Sync" button again

---

## ❓ TROUBLESHOOTING

**Can't find "HRIS" in sidebar?**
- Check if it's named "Connections" or "Integrations"
- Look for a database/plug icon

**"Add Connection" button not showing?**
- Make sure you're on the HRIS Connections page
- Check browser console for errors

**Connection test fails?**
- Verify credentials format: `username@companyID:password`
- Check API URL matches your SF region
- Ensure user has API permissions

---

## 📝 SUMMARY

**WHERE:** Left Sidebar → "HRIS" → "Add Connection" button

**WHAT:** Fill in Company ID, Username, Password, API URL

**HOW:** Click "Auto Sync" button on connection card

**RESULT:** All SuccessFactors data synced automatically!
