// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    app: {
        pageTransition: {name: 'page', mode: 'out-in'}
    },
    experimental: {
        appManifest: false,
    },
    runtimeConfig: {
        public: {
            websocketUrl: process.env.websocketUrl || process.env.WEBSOCKET_URL || 'auto',
            refereeUrl: process.env.refereeUrl || process.env.REFEREE_URL || 'auto',
            streamEmbedUrl: process.env.streamEmbedUrl || process.env.STREAM_EMBED_URL || 'auto'
        }
    },

    modules: [
        '@nuxtjs/tailwindcss',
        '@nuxtjs/google-fonts',
        '@nuxt/image',
        'nuxt-icon',
        '@pinia/nuxt',
        'pinia-plugin-persistedstate'
    ],
    devtools: {
        enabled: true,

        timeline: {
            enabled: true
        }
    },
    css: ['~/assets/css/main.css'],

    postcss: {
        plugins: {
            tailwindcss: {},
            autoprefixer: {},
        },
    },
    googleFonts: {
        download: true,
        inject: true,
        families: {
            Inter: '200..900',
            "Space Mono": true,
        },
    },

    pinia: {
        storesDirs: ['./stores/**'],
    },

    compatibilityDate: '2025-04-18'
})
