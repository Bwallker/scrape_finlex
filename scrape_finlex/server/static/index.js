const isDarkMode = !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);

document.documentElement.setAttribute('data-bs-theme', isDarkMode ? 'dark' : 'light');

const scrapeData = () => {
    console.log('Scraping data...');
};
