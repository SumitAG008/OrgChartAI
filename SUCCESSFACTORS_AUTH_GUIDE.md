# SuccessFactors Authentication - Complete Guide

## 🔐 How SuccessFactors Authentication Works

### **Why Three Separate Fields?**

SuccessFactors requires credentials in a specific format: `username@companyID:password`

We keep them as **three separate fields** so you can:
- ✅ Easily update individual values
- ✅ See what each part represents
- ✅ Avoid confusion about the format

---

## 📝 Step-by-Step: What Goes Where

### **Field 1: Company ID**
**What to enter:** Your SuccessFactors Company ID

**Example:** `SFHUB003674`

**Where to find it:**
1. Log in to SuccessFactors Admin Center
2. Go to **Company Settings** → **Company Information**
3. Look for **Company ID** field

**In the format:** This goes **after the @ symbol**

---

### **Field 2: API Username**
**What to enter:** Your SuccessFactors API user account username

**Example:** `sfadmin`

**Where to find it:**
1. Log in to SuccessFactors Admin Center
2. Go to **Manage Users**
3. Find your API user account
4. Copy the **Username** field

**In the format:** This goes **at the beginning** (before @)

---

### **Field 3: API Password**
**What to enter:** The password for your API user account

**Example:** `MySecurePassword123`

**Where to find it:**
- This is the password you set when creating the API user
- If you forgot it, reset it in SuccessFactors Admin Center

**In the format:** This goes **at the end** (after the colon)

---

## 🔄 How It's Combined

### **Step 1: You Fill In Three Fields**

```
Company ID:  SFHUB003674
Username:    sfadmin
Password:    MySecurePassword123
```

### **Step 2: System Combines Them**

The system automatically creates this string:

```
sfadmin@SFHUB003674:MySecurePassword123
```

**Format:** `[Username]@[CompanyID]:[Password]`

**Important:** 
- No spaces
- @ symbol between username and company ID
- Colon (:) between company ID and password

### **Step 3: System Base64 Encodes It**

The combined string is encoded using Base64:

```
Input:  sfadmin@SFHUB003674:MySecurePassword123
Output: c2ZhZG1pbkBTSEhVQjAwMzY3NDpNeVNlY3VyZVBhc3N3b3JkMTIz
```

### **Step 4: Sent to SuccessFactors**

The encoded string is sent in the HTTP header:

```
Authorization: Basic c2ZhZG1pbkBTSEhVQjAwMzY3NDpNeVNlY3VyZVBhc3N3b3JkMTIz
```

---

## 💡 Visual Example

```
┌─────────────────────────────────────────────────────────┐
│  You Enter:                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Company ID  │  │  Username   │  │  Password   │    │
│  │ SFHUB003674 │  │   sfadmin   │  │  MyPass123 │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  System Combines:                                       │
│  sfadmin@SFHUB003674:MyPass123                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  System Base64 Encodes:                                 │
│  c2ZhZG1pbkBTSEhVQjAwMzY3NDpNeVBhc3MxMjM=               │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Sent to SuccessFactors:                                │
│  Authorization: Basic c2ZhZG1pbkBTSEhVQjAwMzY3NDp...   │
└─────────────────────────────────────────────────────────┘
```

---

## 🧪 Test It Yourself

### **Using Python:**

```python
import base64

# Your values
username = "sfadmin"
company_id = "SFHUB003674"
password = "MySecurePassword123"

# Step 1: Combine
combined = f"{username}@{company_id}:{password}"
print(f"Combined: {combined}")
# Output: sfadmin@SFHUB003674:MySecurePassword123

# Step 2: Base64 encode
encoded = base64.b64encode(combined.encode()).decode()
print(f"Encoded: {encoded}")
# Output: c2ZhZG1pbkBTSEhVQjAwMzY3NDpNeVNlY3VyZVBhc3N3b3JkMTIz
```

### **Using Online Tool:**

1. Go to: https://www.base64encode.org/
2. Enter: `sfadmin@SFHUB003674:MySecurePassword123`
3. Click "Encode"
4. Copy the result

---

## ✅ Quick Reference

| Field | Example Value | Position in Format |
|-------|--------------|-------------------|
| **Username** | `sfadmin` | **Before** @ |
| **Company ID** | `SFHUB003674` | **After** @, **Before** : |
| **Password** | `MyPass123` | **After** : |

**Final Format:** `username@companyID:password`

**Example:** `sfadmin@SFHUB003674:MyPass123`

---

## 🎯 Why This Format?

SuccessFactors uses this format because:
1. **Company ID** identifies which SuccessFactors instance
2. **Username** identifies which user account
3. **Password** authenticates the user
4. The `@` and `:` symbols separate the parts clearly

This is the **standard format** for SuccessFactors OData API Basic Authentication.

---

## ❓ Common Questions

**Q: Why not just one field?**  
A: Three fields make it easier to update individual values and understand what each part represents.

**Q: Do I need to add @ and : myself?**  
A: No! The system adds them automatically when combining the fields.

**Q: Do I need to Base64 encode it?**  
A: No! The system does this automatically when you test the connection.

**Q: What if I get "Authentication failed"?**  
A: Check:
- Company ID is correct (no spaces, exact case)
- Username is correct
- Password is correct
- API URL matches your region

---

**That's it! The UI now shows all of this visually, so you can see exactly how it works.** 🎉
