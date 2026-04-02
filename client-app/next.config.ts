import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  images: {
    domains: ["avatar.iran.liara.run", "res.cloudinary.com"],
  },
  async rewrites() {
    return [
      { source: "/predict", destination: "http://127.0.0.1:8000/predict" },
      { source: "/explain", destination: "http://127.0.0.1:8000/explain" },
      {
        source: "/predict/batch",
        destination: "http://127.0.0.1:8000/predict/batch",
      },
      {
        source: "/predict/upload",
        destination: "http://127.0.0.1:8000/predict/upload",
      },
      {
        source: "/model-info",
        destination: "http://127.0.0.1:8000/model-info",
      },
      {
        source: "/model-info/ui",
        destination: "http://127.0.0.1:8000/model-info/ui",
      },
    ];
  },
};

export default nextConfig;
