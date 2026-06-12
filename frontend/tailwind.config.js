/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'heat-low': '#4ade80',
        'heat-moderate': '#fbbf24',
        'heat-high': '#fb923c',
        'heat-critical': '#ef4444',
        primary: '#1e40af',
        secondary: '#0891b2',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
