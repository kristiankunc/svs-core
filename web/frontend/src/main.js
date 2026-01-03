import Alpine from 'alpinejs';
import hljs from 'highlight.js/lib/core';
import dockerfile from 'highlight.js/lib/languages/dockerfile';
import "./main.scss";

hljs.registerLanguage('dockerfile', dockerfile);

document.querySelectorAll('pre code').forEach(el => {
  hljs.highlightElement(el)
})

// Theme management
const getStoredTheme = () => localStorage.getItem('theme');
const setStoredTheme = theme => localStorage.setItem('theme', theme);

const getPreferredTheme = () => {
    const storedTheme = getStoredTheme();
    if (storedTheme) {
        return storedTheme;
    }
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
};

const setTheme = theme => {
    if (theme === 'auto') {
        document.documentElement.setAttribute('data-bs-theme',
            window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
    } else {
        document.documentElement.setAttribute('data-bs-theme', theme);
    }
};

// Set theme on load
setTheme(getPreferredTheme());

// Listen for system theme changes when theme is set to auto
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    const storedTheme = getStoredTheme();
    if (storedTheme !== 'light' && storedTheme !== 'dark') {
        setTheme(getPreferredTheme());
    }
});

// Alpine.js component for theme switcher
Alpine.data('themeSwitcher', () => ({
    theme: getStoredTheme() || 'auto',

    init() {
        this.$watch('theme', value => {
            setStoredTheme(value);
            setTheme(value);
        });
    },

    setTheme(newTheme) {
        this.theme = newTheme;
    },

    toggleTheme() {
        // Toggle between light and dark only
        // If currently auto, switch to light first
        if (this.theme === 'auto' || this.theme === 'dark') {
            this.theme = 'light';
        } else {
            this.theme = 'dark';
        }
    },

    isActive(checkTheme) {
        return this.theme === checkTheme;
    }
}));

window.Alpine = Alpine;
Alpine.start();
