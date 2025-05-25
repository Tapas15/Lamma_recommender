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
};

export default nextConfig;
