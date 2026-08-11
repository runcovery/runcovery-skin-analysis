const API_URL = 'http://localhost:8000';

const fileInput = document.getElementById('fileInput');
const scanBtn = document.getElementById('scanBtn');
const loading = document.getElementById('loading');
const error = document.getElementById('error');
const results = document.getElementById('results');
const indicesContainer = document.getElementById('indices') || document.getElementById('scores');
const overlaysContainer = document.getElementById('overlays');

let selectedFile = null;
let originalImage = null;

// Enable scan button when file is selected
fileInput.addEventListener('change', (e) => {
    selectedFile = e.target.files[0];

    if (selectedFile) {
        scanBtn.disabled = false;
        scanBtn.style.opacity = '1';
        scanBtn.style.cursor = 'pointer';

        // Load original image
        const reader = new FileReader();
        reader.onload = (e) => {
            originalImage = new Image();
            originalImage.src = e.target.result;
        };
        reader.readAsDataURL(selectedFile);
    } else {
        scanBtn.disabled = true;
        scanBtn.style.opacity = '0.5';
        scanBtn.style.cursor = 'not-allowed';
    }
});

// Scan button click handler
scanBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please select an image first');
        return;
    }

    // Reset UI
    error.style.display = 'none';
    results.classList.remove('active');
    loading.style.display = 'block';
    scanBtn.disabled = true;

    try {
        // Create form data
        const formData = new FormData();
        formData.append('image', selectedFile);

        // Call API
        const response = await fetch(`${API_URL}/scan`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Scan failed');
        }

        const data = await response.json();

        // Display results
        displayResults(data);

    } catch (err) {
        error.textContent = `Error: ${err.message}`;
        error.style.display = 'block';
    } finally {
        loading.style.display = 'none';
        scanBtn.disabled = false;
    }
});

function displayResults(data) {
    if (!indicesContainer) {
        throw new Error('Results container not found. Please hard-refresh the page.');
    }

    // Prefer server-computed condition scores, but derive them for cached APIs.
    let conditionScores = data.condition_scores;
    if (!conditionScores) {
        const legacyScores = !data.indices && data.scores;
        const rawIndices = data.indices || data.scores;
        if (!rawIndices) {
            throw new Error('The API response does not contain skin analysis results.');
        }

        const invertedCategories = new Set([
            'redness', 'oiliness', 'texture', 'pores', 'blemishes', 'pigment'
        ]);
        conditionScores = Object.fromEntries(
            Object.entries(rawIndices).map(([category, value]) => {
                const index = legacyScores && value >= 0 && value <= 1
                    ? Math.round(value * 100)
                    : Math.round(value);
                return [category, invertedCategories.has(category) ? 100 - index : index];
            })
        );
    }

    // Display relative condition scores with a consistent higher-is-better direction.
    indicesContainer.innerHTML = '';
    for (const [category, score] of Object.entries(conditionScores)) {
        const card = document.createElement('div');
        card.className = 'index-card';
        card.innerHTML = `
            <h3>${category}</h3>
            <div class="index-value">${Math.round(score)} / 100</div>
        `;
        indicesContainer.appendChild(card);
    }

    // Display overlays
    overlaysContainer.innerHTML = '';
    for (const [category, overlayDataURL] of Object.entries(data.overlays)) {
        const card = document.createElement('div');
        card.className = 'overlay-card';

        const title = document.createElement('h4');
        title.textContent = category;
        card.appendChild(title);

        const canvasContainer = document.createElement('div');
        canvasContainer.className = 'canvas-container';

        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        // Load and composite overlay
        const overlay = new Image();
        overlay.onload = () => {
            // Set canvas size to match original image
            if (originalImage && originalImage.complete) {
                canvas.width = originalImage.width;
                canvas.height = originalImage.height;

                // Draw original image
                ctx.drawImage(originalImage, 0, 0);

                // Draw overlay
                ctx.drawImage(overlay, 0, 0, canvas.width, canvas.height);
            } else {
                // Fallback: just show overlay
                canvas.width = overlay.width;
                canvas.height = overlay.height;
                ctx.drawImage(overlay, 0, 0);
            }
        };
        overlay.src = overlayDataURL;

        canvasContainer.appendChild(canvas);
        card.appendChild(canvasContainer);
        overlaysContainer.appendChild(card);
    }

    results.classList.add('active');
}
