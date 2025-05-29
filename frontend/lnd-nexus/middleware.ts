import { NextRequest, NextResponse } from 'next/server';

/**
 * Enhanced proxy middleware for API requests
 * Based on Create React App proxy concept but optimized for Next.js
 * Reference: https://create-react-app.dev/docs/proxying-api-requests-in-development/
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Proxy API requests to FastAPI backend
  if (pathname.startsWith('/api/') || 
      pathname.startsWith('/docs') || 
      pathname.startsWith('/redoc') || 
      pathname.startsWith('/health') ||
      pathname.startsWith('/openapi.json')) {
    
    // Create the backend URL
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const url = new URL(pathname + request.nextUrl.search, backendUrl);
    
    // Clone the request headers
    const requestHeaders = new Headers(request.headers);
    
    // Add CORS headers for development
    if (process.env.NODE_ENV === 'development') {
      requestHeaders.set('Access-Control-Allow-Origin', '*');
      requestHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      requestHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    }
    
    // Handle preflight OPTIONS requests
    if (request.method === 'OPTIONS') {
      return new NextResponse(null, { 
        status: 200,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        }
      });
    }
    
    // Create the proxied request
    const modifiedRequest = new Request(url, {
      method: request.method,
      headers: requestHeaders,
      body: request.body,
    });
    
    // Forward to backend
    return fetch(modifiedRequest);
  }
  
  // Continue to Next.js for all other requests
  return NextResponse.next();
}

export const config = {
  matcher: [
    '/api/:path*',
    '/docs',
    '/redoc', 
    '/health',
    '/openapi.json'
  ]
}; 