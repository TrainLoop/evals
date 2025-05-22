/** @type {import('next').NextConfig} */
const nextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  output: 'standalone',
  serverExternalPackages: [
    '@duckdb/node-api',               // high-level JS
    '@duckdb/node-bindings',          // platform switcher
    '@duckdb/node-bindings-darwin-arm64' // apple silicon
  ]
}

export default nextConfig
