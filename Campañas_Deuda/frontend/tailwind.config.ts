import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#1E2761',
          hover: '#162054',
        },
        secondary: {
          DEFAULT: '#3B5BA9',
        },
        accent: {
          DEFAULT: '#D8A23A',
          hover: '#C49130',
        },
        background: '#F4F7FC',
        surface: '#FFFFFF',
        'card-border': '#E5ECFA',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'sans-serif'],
      },
      screens: {
        xs: '375px',
      },
    },
  },
  plugins: [],
}

export default config
