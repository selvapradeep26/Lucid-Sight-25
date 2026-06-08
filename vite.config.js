import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite dev server proxies API calls to the Flask backend running on :5000
const backendUrl = "http://127.0.0.1:5000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/start_detection": backendUrl,
      "/stop_detection": backendUrl,
      "/api": backendUrl,
    },
  },
});
