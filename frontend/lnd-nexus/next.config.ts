/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {
    serverActions: {
      allowedOrigins: ['localhost:3000', 'localhost:3005']
    },
  },
  images: {
    domains: ["images.unsplash.com", "logo.clearbit.com"],
  },
  env: {
    NEXT_PUBLIC_LIBRETRANSLATE_URL: process.env.NEXT_PUBLIC_LIBRETRANSLATE_URL || 'http://localhost:5000',
    BACKEND_URL: process.env.BACKEND_URL || 'http://localhost:8000',
  },
  
  // Enhanced proxy configuration based on Create React App pattern
  // Reference: https://create-react-app.dev/docs/proxying-api-requests-in-development/
  async rewrites() {
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    return [
      // Handle /api/ prefixed requests
      {
        source: '/api/:path*',
        destination: `${backendUrl}/:path*`,
      },
      
      // Handle direct FastAPI endpoint requests (without /api/ prefix)
      {
        source: '/jobs/:path*',
        destination: `${backendUrl}/jobs/:path*`,
      },
      {
        source: '/projects/:path*',
        destination: `${backendUrl}/projects/:path*`,
      },
      {
        source: '/candidates/:path*',
        destination: `${backendUrl}/candidates/:path*`,
      },
      {
        source: '/recommendations/:path*',
        destination: `${backendUrl}/recommendations/:path*`,
      },
      {
        source: '/skill-gap/:path*',
        destination: `${backendUrl}/skill-gap/:path*`,
      },
      {
        source: '/career-paths/:path*',
        destination: `${backendUrl}/career-paths/:path*`,
      },
      {
        source: '/analytics/:path*',
        destination: `${backendUrl}/analytics/:path*`,
      },
      {
        source: '/ml/:path*',
        destination: `${backendUrl}/ml/:path*`,
      },
      {
        source: '/token',
        destination: `${backendUrl}/token`,
      },
      {
        source: '/register/:path*',
        destination: `${backendUrl}/register/:path*`,
      },
      {
        source: '/profile/:path*',
        destination: `${backendUrl}/profile/:path*`,
      },
      
      // FastAPI documentation and utility endpoints
      {
        source: '/docs',
        destination: `${backendUrl}/docs`,
      },
      {
        source: '/redoc', 
        destination: `${backendUrl}/redoc`,
      },
      {
        source: '/openapi.json',
        destination: `${backendUrl}/openapi.json`,
      },
      {
        source: '/health',
        destination: `${backendUrl}/health`,
      },
    ];
  },
  
  // CORS configuration for development
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
  },
};

export default nextConfig;
