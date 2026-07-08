import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow the API route to spawn Python subprocess for long-running tasks
  serverExternalPackages: [],

  // Increase body size limit for job descriptions
  experimental: {
    serverActions: {
      bodySizeLimit: "2mb",
    },
  },
};

export default nextConfig;
