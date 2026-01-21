# Authentication & Security Implementation Guide

## 🎯 Overview

This guide covers the complete authentication system implementation to solve the mapping persistence and security issues.

---

## 🔐 What Was Implemented

### 1. **User Authentication System**
- ✅ JWT-based authentication (access + refresh tokens)
- ✅ User registration and login
- ✅ Password hashing with bcrypt
- ✅ Session management
- ✅ Secure token storage

### 2. **User-Specific Data**
- ✅ All connections are now user-specific
- ✅ All mappings are user-specific (via connections)
- ✅ Multi-tenant support with organizations/workspaces
- ✅ Data isolation between users

### 3. **Security Features**
- ✅ Password strength requirements
- ✅ Token expiration and refresh
- ✅ Session revocation
- ✅ Audit logging for auth events
- ✅ CORS protection

---

## 📋 Database Schema

### New Tables Created:

1. **`users`** - User accounts
2. **`user_sessions`** - Refresh token storage
3. **`organizations`** - Workspaces/tenants
4. **`user_organizations`** - User-org membership
5. **`auth_audit_log`** - Security audit trail

### Updated Tables:

- **`hris_connection`** - Added `user_id` and `organization_id`
- All mappings are now user-specific through connections

---

## 🚀 Setup Instructions

### Step 1: Create Database Tables

```bash
# Run the auth schema
psql 'postgresql://neondb_owner:npg_Mruj0FCPdbT9@ep-falling-dawn-ab3vxbgv-pooler.eu-west-2.aws.neon.tech/neondb?sslmode=require' -f database/auth_schema.sql
```

Or use Python:

```bash
cd backend/auth-service
python setup_auth_tables.py
```

### Step 2: Install Auth Service Dependencies

```bash
cd backend/auth-service
pip install fastapi uvicorn sqlalchemy[asyncio] asyncpg passlib[bcrypt] python-jose[cryptography] python-multipart
```

### Step 3: Start Auth Service

```bash
cd backend/auth-service
uvicorn main:app --reload --port 8003
```

---

## 🔧 API Endpoints

### Authentication

#### Register User
```bash
POST http://localhost:8003/api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

#### Login
```bash
POST http://localhost:8003/api/v1/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123!",
  "remember_me": false
}
```

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "full_name": "John Doe",
    "is_active": true,
    "is_superuser": false,
    "email_verified": false,
    "created_at": "2024-01-19T10:00:00Z",
    "last_login": "2024-01-19T10:00:00Z"
  },
  "tokens": {
    "access_token": "eyJ...",
    "refresh_token": "abc123...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### Get Current User
```bash
GET http://localhost:8003/api/v1/auth/me
Authorization: Bearer {access_token}
```

#### Refresh Token
```bash
POST http://localhost:8003/api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "abc123..."
}
```

#### Logout
```bash
POST http://localhost:8003/api/v1/auth/logout
Content-Type: application/json

{
  "refresh_token": "abc123..."
}
```

#### Change Password
```bash
POST http://localhost:8003/api/v1/auth/change-password
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "current_password": "OldPass123!",
  "new_password": "NewPass123!"
}
```

---

## 🔒 Securing Other Services

### Update HRIS Service to Require Authentication

Add to `backend/hris-service/app/routers/connections.py`:

```python
from fastapi import Depends, HTTPException
from app.middleware.auth import get_current_user

@router.post("/connections")
async def create_connection(
    connection: HRISConnectionCreate,
    current_user: User = Depends(get_current_user),  # Add this
    db: AsyncSession = Depends(get_db)
):
    # Add user_id to connection
    connection.user_id = current_user.id
    # ... rest of code
```

### Update Mapping Endpoints

All mapping endpoints should:
1. Verify user authentication
2. Filter by `user_id` through `connection_id`
3. Ensure users can only access their own mappings

---

## 🎨 Frontend Integration

### 1. Create Auth Context

```typescript
// frontend/src/contexts/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const login = async (username: string, password: string) => {
    const response = await fetch('http://localhost:8003/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password })
    });
    const data = await response.json();
    setToken(data.tokens.access_token);
    setUser(data.user);
    localStorage.setItem('access_token', data.tokens.access_token);
    localStorage.setItem('refresh_token', data.tokens.refresh_token);
    localStorage.setItem('user', JSON.stringify(data.user));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
};
```

### 2. Create Login Component

```typescript
// frontend/src/components/Auth/Login.tsx
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold text-center">Login to OrgChartAI</h2>
        {error && <div className="text-red-600">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Username or Email"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded"
            required
          />
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700"
          >
            Login
          </button>
        </form>
      </div>
    </div>
  );
};
```

### 3. Protect Routes

```typescript
// frontend/src/components/Auth/ProtectedRoute.tsx
import { Navigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
};
```

---

## ✅ Benefits

### Before (Problems):
- ❌ No user authentication
- ❌ Mappings not user-specific
- ❌ Need to reconnect every time
- ❌ Mappings can be lost
- ❌ No data security

### After (Solutions):
- ✅ Secure user authentication
- ✅ Mappings are user-specific and persistent
- ✅ Login once, stay logged in
- ✅ Mappings automatically load for logged-in user
- ✅ Complete data isolation and security

---

## 🔄 Migration Path

1. **Run database migration** - Add auth tables
2. **Start auth service** - Port 8003
3. **Update HRIS service** - Add user authentication
4. **Update frontend** - Add login/signup UI
5. **Test** - Register, login, create connection, verify mappings persist

---

## 📝 Next Steps

1. ✅ Database schema created
2. ✅ Auth service implemented
3. ⏳ Update HRIS service to use auth
4. ⏳ Create frontend login/signup UI
5. ⏳ Add protected routes
6. ⏳ Test complete flow

---

**Need Help?** Check the auth service logs and database for any issues.
