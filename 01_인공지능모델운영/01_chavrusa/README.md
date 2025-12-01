# Gradio + FastAPI Mini Project

This folder demonstrates the multi-server and single-server setups for a FastAPI + Gradio workflow using a persisted Iris classifier. Run `train_model.py` once before starting any server to generate `iris_model.pkl`.

| 구분 | 파일명 | 역할 | 실행 주소 (기본 포트) | 핵심 엔드포인트 / 함수 | 설명 |
| --- | --- | --- | --- | --- | --- |
| 백엔드 (서버) | `api.py` | FastAPI 서버 (모델 서빙) | `http://127.0.0.1:8000` | `POST /predict/` | 저장된 `iris_model.pkl` 로드 → 입력 특성(sl, sw, pl, pw) 처리 → JSON 반환 |
| 프론트엔드 (클라이언트) | `app_gradio.py` | Gradio 인터페이스 (UI/UX) | `http://127.0.0.1:7860` | `predict_species()` | 슬라이더로 입력을 받고 FastAPI `/predict/` 호출 → 결과 출력 |
| 연결 URL | `app_gradio.py` via `requests` | 클라이언트 → 서버 HTTP | `http://127.0.0.1:8000/predict/` | `requests.post()` | Gradio에서 FastAPI에 POST 요청을 보내어 예측 수행 |

## Files

- `train_model.py`: trains `RandomForestClassifier` on the Iris dataset and saves it to `iris_model.pkl`.
- `api.py`: FastAPI backend that loads the saved model, validates feature inputs, and exposes `POST /predict/`.
- `app_gradio.py`: Gradio UI that sends slider inputs to the FastAPI backend and renders the prediction/probabilities.
- `gradio_fastapi_twoservers.py`: helper script that launches FastAPI (port 8000) and the Gradio client (port 7860) in parallel threads.
- `main_gradio_mount.py`: single FastAPI instance that mounts the Gradio interface at `/gradio`; API routes are prefixed with `/api`.

## Usage

1. Train the model:
   ```bash
   python 01_chavrusa/train_model.py
   ```
2. Start the FastAPI backend:
   ```bash
   uvicorn api:app --host 127.0.0.1 --port 8000
   ```
3. In another terminal, start the Gradio client:
   ```bash
   python 01_chavrusa/app_gradio.py
   ```

### Multi-server snippet

Use `python 01_chavrusa/gradio_fastapi_twoservers.py` to launch both the FastAPI server and the Gradio UI concurrently. The Gradio UI communicates with `http://127.0.0.1:8000/predict/`.

### Single-server Gradio mount

After training, run:

```bash
python 01_chavrusa/main_gradio_mount.py
```

With this setup:

- Visit `/gradio/` in your browser to see the UI.
- `/api/predict/` accepts `POST`; GET requests will return `405 Method Not Allowed`.
- Use Swagger (`http://127.0.0.1:8000/docs`) or `/gradio/` to submit POST requests.
