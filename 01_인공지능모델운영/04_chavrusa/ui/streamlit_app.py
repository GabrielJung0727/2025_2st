import os
from io import BytesIO

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_BASE = os.getenv("API_BASE", "http://localhost:8000")


def post_json(path: str, payload: dict) -> dict:
    resp = requests.post(f"{API_BASE}{path}", json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()


def upload_file(file) -> dict:
    data = {"file": (file.name, BytesIO(file.getvalue()), file.type)}
    resp = requests.post(f"{API_BASE}/files", files=data, timeout=60)
    resp.raise_for_status()
    return resp.json()


st.set_page_config(page_title="Gemini FastAPI + Streamlit", page_icon="🤖")
st.title("Gemini FastAPI + Streamlit")
st.caption("Tiny demo that calls the FastAPI backend and Gemini.")

st.subheader("1) 일반 챗")
with st.form("chat"):
    query = st.text_area("질문", placeholder="예: Gemini로 FastAPI를 만드는 법을 알려줘", height=100)
    context = st.text_area("선택: 추가 컨텍스트", height=80)
    if st.form_submit_button("보내기"):
        if not query.strip():
            st.warning("질문을 입력하세요.")
        else:
            try:
                data = post_json("/chat", {"query": query, "context": context or None})
                st.success(data.get("response", ""))
            except requests.HTTPError as exc:
                st.error(f"API 오류: {exc.response.text}")

st.subheader("2) 파일 기반 RAG (File Search API)")
uploaded = st.file_uploader("텍스트/문서 파일 업로드", type=["txt", "md", "pdf"])
rag_question = st.text_area("파일을 참고해 답변받을 질문", height=100)
if st.button("업로드 & 질의"):
    if not uploaded:
        st.warning("파일을 업로드하세요.")
    elif not rag_question.strip():
        st.warning("질문을 입력하세요.")
    else:
        try:
            info = upload_file(uploaded)
            data = post_json(
                "/rag", {"prompt": rag_question, "file_uri": info["file_uri"]}
            )
            st.info(f"파일 업로드: {info['display_name']} (uri: {info['file_uri']})")
            st.success(data.get("response", ""))
        except requests.HTTPError as exc:
            st.error(f"API 오류: {exc.response.text}")
