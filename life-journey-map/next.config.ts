import type { NextConfig } from "next";

const isGitHubPages = process.env.GITHUB_ACTIONS === "true";
const repoName = "estimate-backend-calc";

const nextConfig: NextConfig = {
  output: isGitHubPages ? "export" : "standalone",
  basePath: isGitHubPages ? `/${repoName}` : undefined,
  assetPrefix: isGitHubPages ? `/${repoName}/` : undefined,
  images: {
    unoptimized: true,
  },
  trailingSlash: isGitHubPages,
  turbopack: {
    root: process.cwd(),
  },
};

export default nextConfig;
