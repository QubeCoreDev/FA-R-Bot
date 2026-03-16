import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

const backendTarget = process.env.BACKEND_URL ?? "http://127.0.0.1:8002";

export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 5174,
    proxy: {
      "/facr": {
        target: backendTarget,
        changeOrigin: true,
      },
    },
    allowedHosts: [".ngrok.io", ".trycloudflare.com"],
  },
});
