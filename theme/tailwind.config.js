/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        '../templates/**/*.html',
        '../main/templates/**/*.html',
        '../catalogo/templates/**/*.html',
        './templates/**/*.html',
        './static_src/**/*.js',
    ],
    theme: {
        extend: {
            colors: {
                'herbario-green': '#2d5a27',
                'herbario-light-green': '#4a7c59',
                'herbario-cream': '#f5f5dc',
                'herbario-brown': '#8b4513',
            },
            fontFamily: {
                'serif': ['Georgia', 'serif'],
                'sans': ['Inter', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
} 