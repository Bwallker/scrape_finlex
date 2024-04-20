const isDarkMode = !!(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches);

document.documentElement.setAttribute('data-bs-theme', isDarkMode ? 'dark' : 'light');

const form = document.getElementById('scrape-form');
if (form === null) {
    throw new Error('Form not found');
}

const scrapeApiCall = (e) => {
    e.preventDefault();
    const data = new FormData(form);
    fetch('/api/scrape', {
        method: 'POST',
        headers: {
            'Context-Type': 'multipart/form-data',
            'Accept': 'text/csv',
        },
        body: data,
    }).then((res) => res.text()).catch((e) => {
        console.error("Got error from request: ", e);
    }).then((blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.get('output-file-name') || 'output.csv';
        if (!a.download.endsWith('.csv')) {
            a.download += '.csv';
        }
        a.click();
        window.URL.revokeObjectURL(url);
    });
};

form.addEventListener('submit', scrapeApiCall);
