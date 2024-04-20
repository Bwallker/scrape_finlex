const isDarkMode = !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);

document.documentElement.setAttribute('data-bs-theme', isDarkMode ? 'dark' : 'light');
