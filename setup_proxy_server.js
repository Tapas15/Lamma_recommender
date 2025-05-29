/**
 * Manual Proxy Server Setup
 * Based on Create React App's http-proxy-middleware approach
 * Reference: https://create-react-app.dev/docs/proxying-api-requests-in-development/
 */

const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

console.log('🚀 Setting up unified proxy server...');
console.log(`Frontend will serve on: http://localhost:${PORT}`);
console.log(`Backend proxy target: ${BACKEND_URL}`);

// Proxy API requests to FastAPI backend
app.use(
  '/api',
  createProxyMiddleware({
    target: BACKEND_URL,
    changeOrigin: true,
    pathRewrite: {
      '^/api': '', // Remove /api prefix when forwarding
    },
    onProxyReq: (proxyReq, req, res) => {
      console.log(`🔄 Proxying: ${req.method} ${req.url} -> ${BACKEND_URL}${req.url}`);
    },
    onError: (err, req, res) => {
      console.error('❌ Proxy error:', err.message);
      res.status(500).json({ error: 'Proxy error', details: err.message });
    },
  })
);

// Proxy docs and health endpoints
app.use(
  ['/docs', '/redoc', '/health', '/openapi.json'],
  createProxyMiddleware({
    target: BACKEND_URL,
    changeOrigin: true,
    onProxyReq: (proxyReq, req, res) => {
      console.log(`📚 Proxying docs: ${req.method} ${req.url} -> ${BACKEND_URL}${req.url}`);
    },
  })
);

// Serve static files from Next.js build (if available)
const nextBuildPath = path.join(__dirname, 'frontend', 'lnd-nexus', '.next');
const nextStaticPath = path.join(__dirname, 'frontend', 'lnd-nexus', 'out');

if (require('fs').existsSync(nextStaticPath)) {
  app.use(express.static(nextStaticPath));
  console.log('✅ Serving static Next.js build');
} else {
  // Fallback: serve a simple landing page
  app.get('*', (req, res) => {
    res.send(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>Job Recommender - Unified Server</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 20px; background: #f0f8ff; border-radius: 8px; }
            .endpoint { margin: 10px 0; }
            a { color: #0066cc; text-decoration: none; }
            a:hover { text-decoration: underline; }
          </style>
        </head>
        <body>
          <div class="container">
            <h1>🚀 Job Recommender - Unified Server</h1>
            <div class="status">
              <h2>✅ Proxy Server Running</h2>
              <p><strong>Frontend Port:</strong> ${PORT}</p>
              <p><strong>Backend Target:</strong> ${BACKEND_URL}</p>
            </div>
            
            <h3>📚 Available Endpoints:</h3>
            <div class="endpoint">🏠 <a href="/">Frontend Application</a></div>
            <div class="endpoint">📖 <a href="/docs">API Documentation</a></div>
            <div class="endpoint">📋 <a href="/redoc">Alternative API Docs</a></div>
            <div class="endpoint">💓 <a href="/health">Health Check</a></div>
            <div class="endpoint">🔧 <a href="/api/">API Endpoints (prefix with /api/)</a></div>
            
            <p><em>All API requests are automatically proxied to the FastAPI backend!</em></p>
          </div>
        </body>
      </html>
    `);
  });
}

// Start the server
app.listen(PORT, () => {
  console.log('');
  console.log('🎉 Unified Proxy Server Started!');
  console.log('='.repeat(50));
  console.log(`🌐 Access your app: http://localhost:${PORT}`);
  console.log(`📚 API Documentation: http://localhost:${PORT}/docs`);
  console.log(`💓 Health Check: http://localhost:${PORT}/health`);
  console.log(`🔧 API Endpoints: http://localhost:${PORT}/api/*`);
  console.log('='.repeat(50));
  console.log('✨ All requests automatically routed!');
  console.log('🔄 API calls proxied to backend transparently');
});

module.exports = app; 