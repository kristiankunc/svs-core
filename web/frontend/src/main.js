import Alpine from 'alpinejs';
import * as bootstrap from 'bootstrap';
import "./main.scss";

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
    
    isActive(checkTheme) {
        return this.theme === checkTheme;
    }
}));

window.Alpine = Alpine;
Alpine.start();
