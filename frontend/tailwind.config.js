/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        neon: {
          green: '#00ff41',
          dark: '#003b00',
          light: '#7cff7c',
        },
        cyber: {
          black: '#0a0a0a',
          dark: '#0d1117',
          gray: '#161b22',
          light: '#21262d',
          border: '#30363d',
        },
      },
      fontFamily: {
        mono: ['Courier New', 'Consolas', 'monospace'],
        cyber: ['Orbitron', 'sans-serif'],
      },
      boxShadow: {
        'neon': '0 0 10px #00ff41, 0 0 20px #00ff41, 0 0 40px #00ff41',
        'neon-sm': '0 0 5px #00ff41, 0 0 10px #00ff41',
        'glass': '0 8px 32px 0 rgba(0, 255, 65, 0.1)',
      },
      animation: {
        'glow': 'glow 2s ease-in-out infinite alternate',
        'pulse-neon': 'pulse-neon 2s infinite',
        'float': 'float 6s ease-in-out infinite',
        'scan': 'scan 3s linear infinite',
        'matrix-fall': 'matrix-fall 10s linear infinite',
        'typing': 'typing 3.5s steps(40, end), blink-caret .75s step-end infinite',
      },
      keyframes: {
        glow: {
          '0%': { textShadow: '0 0 10px #00ff41, 0 0 20px #00ff41' },
          '100%': { textShadow: '0 0 20px #00ff41, 0 0 40px #00ff41, 0 0 60px #00ff41' },
        },
        'pulse-neon': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-20px)' },
        },
        scan: {
          '0%': { top: '0%' },
          '100%': { top: '100%' },
        },
      },
    },
  },
  plugins: [],
}
