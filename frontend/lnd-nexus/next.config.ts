/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  experimental: {
    serverActions: true,
  },
  images: {
    domains: ["images.unsplash.com", "logo.clearbit.com"],
  },
  env: {
    NEXT_PUBLIC_LIBRETRANSLATE_URL: process.env.NEXT_PUBLIC_LIBRETRANSLATE_URL || 'http://localhost:5000',
  },
};

export default nextConfig;
