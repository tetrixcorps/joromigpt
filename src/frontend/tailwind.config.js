/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
    "./components/**/*.{js,jsx,ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        border: "var(--border-color)",
        input: "var(--border-color)",
        ring: "var(--secondary-color)",
        background: "var(--light-gray)",
        foreground: "var(--text-color)",
        primary: {
          DEFAULT: "var(--primary-color)",
          foreground: "white",
        },
        secondary: {
          DEFAULT: "var(--secondary-color)",
          foreground: "white",
        },
        destructive: {
          DEFAULT: "var(--error-color)",
          foreground: "white",
        },
        muted: {
          DEFAULT: "#f5f5f5",
          foreground: "#737373",
        },
        accent: {
          DEFAULT: "var(--accent-color)",
          foreground: "white",
        },
      },
      borderRadius: {
        lg: "var(--border-radius)",
        md: "calc(var(--border-radius) - 2px)",
        sm: "calc(var(--border-radius) - 4px)",
      },
    },
  },
  plugins: [],
}