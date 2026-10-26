/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        paper: "#f4efe6",
        sand: "#e7dcc8",
        card: "#fbf7f0",
        ink: "#2c241c",
        walnut: "#5c4033",
        bark: "#3f2e22",
        brass: "#a68456",
        clay: "#c4622d",
        moss: "#3e6848",
      },
      fontFamily: {
        serif: ["Fraunces", "Georgia", "serif"],
        sans: ["Source Sans 3", "ui-sans-serif", "system-ui", "sans-serif"],
      },
      boxShadow: {
        desk: "0 18px 50px rgba(62, 42, 24, 0.08)",
      },
    },
  },
  plugins: [],
}
