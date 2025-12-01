import os
from typing import Tuple, Optional
from urllib.parse import unquote

import pandas as pd
import requests
import folium
from folium.plugins import MarkerCluster

import gradio as gr


JEJU_CENTER = (33.38, 126.53)


def _load_dotenv_simple(path: str = ".env") -> None:
    """Very small .env loader (KEY=VALUE per line, no quotes)."""
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    k, v = k.strip(), v.strip()
                    if k and v and k not in os.environ:
                        os.environ[k] = v
    except Exception:
        # best-effort only
        pass


def _normalize_key(key: str) -> str:
    """Decode percent-encoded key up to 3 times to avoid double-encoding."""
    if not key:
        return key
    for _ in range(3):
        nk = unquote(key)
        if nk == key:
            break
        key = nk
    return key


def fetch_oreum_df() -> pd.DataFrame:
    """Fetch oreum data from ODCloud or load from CSV if present.

    Priority:
    1) Load CSV `제주오름_좌표.csv` if it exists.
    2) Else call ODCloud API using env `ODCLOUD_SERVICE_KEY` and derive DataFrame.
    """
    csv_path = os.path.join(os.path.dirname(__file__), "제주오름_좌표.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        # Ensure expected columns exist
        expected = {"오름명", "위도", "경도"}
        if expected.issubset(df.columns):
            return df

    # Fallback: call API
    _load_dotenv_simple()  # try to populate env
    raw_key = os.getenv("ODCLOUD_SERVICE_KEY", "")
    if not raw_key:
        raise RuntimeError(
            "ODCLOUD_SERVICE_KEY not set and CSV not found. Set env var or place 제주오름_좌표.csv."
        )

    service_key = _normalize_key(raw_key)
    base = "https://api.odcloud.kr/api"
    uddi = "uddi:78ffcb9e-6d65-4650-8568-921c94d0d9ec"  # 2024-05-02
    endpoint = f"/3082952/v1/{uddi}"
    url = f"{base}{endpoint}"
    params = {
        "serviceKey": service_key,
        "page": 1,
        "perPage": 1000,
        "returnType": "JSON",
    }
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()

    if isinstance(payload, dict):
        if isinstance(payload.get("data"), list):
            rows = payload["data"]
        elif isinstance(payload.get("records"), list):
            rows = payload["records"]
        else:
            rows = next((v for v in payload.values() if isinstance(v, list)), [])
    else:
        rows = payload if isinstance(payload, list) else []

    raw_df = pd.DataFrame(rows)
    return _select_oreum_columns(raw_df)


def _select_oreum_columns(df: pd.DataFrame) -> pd.DataFrame:
    cols = list(df.columns)
    lower = {c: str(c).lower() for c in cols}

    def find_col(cands):
        for cand in cands:
            for c in cols:
                lc = lower[c]
                if cand in str(c) or cand in lc:
                    return c
        return None

    name_col = find_col(["오름", "명칭", "이름", "명"]) or "오름명"
    lat_col = find_col(["위도", "latitude", "lat", "(y", " y", " y)"]) or "위도"
    lon_col = find_col(["경도", "longitude", "lon", "(x", " x", " x)"]) or "경도"
    desc_col = find_col(["설명", "소개", "상세", "상세설명", "내용", "비고", "개요", "메모", "description", "detail"])  # optional
    img_col  = find_col(["이미지", "사진", "image", "img", "thumbnail"])  # optional
    link_col = find_col(["링크", "url", "URL", "homepage", "홈페이지", "상세보기"])  # optional

    keep = [name_col, lat_col, lon_col]
    opt = [c for c in [desc_col, img_col, link_col] if c]
    out = df[keep + opt].copy()
    # Rename required + optional
    rename = {name_col: "오름명", lat_col: "위도", lon_col: "경도"}
    if desc_col:
        rename[desc_col] = "설명"
    if img_col:
        rename[img_col] = "이미지"
    if link_col:
        rename[link_col] = "링크"
    out = out.rename(columns=rename)
    out["위도"] = pd.to_numeric(out["위도"], errors="coerce")
    out["경도"] = pd.to_numeric(out["경도"], errors="coerce")
    out = out.dropna(subset=["위도", "경도"]).reset_index(drop=True)
    # Rough Jeju bbox guard
    out = out[(out["위도"].between(32.5, 34.5)) & (out["경도"].between(125.0, 129.0))]
    # Ensure optional columns exist
    for c in ["설명", "이미지", "링크"]:
        if c not in out.columns:
            out[c] = ""
    # Order columns
    ordered = ["오름명", "위도", "경도", "설명", "이미지", "링크"]
    extras = [c for c in out.columns if c not in ordered]
    out = out[ordered + extras]
    return out.reset_index(drop=True)


def _build_map(df: pd.DataFrame, use_cluster: bool) -> folium.Map:
    if len(df) == 0:
        m = folium.Map(location=JEJU_CENTER, zoom_start=10, tiles="OpenStreetMap")
        return m

    lat = df["위도"].mean()
    lon = df["경도"].mean()
    m = folium.Map(location=[lat, lon], zoom_start=11, tiles="OpenStreetMap")
    layer = MarkerCluster() if use_cluster else m
    if use_cluster:
        layer.add_to(m)

    for _, r in df.iterrows():
        name = str(r.get("오름명", ""))
        desc = str(r.get("설명", ""))
        img = str(r.get("이미지", ""))
        link = str(r.get("링크", ""))
        html_parts = [f"<h4 style='margin:4px 0'>{name}</h4>"]
        if desc:
            html_parts.append(f"<div style='max-width:260px;white-space:normal'>{desc}</div>")
        if img and (img.startswith("http://") or img.startswith("https://")):
            html_parts.append(f"<div style='margin-top:6px'><img src='{img}' width='220' style='border-radius:4px'/></div>")
        if link and (link.startswith("http://") or link.startswith("https://")):
            html_parts.append(f"<div style='margin-top:6px'><a href='{link}' target='_blank'>상세 링크</a></div>")
        popup_html = "".join(html_parts)
        folium.Marker([r["위도"], r["경도"]], popup=folium.Popup(popup_html, max_width=300)).add_to(layer)
    return m


# Load data once at startup
try:
    OREUM_DF = fetch_oreum_df()
except Exception as e:
    # Defer raising to the UI callback so app can show message
    OREUM_DF = None
    STARTUP_ERROR = str(e)
else:
    STARTUP_ERROR = ""


def _load_from_file(file_path: str) -> Optional[pd.DataFrame]:
    try:
        df = pd.read_csv(file_path)
        return _select_oreum_columns(df)
    except Exception:
        return None


def _load_from_url(data_url: str) -> Optional[pd.DataFrame]:
    try:
        r = requests.get(data_url, timeout=30)
        r.raise_for_status()
        ctype = r.headers.get("content-type", "").lower()
        if data_url.lower().endswith(".csv") or "text/csv" in ctype:
            from io import StringIO
            df = pd.read_csv(StringIO(r.text))
        else:
            payload = r.json()
            if isinstance(payload, dict):
                rows = payload.get("data") or payload.get("records")
                if not isinstance(rows, list):
                    rows = next((v for v in payload.values() if isinstance(v, list)), [])
            else:
                rows = payload if isinstance(payload, list) else []
            df = pd.DataFrame(rows)
        return _select_oreum_columns(df)
    except Exception:
        return None


def search_and_render(query: str, cluster: bool, file, data_url: str) -> Tuple[str, pd.DataFrame, str]:
    # Determine data source priority: file > url > startup
    df_src: Optional[pd.DataFrame] = None
    if file is not None:
        df_src = _load_from_file(getattr(file, "name", file))
    if df_src is None and data_url:
        df_src = _load_from_url(data_url.strip())
    if df_src is None:
        if OREUM_DF is None:
            return (f"<div style='color:red'>로드 오류: {STARTUP_ERROR}</div>", pd.DataFrame(), STARTUP_ERROR)
        df_src = OREUM_DF

    q = (query or "").strip().lower()
    df = df_src
    if q:
        df = df[df["오름명"].astype(str).str.lower().str.contains(q, na=False)]

    m = _build_map(df, use_cluster=cluster)
    html = m.get_root().render()
    # Show canonical columns first
    preview_cols = [c for c in ["오름명", "위도", "경도", "설명", "이미지", "링크"] if c in df.columns]
    preview = df[preview_cols].head(200)
    info = f"총 {len(df)}건"
    return html, preview, info


with gr.Blocks(title="제주 오름 지도 검색") as demo:
    gr.Markdown("""
    # 제주 오름 지도 검색 (Gradio)
    - 검색어로 오름명을 필터링하고 Folium 지도를 표시합니다.
    - 클러스터 옵션으로 다수 마커를 보기 쉽게 묶을 수 있습니다.
    """)

    with gr.Row():
        query = gr.Textbox(label="검색어 (오름명)", placeholder="예: 군산, 오름 ...", scale=3)
        cluster = gr.Checkbox(value=True, label="마커 클러스터")
        run_btn = gr.Button("검색/업데이트", variant="primary")
    with gr.Row():
        upload = gr.File(label="CSV 업로드 (오름명/위도/경도 포함)", file_types=[".csv"], interactive=True)
        data_url = gr.Textbox(label="데이터 URL (CSV 또는 JSON)", placeholder="https://...csv 또는 ...json")

    with gr.Row():
        map_html = gr.HTML(label="지도")
    with gr.Row():
        info_text = gr.Textbox(label="검색 결과", interactive=False)
    with gr.Row():
        table = gr.Dataframe(label="오름 목록 (일부 미리보기)", wrap=True)

    def _run(q, c, f, u):
        html, df, info = search_and_render(q, c, f, u)
        return html, info, df

    # Trigger on button and on text change
    run_btn.click(_run, inputs=[query, cluster, upload, data_url], outputs=[map_html, info_text, table])
    query.submit(_run, inputs=[query, cluster, upload, data_url], outputs=[map_html, info_text, table])
    upload.change(_run, inputs=[query, cluster, upload, data_url], outputs=[map_html, info_text, table])
    data_url.submit(_run, inputs=[query, cluster, upload, data_url], outputs=[map_html, info_text, table])

    # Initial load
    gr.on(
        triggers=[demo.load],
        fn=_run,
        inputs=[query, cluster, upload, data_url],
        outputs=[map_html, info_text, table],
    )


if __name__ == "__main__":
    # In notebooks/Colab, this renders inline; in terminal, opens local server.
    demo.launch()
