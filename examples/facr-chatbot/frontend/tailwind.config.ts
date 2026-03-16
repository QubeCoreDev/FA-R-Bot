import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          "Inter",
          "system-ui",
          "-apple-system",
          "BlinkMacSystemFont",
          "Segoe UI",
          "sans-serif",
        ],
        display: [
          "Barlow Condensed",
          "Inter",
          "system-ui",
          "sans-serif",
        ],
      },
      colors: {
        facr: {
          blue: "#003087",
          red: "#ED1C24",
          gold: "#c9a84c",
          "blue-light": "#1a4a9e",
          "red-light": "#ff3b42",
          "blue-dark": "#001f5c",
        },
      },
    },
  },
  plugins: [],
};

export default config;
