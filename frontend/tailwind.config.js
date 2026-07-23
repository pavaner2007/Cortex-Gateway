const config = {
    content: [
        './index.html',
        './src/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
        extend: {
            colors: {
                // Deep space dark palette
                cortex: {
                    950: '#070b14',
                    900: '#0d1220',
                    800: '#111827',
                    700: '#162032',
                    600: '#1e2d42',
                    500: '#243550',
                },
                // Primary brand – indigo/violet
                primary: {
                    50: '#eef2ff',
                    100: '#e0e7ff',
                    200: '#c7d2fe',
                    300: '#a5b4fc',
                    400: '#818cf8',
                    500: '#6366f1',
                    600: '#4f46e5',
                    700: '#4338ca',
                    800: '#3730a3',
                    900: '#312e81',
                },
                // Accent colours
                accent: {
                    cyan: '#06b6d4',
                    violet: '#8b5cf6',
                    emerald: '#10b981',
                    amber: '#f59e0b',
                    rose: '#f43f5e',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace'],
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'mesh-gradient': 'radial-gradient(at 40% 20%, hsla(252,100%,74%,0.15) 0px, transparent 50%), ' +
                    'radial-gradient(at 80% 0%, hsla(189,100%,56%,0.10) 0px, transparent 50%), ' +
                    'radial-gradient(at 0% 50%, hsla(355,100%,93%,0.05) 0px, transparent 50%)',
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'fade-in': 'fadeIn 0.4s ease-out',
                'slide-up': 'slideUp 0.4s ease-out',
                'slide-in-left': 'slideInLeft 0.3s ease-out',
                'spin-slow': 'spin 3s linear infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { opacity: '0', transform: 'translateY(16px)' },
                    '100%': { opacity: '1', transform: 'translateY(0)' },
                },
                slideInLeft: {
                    '0%': { opacity: '0', transform: 'translateX(-16px)' },
                    '100%': { opacity: '1', transform: 'translateX(0)' },
                },
                glow: {
                    '0%': { boxShadow: '0 0 5px rgba(99,102,241,0.4)' },
                    '100%': { boxShadow: '0 0 20px rgba(99,102,241,0.8), 0 0 40px rgba(99,102,241,0.2)' },
                },
            },
            boxShadow: {
                'glass': '0 4px 30px rgba(0, 0, 0, 0.3)',
                'card': '0 8px 32px rgba(0, 0, 0, 0.4)',
                'glow-sm': '0 0 10px rgba(99, 102, 241, 0.4)',
                'glow-md': '0 0 20px rgba(99, 102, 241, 0.5)',
                'glow-cyan': '0 0 20px rgba(6, 182, 212, 0.4)',
            },
            backdropBlur: {
                xs: '2px',
            },
        },
    },
    plugins: [],
};
export default config;
