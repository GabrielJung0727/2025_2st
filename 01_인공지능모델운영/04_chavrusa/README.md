# 04_chavrusa: Gemini FastAPI + Streamlit + RAG 스터터

Gemini API를 가장 간단히 묶은 샘플입니다.

- FastAPI REST API (`/chat`, `/files`, `/rag`)
- Streamlit UI로 API 호출
- LangChain 기반 RAG 예제 노트북 + File Search API 노트북

## 빠른 시작
```bash
cd 04_chavrusa
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # GEMINI_API_KEY 설정
```

### 백엔드 (FastAPI)
```bash
cd api
uvicorn main:app --reload
# http://localhost:8000/docs
```

### 프론트엔드 (Streamlit)
새 터미널에서:
```bash
cd 04_chavrusa
streamlit run ui/streamlit_app.py  # 기본 API_BASE=http://localhost:8000
```

## 파일 기반 RAG (File Search API)
1. `/files` 엔드포인트로 파일 업로드 → `file_uri` 획득  
2. `/rag`에 `{prompt, file_uri}` 전달 → 파일 내용에 근거한 답변

샘플 데이터: `data/sample.txt`

## 노트북
- `notebooks/Langchain_rag_geminiAPI.ipynb`: LangChain + FAISS로 RAG 전체 흐름
- `notebooks/google_file_search.ipynb`: File Search API로 업로드 후 질의

로컬에서 실행:
```bash
jupyter notebook notebooks/Langchain_rag_geminiAPI.ipynb
```

## 폴더 구조
```
04_chavrusa/
  api/                # FastAPI 서버
  ui/                 # Streamlit UI
  data/               # 데모 문서
  notebooks/          # 실습 노트북
  requirements.txt
  .env.example
```
