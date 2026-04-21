/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./layouts/**/*.vue",
    "./pages/**/*.vue",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue",
  ],
  theme: {
    extend: {
      colors: {
        'frc-red': '#830D13',
        'frc-red-light': '#EC1D25',
        'frc-red-dark': '#830F12',
        'frc-red-mid': '#A31317',
        'frc-red-ultra-dark': '#4E0A0D',

        //blue
        'frc-blue': '#014172',
        'frc-blue-light': '#0066B3',
        'frc-blue-dark': '#00355D',
        'frc-blue-mid': '#004C86',
        'frc-blue-ultra-dark': '#002A4D',
      }
      
    },
  },
  plugins: [],
}

