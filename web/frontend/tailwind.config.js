/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: '#2E86AB',
                secondary: '#A23B72',
                accent: '#F18F01',
                dark: '#2B2D42',
                light: '#EDF2F4',
            },
        },
    },
    plugins: [],
}
