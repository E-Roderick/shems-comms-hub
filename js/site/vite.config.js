import solid from "solid-start/vite";
import { defineConfig } from "vite";

const HOST = process.env.WEB_SITE_ADDR || "0.0.0.0";
const PORT = process.env.WEB_SITE_PORT || 3000;

export default defineConfig({
  plugins: [
    solid({ ssr: false, }),
  ],
  server: {
	  host: HOST,
	  port: PORT
  },
});
