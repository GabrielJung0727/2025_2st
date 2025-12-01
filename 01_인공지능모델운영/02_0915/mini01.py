import os
import random
from typing import List, Dict, Optional
import tempfile
import requests

# Optional: auto-load .env for local secrets
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

import pandas as pd
import gradio as gr
from faker import Faker


def make_phone() -> str:
    mid = random.randint(0, 9999)
    end = random.randint(0, 9999)
    return f"010-{mid:04d}-{end:04d}"


def fetch_addresses_kakao(query: str, want: int, api_key: Optional[str] = None) -> List[str]:
    """Fetch Korean addresses using Kakao Local API.

    Requires env var KAKAO_REST_API_KEY if api_key not provided.
    """
    key = api_key or os.environ.get("KAKAO_REST_API_KEY")
    if not key:
        return []

    headers = {"Authorization": f"KakaoAK {key}"}
    collected: List[str] = []
    page = 1
    # Kakao size max is 30; fetch several pages until we have enough or no more results
    while len(collected) < want and page <= 5:
        try:
            resp = requests.get(
                "https://dapi.kakao.com/v2/local/search/address.json",
                params={"query": query, "size": 30, "page": page},
                headers=headers,
                timeout=5,
            )
            resp.raise_for_status()
            data = resp.json()
            docs = data.get("documents", [])
            if not docs:
                break
            for d in docs:
                road = (d.get("road_address") or {}).get("address_name")
                jibun = (d.get("address") or {}).get("address_name")
                addr = road or jibun
                if addr and addr not in collected:
                    collected.append(addr)
        except Exception:
            break
        page += 1
    return collected


def generate_people(n: int = 10, seed: Optional[int] = None, addr_query: str = "서울") -> pd.DataFrame:
    """Generate a DataFrame of people and sort by 이름, 나이."""
    fake = Faker("ko_KR")
    if seed is not None:
        Faker.seed(seed)
        random.seed(seed)

    # Fetch addresses from external API; graceful fallback to Faker if empty
    addresses = fetch_addresses_kakao(addr_query, max(n, 30))
    # Shuffle for randomness but deterministic under seed
    random.shuffle(addresses)
    if len(addresses) >= n:
        addresses = addresses[:n]
    else:
        # If not enough from API, fill remaining using Faker addresses
        while len(addresses) < n:
            addresses.append(fake.address().replace("\n", " "))

    rows: List[Dict[str, object]] = []
    for i in range(n):
        name = fake.name()
        address = addresses[i]
        phone = make_phone()
        email = fake.email()
        job = fake.job()
        age = random.randint(18, 70)

        rows.append(
            {
                "이름": name,
                "주소": address,
                "전화번호": phone,
                "이메일": email,
                "직업": job,
                "나이": age,
            }
        )

    df = pd.DataFrame(rows, columns=["이름", "주소", "전화번호", "이메일", "직업", "나이"])
    df = df.sort_values(by=["이름", "나이"], ascending=[True, True], ignore_index=True)
    return df


def on_generate(n: int, seed: str, addr_query: str):
    seed_val = int(seed) if seed.strip() != "" else None
    df = generate_people(n=n, seed=seed_val, addr_query=addr_query)
    return df, df


def download_csv(current_df: Optional[pd.DataFrame]) -> str:
    df = current_df if isinstance(current_df, pd.DataFrame) else generate_people(10, None)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
    df.to_csv(tmp.name, index=False, encoding="utf-8-sig")
    return tmp.name


with gr.Blocks(title="가짜 사용자 데이터 생성기") as demo:
    gr.Markdown("""
    # 가짜 사용자 데이터 생성기
    - Faker(ko_KR)로 이름/이메일/직업을 생성합니다.
    - 전화번호는 010-XXXX-XXXX 형식으로 생성됩니다.
    - 주소는 외부 Kakao Local API(주소 검색)를 통해 조회합니다. (환경변수 KAKAO_REST_API_KEY 필요)
    - 결과는 "이름 → 나이" 순으로 정렬되어 표시됩니다.
    - 시드(Seed): 난수 생성 시작점을 고정해 같은 입력이면 동일한 결과가 재생성되도록 합니다.
    """)

    with gr.Row():
        n_input = gr.Slider(minimum=1, maximum=100, value=10, step=1, label="생성 인원수")
        seed_input = gr.Textbox(value="", label="시드(선택)", placeholder="예: 20 (비워두면 매번 랜덤)")
        addr_query_input = gr.Textbox(value="서울", label="주소 키워드", placeholder="예: 서울, 부산, 강남구 ...")
        gen_btn = gr.Button("새로 생성")

    with gr.Row():
        download_btn = gr.Button("CSV 다운로드")
        file_out = gr.File(label="다운로드된 CSV 파일", interactive=False)

    table = gr.Dataframe(interactive=False, label="생성된 사용자 목록 (이름 → 나이 정렬)")
    state_df = gr.State(value=None)

    gen_btn.click(fn=on_generate, inputs=[n_input, seed_input, addr_query_input], outputs=[table, state_df])
    download_btn.click(fn=download_csv, inputs=state_df, outputs=file_out)
    # 초기 로드 시 자동 생성 (테이블과 상태 동시 설정)
    demo.load(fn=lambda: (generate_people(10, None, "서울"), generate_people(10, None, "서울")), outputs=[table, state_df])


if __name__ == "__main__":
    demo.launch()
