# Quick Start Guide

## Installation

```bash
cd skin-scan

# Create virtual environment and install dependencies
make setup

# Or manually:
uv venv
uv pip install -e ".[dev]"
cp .env.example .env
```

## Run the API

```bash
# Start the FastAPI server
make dev

# Or manually:
uv run uvicorn src.app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## Test the API

### Using the Web UI

1. Start the API server (see above)
2. Open `web/client.html` in your browser
3. Upload a face image
4. Click "Scan Image"
5. View the relative condition scores and heatmap overlays

### Using curl

```bash
curl -X POST http://localhost:8000/scan \
  -F "image=@path/to/face.jpg" \
  | jq .
```

### Using the CLI

```bash
# Basic scan
uv run python -m src.cli.scan_image --input path/to/face.jpg --out results/

# Save overlay images
uv run python -m src.cli.scan_image --input path/to/face.jpg --out results/ --save-overlays

# Using make
make scan SCAN=path/to/face.jpg
```

## Docker

```bash
# Build image
docker build -t skin-scan .

# Run container
docker run -p 8000:8000 skin-scan

# Test
curl http://localhost:8000/health
```

## Run Tests

```bash
make test

# Or manually:
uv run pytest -v
```

## API Endpoints

### POST /scan

Upload a facial image and receive analysis results.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Field: `image` (file)

**Response:**
```json
{
  "indices": {
    "redness": 72,
    "oiliness": 45,
    "texture": 58,
    "pores": 33,
    "blemishes": 21,
    "hydration": 67,
    "pigment": 89
  },
  "condition_scores": {
    "redness": 28,
    "oiliness": 55,
    "texture": 42,
    "pores": 67,
    "blemishes": 79,
    "hydration": 67,
    "pigment": 11
  },
  "overlays": {
    "redness": "data:image/png;base64,...",
    "oiliness": "data:image/png;base64,...",
    ...
  },
  "regions": ["forehead", "cheeks", "nose", "chin"]
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "ok": true
}
```

## Expected Results

Each analysis category returns:
- **Feature intensity index**: Relative detected intensity from 0 to 100
- **Condition score**: Direction-normalized value from 0 to 100 where higher is better; not a percentage, percentile, diagnosis, or clinically calibrated score
- **Overlay**: Base64-encoded PNG heatmap with transparency

### Categories

1. **Redness**: Measures skin redness/inflammation using LAB color space
2. **Oiliness**: Detects specular highlights indicating oily areas
3. **Texture**: Analyzes skin roughness using local variance
4. **Pores**: Identifies pore density via blob detection
5. **Blemishes**: Detects spots, acne, and imperfections
6. **Hydration**: Higher-is-better proxy computed as 1 minus robustly normalized roughness, brightness unevenness, and edge strength
7. **Pigmentation**: Detects melanin-rich areas and dark spots

## Troubleshooting

### "No face detected"
- Ensure image contains a clear, front-facing face
- Check image quality and lighting
- Face should take up significant portion of image

### Low quality results
- Use well-lit images with diffused lighting
- Avoid harsh shadows or extreme angles
- Recommended: neutral background, no makeup filters

### Import errors
- Ensure all dependencies installed: `uv pip install -e ".[dev]"`
- Check Python version: requires 3.11+

### API errors
- Check logs for detailed error messages
- Verify `.env` file exists (copy from `.env.example`)
- Ensure port 8000 is available

## Next Steps

1. **Collect training data**: Save scans with `--save-overlays` for model training
2. **Train ML models**: Use `src/ml/train_acne.py` as template for blemish classifier
3. **Tune parameters**: Adjust thresholds in individual map modules
4. **Add features**: Extend with wrinkle detection, elasticity, etc.
5. **Deploy**: Use Docker image for production deployment

## Development

```bash
# Lint code
make lint

# Run specific test
uv run pytest tests/test_maps.py::test_redness_map -v

# Clean build artifacts
make clean
```

## Notes

- This is a **cosmetic analysis tool**, not medical software
- Results are estimates based on computer vision heuristics
- For production use, validate against ground truth data
- Privacy: EXIF data is automatically stripped from uploads
