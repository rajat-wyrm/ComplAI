const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  compress: true,
  poweredByHeader: false,
  experimental: {
    optimizeCss: true,
    scrollRestoration: true
  }
};

module.exports = nextConfig;
