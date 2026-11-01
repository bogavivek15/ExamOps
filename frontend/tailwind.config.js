/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#0B1118',
          sidebar: '#0E151D',
          surface: '#121C26',
          elevated: '#172330',
          border: '#263442',
          text: '#E8EEF5',
          muted: '#9AAABA',
          accent: '#56D6C2',
          'accent-hover': '#45c4b0',
          success: '#57BE93',
          warning: '#E8B66D',
          danger: '#E87979',
          info: '#7CAAE5',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
    },
  },
  plugins: [],
}
