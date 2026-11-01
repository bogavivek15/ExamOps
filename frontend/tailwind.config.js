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
          // Primary Theme Palette
          bg: '#08090A',             // Outskill obsidian canvas
          sidebar: '#0D0E10',        // Outskill dark sidebar
          surface: '#121212',        // Outskill charcoal card surface
          elevated: '#1C1C1C',       // Outskill elevated container surface
          panel: '#141414',          // Outskill intermediate container
          iconbox: '#343535',        // Outskill slate icon box
          border: '#242629',         // Outskill subtle border equivalent
          'border-strong': '#363A3E',// Outskill strong border
          text: '#FFFFFF',           // Outskill pure white primary text
          secondary: '#D1D5DB',      // Outskill gray-300 secondary text
          muted: '#9CA3AF',          // Outskill gray-400 muted text
          accent: '#B8EF43',         // Outskill Electric Lime signature accent
          'accent-hover': '#BEF264', // Outskill lime-300 hover
          'accent-active': '#A6DF30',// Outskill active press
          cream: '#FCF7F3',          // Outskill warm cream
          success: '#B8EF43',        // Harmonized success using Outskill Lime
          warning: '#E8B66D',        // Harmonized warning amber
          danger: '#FF6B6B',         // High-contrast coral red
          info: '#7CAAE5',           // Informational slate blue

          // AGENTS.md Baseline Enterprise Specification Tokens
          spec_bg: '#0B1118',
          spec_sidebar: '#0E151D',
          spec_surface: '#121C26',
          spec_elevated: '#172330',
          spec_border: '#263442',
          spec_text: '#E8EEF5',
          spec_secondary: '#9AAABA',
          spec_accent: '#56D6C2',
          spec_success: '#57BE93',
          spec_warning: '#E8B66D',
          spec_danger: '#E87979',
          spec_info: '#7CAAE5',
        },
      },
      fontFamily: {
        sans: ['Figtree', 'Fira Sans', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
      },
      borderRadius: {
        xs: '2px',
        sm: '4px',
        md: '6px',
        lg: '8px',
      },
    },
  },
  plugins: [],
}
