import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Vite config for the Agora mini SPA that builds into ui/static/spa
export default defineConfig({
  plugins: [react()],
  build: {
    // Output goes under ui/static/spa so Streamlit can serve it as static assets.
    outDir: "../static/spa",
    // Keep any existing static assets under ui/static (CSS, images, etc.).
    emptyOutDir: false
  }
});

