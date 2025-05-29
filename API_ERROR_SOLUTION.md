# API Error Fix Documentation

## Problem: `throw new ApiError(errorMessage, response.status, errorData)`

This error occurs in the **professional**, **jobs**, and **projects** sections when the frontend cannot communicate with the backend API.

## Root Cause Analysis

The `ApiError` is thrown by the `handleResponse` function in `frontend/lnd-nexus/app/services/api.ts` when:

1. **Backend is not running** (Connection refused)
2. **Proxy configuration is incorrect** (Routes not matching)  
3. **API endpoints return non-200 status codes** (404, 500, etc.)
4. **CORS issues** (Cross-origin request blocked)

## What We Fixed

### ✅ 1. Enhanced Next.js Proxy Configuration

**File**: `frontend/lnd-nexus/next.config.ts`

```typescript
async rewrites() {
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
  
  return [
    // Handle /api/ prefixed requests
    { source: '/api/:path*', destination: `${backendUrl}/:path*` },
    
    // Handle direct FastAPI endpoint requests (without /api/ prefix)
    { source: '/jobs/:path*', destination: `${backendUrl}/jobs/:path*` },
    { source: '/projects/:path*', destination: `${backendUrl}/projects/:path*` },
    { source: '/candidates/:path*', destination: `${backendUrl}/candidates/:path*` },
    { source: '/recommendations/:path*', destination: `${backendUrl}/recommendations/:path*` },
    // ... more endpoints
  ];
}
```

**Why This Fixes It**: 
- Routes API calls from frontend (port 3000) to backend (port 8000)
- Eliminates CORS issues by serving everything from same origin
- Supports both `/api/` prefixed and direct endpoint calls

### ✅ 2. Environment Variable Support

**File**: `frontend/lnd-nexus/next.config.ts`

```typescript
env: {
  BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
}
```

**Why This Fixes It**: 
- Allows dynamic backend URL configuration
- Supports different environments (dev, staging, production)

### ✅ 3. Enhanced CORS Headers

**File**: `frontend/lnd-nexus/next.config.ts`

```typescript
async headers() {
  return [
    {
      source: '/(.*)',
      headers: [
        { key: 'Access-Control-Allow-Origin', value: '*' },
        { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
        { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
      ],
    },
  ];
}
```

### ✅ 4. Middleware Proxy (Alternative)

**File**: `frontend/lnd-nexus/middleware.ts`

- Advanced request interception
- Custom header handling  
- OPTIONS request support
- Runtime proxy configuration

### ✅ 5. Multiple Startup Methods

Created several startup methods:
- `start_unified_simple.bat` - Basic startup
- `run_proxy_method.bat` - Advanced proxy selection
- `quick_fix_api.bat` - Diagnostic and fix script

## How to Test the Fix

### Method 1: Quick Fix (Recommended)

```bash
quick_fix_api.bat
```

This will:
1. Check if services are running
2. Start them if needed
3. Open test URLs in browser
4. Provide diagnostic information

### Method 2: Manual Testing

1. **Start Backend**:
   ```bash
   python run_cors_backend.py
   ```

2. **Start Frontend**:
   ```bash
   cd frontend/lnd-nexus
   npm run dev
   ```

3. **Test Endpoints**:

   **Via Frontend (Proxy)**: http://localhost:3000
   - http://localhost:3000/candidates/public
   - http://localhost:3000/jobs/public
   - http://localhost:3000/projects/public
   - http://localhost:3000/health

   **Via Backend (Direct)**: http://localhost:8000
   - http://localhost:8000/candidates/public
   - http://localhost:8000/jobs/public
   - http://localhost:8000/projects/public
   - http://localhost:8000/health

## Expected Results

### ✅ Working Correctly

- **Frontend URLs** return data via proxy
- **Backend URLs** return data directly
- **No CORS errors** in browser console
- **No ApiError messages** in application

### ❌ Still Having Issues

If you still see `ApiError`, check:

1. **Browser Console**: Look for specific error messages
2. **Network Tab**: Check if requests are reaching the backend
3. **Backend Logs**: Verify endpoints are being called
4. **Port Status**: Ensure both ports 3000 and 8000 are active

## Troubleshooting Commands

```bash
# Check if ports are in use
netstat -an | findstr ":3000"
netstat -an | findstr ":8000"

# Test backend directly
curl http://localhost:8000/health
curl http://localhost:8000/candidates/public

# Test frontend proxy
curl http://localhost:3000/health
curl http://localhost:3000/candidates/public
```

## Architecture Overview

```
Frontend (Port 3000)     Backend (Port 8000)
       ↓                        ↑
[Next.js App] ←--proxy--> [FastAPI Server]
       ↓                        ↑
[API Calls] ←-----------> [Database + ML]
```

**Single Port Access**: Everything accessible from http://localhost:3000
**Proxy Routing**: Automatic backend calls via Next.js rewrites
**No CORS Issues**: Same-origin requests eliminate cross-origin problems

## File Structure

```
project/
├── frontend/lnd-nexus/
│   ├── next.config.ts          # ✅ Updated proxy config
│   ├── middleware.ts           # ✅ New proxy middleware  
│   └── app/services/api.ts     # ✅ Fixed API base URL
├── run_cors_backend.py         # ✅ Backend with CORS
├── start_unified_simple.bat    # ✅ Simple startup
├── run_proxy_method.bat        # ✅ Advanced startup
└── quick_fix_api.bat          # ✅ Diagnostic script
```

## Summary

The `ApiError` issues in professional, jobs, and projects sections have been resolved by:

1. **Proper proxy configuration** routing frontend calls to backend
2. **Environment variable support** for flexible deployment
3. **Enhanced CORS handling** eliminating cross-origin issues
4. **Multiple startup methods** for different scenarios
5. **Comprehensive testing tools** for validation

**Result**: Single port access (http://localhost:3000) with seamless API integration! 🎉 