/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        bg: '#0B0F14',
        surface: '#0F1720',
        primary: '#7C5CFF',
        accent: '#22D3EE',
        danger: '#FF6B6B',
        text: '#E6EEF3'
      },
      animation: {
        'pulse-danger': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'draw-line': 'draw 2s ease-in-out forwards'
      },
      keyframes: {
        draw: {
          'from': { 'stroke-dashoffset': '100%' },
          'to': { 'stroke-dashoffset': '0%' }
        }
      }
    },
  },
  plugins: [],
}