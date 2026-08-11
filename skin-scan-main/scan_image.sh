#!/bin/bash
# Simple script to scan an image using the Skin Scan API

if [ "$#" -ne 1 ]; then
    echo "Usage: ./scan_image.sh /path/to/image.jpg"
    exit 1
fi

IMAGE_PATH="$1"

if [ ! -f "$IMAGE_PATH" ]; then
    echo "Error: Image file not found at $IMAGE_PATH"
    exit 1
fi

echo "Scanning: $IMAGE_PATH"
echo ""

curl -s -X POST http://127.0.0.1:8000/scan \
    -F "image=@${IMAGE_PATH}" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('=== Skin Analysis Results ===\n')
print('Scores:')
for category, score in data.get('scores', {}).items():
    bar = '█' * int(score * 20)
    print(f'  {category:12s}: {score:.2f} {bar}')

print(f'\nRegions: {', '.join(data.get('regions', []))}')
print(f'Overlays: {len(data.get('overlays', {}))} heatmaps generated')
"
