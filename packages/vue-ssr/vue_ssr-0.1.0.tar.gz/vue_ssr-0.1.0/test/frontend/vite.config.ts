import { defineConfig } from "vite";
import { resolve } from "path";
import vue from "@vitejs/plugin-vue";
import { ssrPlugin } from "vue-ssr-service/vite";
import { analyzer } from "vite-bundle-analyzer";

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue(), ssrPlugin()],
  base: "/static/",
  build: {
    sourcemap: true,
    manifest: "manifest.json",
    rollupOptions: {
      input: {
        basic: resolve("./userGreeting.ts"),
      },
    },
  },
  environments: {
    client: {
      build: {
        outDir: resolve("dist", "client"),
      },
    },
    ssr: {
      build: {
        outDir: resolve("dist", "server"),
        ssr: true,
      },
    },
  },
});
