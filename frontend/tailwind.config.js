/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'premier': {
          'purple': '#38003c',
          'cyan': '#00ff85',
          'magenta': '#e90052',
          'green': '#00ff85',
        },
      },
    },
  },
  plugins: [],
}
