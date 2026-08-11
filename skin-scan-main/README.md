# Skin-Scan OSS Starter

Production-grade skin analysis API that generates 7 category maps from facial images: redness, oiliness, texture, pores, blemishes, hydration, and pigmentation.

**✨ 100% Free & Open Source** - No API keys or external services required. All processing runs locally using OpenCV and MediaPipe.

## Quickstart

### Local

```bash
# Python 3.11+
uv venv && uv pip install -e .
cp .env.example .env

# Run API
uv run uvicorn src.app.main:app --reload --port 8000

# One-off CLI scan
uv run python -m src.cli.scan_image --input path/to/face.jpg --out out_dir/
```

### Docker

```bash
docker build -t skin-scan .
docker run -p 8000:8000 skin-scan
```

### Make targets

```bash
make setup      # Create venv, install dependencies
make dev        # Run API with reload
make test       # Run pytest
make scan SCAN=path/to/img.jpg  # CLI scan
make lint       # Run ruff + pyright
```

## API Endpoints

### POST /scan

Upload an image and receive skin analysis results.

**Request:** multipart/form-data with `image` field

**Response:**
```json
{
  "indices": {
    "redness": 81,
    "oiliness": 74,
    "texture": 62,
    "pores": 48,
    "blemishes": 36,
    "hydration": 29,
    "pigment": 97
  },
  "condition_scores": {
    "redness": 19,
    "oiliness": 26,
    "texture": 38,
    "pores": 52,
    "blemishes": 64,
    "hydration": 29,
    "pigment": 3
  },
  "overlays": {
    "redness": "data:image/png;base64,...",
    "oiliness": "...",
    "texture": "...",
    "pores": "...",
    "blemishes": "...",
    "hydration": "...",
    "pigment": "..."
  },
  "regions": ["forehead", "nose", "cheeks", "chin"]
}
```

### GET /health

Health check endpoint.

## Pipeline Overview

```
input image
→ preprocess (color constancy, white balance, face crop, gamma)
→ landmarks (MediaPipe FaceMesh - 468 points)
→ region masks (forehead, cheeks, nose, chin)
→ per-map analysis:
   • redness: CIE LAB a* channel
   • oiliness: specular highlight detection
   • texture: local binary patterns / variance
   • pores: blob detection on high-pass filter
   • blemishes: rule-based + optional CNN
   • hydration: texture-based proxy
   • pigment: normalized brown mask
→ normalize maps to [0,1], compute feature-intensity indices [0,100] and higher-is-better condition scores
→ overlay RGBA heatmaps
→ JSON + base64 overlays out
```

## Map Algorithms

### Redness
Convert to CIE LAB, use a* channel. Z-score within face mask, clamp to [0,1].

### Oiliness
Detect specular highlights via HSV thresholding (high V, low S) with gradient confirmation.

### Texture
Local Binary Patterns or Laplacian variance over patches. High variance = roughness.

### Pores
High-pass filter (DoG) + Laplacian of Gaussian blob detector (radius 2-5px).

### Blemishes
Rule-based: oiliness + pore blobs + brightness delta. Optional CNN classifier.

### Hydration
Proxy from 1 minus a weighted dryness map: local roughness 40%, brightness unevenness 30%, and gradient strength 30%. Features use face-region 95th-percentile scaling to limit outlier distortion.

### Pigment
Brown mask via RGB thresholds and LAB b* after shading correction.

## Structure

```
skin-scan/
├─ src/
│  ├─ app/              # FastAPI application
│  ├─ pipeline/         # Image analysis pipeline
│  │  ├─ maps/          # Individual map algorithms
│  │  ├─ face_mesh.py   # MediaPipe face detection
│  │  ├─ preprocess.py  # Image preprocessing
│  │  ├─ compose.py     # Pipeline orchestration
│  │  └─ visualize.py   # Heatmap generation
│  ├─ ml/               # Optional ML models
│  └─ cli/              # Command-line interface
├─ tests/
└─ web/                 # Demo frontend
```

## Disclaimer

This is a cosmetic analysis tool for educational and research purposes. **This is not medical software.** Do not use for diagnostic purposes. Always consult qualified healthcare professionals for medical advice.

## License

MIT
