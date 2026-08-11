# Skin Scan

얼굴 사진을 기반으로 피부 특징을 분석하는 로컬 API입니다.

분석 항목:

- Redness
- Oiliness
- Texture
- Pores
- Blemishes
- Hydration
- Pigment

모든 분석은 OpenCV와 MediaPipe를 사용해 로컬에서 실행됩니다. 외부 API 키가 필요하지 않습니다.

## Requirements

- Python 3.12
- uv
- Windows, macOS, Linux

MediaPipe가 Python 3.14를 지원하지 않으므로 Python 3.12를 사용해야 합니다.

## Installation

저장소를 내려받고 프로젝트 폴더로 이동합니다.

```bash
git clone <REPOSITORY_URL>
cd skin-scan-main
```

`uv`가 설치되어 있지 않다면:

```bash
python -m pip install uv
```

Python 3.12를 설치하고 가상환경을 생성합니다.

```bash
uv python install 3.12
uv venv --python 3.12 --clear
uv sync --extra dev
```

설치가 정상인지 확인합니다.

```bash
uv run --python 3.12 python -c "import sys, mediapipe; print(sys.version); print(mediapipe.__version__)"
```

Python 3.12와 MediaPipe 버전이 출력되면 설치가 완료된 것입니다.

## Run the API

다음 명령으로 서버를 실행합니다.

```bash
uv run uvicorn src.app.main:app --reload --port 8000
```

실행 후 다음 주소를 사용할 수 있습니다.

- Web UI: http://localhost:8000
- API 문서: http://localhost:8000/docs
- Health check: http://localhost:8000/health

가장 쉬운 테스트 방법은 http://localhost:8000 에 접속해 얼굴 사진을 업로드하는 것입니다.

## Test with the Web UI

1. http://localhost:8000 접속
2. 얼굴 사진 선택
3. `Scan Image` 클릭
4. 분석 결과 확인

사진은 다음 조건일수록 좋습니다.

- 얼굴이 정면을 향함
- 얼굴이 사진에서 충분히 크게 보임
- 밝고 균일한 조명
- 과도한 필터나 메이크업이 없음

## Test with curl

Windows PowerShell:

```powershell
curl.exe -X POST http://localhost:8000/scan -F "image=@C:\path\to\face.jpg"
```

macOS/Linux:

```bash
curl -X POST http://localhost:8000/scan \
  -F "image=@/path/to/face.jpg"
```

응답 예시:

```json
{
  "indices": {
    "redness": 39,
    "oiliness": 24,
    "texture": 11,
    "pores": 0,
    "blemishes": 21,
    "hydration": 16,
    "pigment": 15
  },
  "condition_scores": {
    "redness": 61,
    "oiliness": 76,
    "texture": 89,
    "pores": 100,
    "blemishes": 79,
    "hydration": 16,
    "pigment": 85
  },
  "overlays": {
    "redness": "data:image/png;base64,...",
    "oiliness": "data:image/png;base64,..."
  },
  "regions": [
    "forehead",
    "nose",
    "chin",
    "cheeks"
  ]
}
```

## Score Meaning

### `indices`

`indices`는 사진 안에서 특정 특징이 얼마나 강하게 검출됐는지를 나타내는 상대 지수입니다.

- 범위: `0~100`
- 높을수록 해당 특징이 강하게 검출됨
- 퍼센트나 백분위가 아님
- 의료적 진단 결과가 아님

예를 들어:

```text
Redness index 39
```

는 피부의 39%가 붉다는 뜻이 아니라, 해당 사진의 얼굴 영역에서 붉음 특징이 상대적으로 어느 정도 검출됐다는 뜻입니다.

### `condition_scores`

`condition_scores`는 모든 항목에서 높을수록 상대적으로 양호한 방향이 되도록 변환한 값입니다.

```text
Redness condition score   = 100 - redness index
Oiliness condition score  = 100 - oiliness index
Texture condition score   = 100 - texture index
Pores condition score     = 100 - pores index
Blemishes condition score = 100 - blemishes index
Hydration condition score = hydration index
Pigment condition score   = 100 - pigment index
```

이 점수는 방향을 통일한 상대 상태 점수이며, 임상적으로 보정된 피부 건강 점수는 아닙니다.

## CLI Scan

이미지 한 장을 명령줄에서 분석할 수 있습니다.

```bash
uv run python -m src.cli.scan_image \
  --input path/to/face.jpg \
  --out results \
  --save-overlays
```

Windows PowerShell:

```powershell
uv run python -m src.cli.scan_image `
  --input "C:\path\to\face.jpg" `
  --out results `
  --save-overlays
```

결과 폴더에는 다음 파일이 생성됩니다.

- `*_analysis.json`: 원본 지수와 상태 점수
- `*_redness_overlay.png`
- `*_oiliness_overlay.png`
- 기타 항목별 오버레이 이미지

## Run Tests

```bash
uv run pytest -q
```

현재 테스트에는 다음 항목이 포함되어 있습니다.

- 각 피부 분석 맵의 출력 범위
- 0~100 특징 강도 지수 변환
- 높을수록 양호한 상태 점수 변환
- 수분 알고리즘의 매끄러운 이미지와 노이즈 이미지 비교
- 빈 얼굴 마스크 처리

## Troubleshooting

### MediaPipe 설치 오류

다음과 같은 오류가 발생하면 Python 3.14를 사용 중인 것입니다.

```text
mediapipe ... doesn't have a source distribution or wheel for the current platform
```

Python 3.12 환경을 다시 생성합니다.

```powershell
uv python install 3.12
uv venv --python 3.12 --clear
uv sync --extra dev
```

### `No face detected in image`

다음 조건의 사진을 사용하세요.

- 얼굴이 정면에 가까움
- 얼굴이 충분히 큼
- 조명이 너무 어둡거나 강하지 않음
- 얼굴이 다른 물체에 가려지지 않음

### 웹 화면에서 결과 요소를 찾을 수 없다는 오류

기존 브라우저 캐시가 남아 있을 수 있습니다.

- Windows/Linux: `Ctrl + F5`
- macOS: `Cmd + Shift + R`

가능하면 프런트엔드와 API를 별도 포트로 실행하지 말고, `http://localhost:8000`에서 제공되는 Web UI를 사용하세요.

별도 프런트엔드를 8080 포트에서 실행하는 경우에도 API 서버는 8000 포트에서 실행되어야 합니다. API 포트를 변경하면 `web/demo.js`의 `API_URL`도 함께 변경해야 합니다.

## Disclaimer

이 프로젝트는 교육·연구 목적의 화장품 분석 도구입니다.

의료 진단, 질병 판정, 치료 결정 또는 전문적인 피부 상태 평가에 사용하지 마세요.
````
