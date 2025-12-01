## AdventureWorks Sales Intelligence (02_chavrusa)

이 프로젝트는 AdventureWorks Sales CSV 데이터를 자동으로 내려받아 SQLite에 적재하고, FastAPI 기반 부가가치 서비스를 제공합니다. 파이프라인은 다음 단계를 포함합니다.

1. **데이터 수집** – GitHub 원본 CSV(2019 버전)를 다운로드하여 `data/raw`에 저장.
2. **데이터 적재** – 컬럼을 `snake_case`로 정규화하여 SQLite(`data/adventureworks.sqlite`)에 로드.
3. **전처리 및 EDA** – 주문/고객/지역/제품 정보를 조인한 `enriched_sales` 뷰 생성, 기초 통계 요약/시각화 이미지 출력.
4. **시각화** – 월별 매출 추이, 카테고리 매출, 테리토리 매출 그래프(`reports/figures/*.png`).
5. **RFM 분석** – Recency/Frequency/Monetary 점수 및 세그먼트 분류(`data/processed/rfm_segments.parquet`).
6. **예측 모형** – 고객 주문 시퀀스를 기반으로 **다음 구매까지 일 수** 회귀 모델을 학습하여 `models/next_purchase_model.pkl`과 성능 리포트 출력.
7. **API 서비스** – FastAPI가 요약 지표, 월별/카테고리/지역 매출, 고객 RFM, 주문 히스토리, 다음 구매 예측을 엔드포인트로 제공합니다.

### 디렉터리 구조

```
02_chavrusa/
├── api/                  # FastAPI 진입점
├── data/
│   ├── raw/              # 다운로드 받은 CSV
│   ├── processed/        # 파이프라인 산출물(parquet/csv/json)
│   └── adventureworks.sqlite
├── models/               # 학습된 사이킷런 모델
├── reports/figures/      # PNG 시각화 결과
├── scripts/              # 파이프라인 실행 스크립트
├── src/chavrusa/         # 공용 파이썬 모듈
└── README.md
```

### 빠른 시작

```bash
cd 02_chavrusa
pip install -r requirements.txt

# 데이터 다운로드 → SQLite 적재 → EDA/RFM/모델 생성
PYTHONPATH=src python scripts/run_pipeline.py

# FastAPI 실행
PYTHONPATH=src uvicorn api.main:app --reload --port 8000
```

### 주요 산출물

| 파일 | 설명 |
| --- | --- |
| `data/adventureworks.sqlite` | 정규화된 원천 테이블 |
| `data/processed/enriched_sales.parquet` | 주문×제품×지역 풀 조인 데이터 |
| `data/processed/summary.json` | 매출 총괄, 고객 수, 기간, 시각화 경로 |
| `reports/figures/*.png` | 월별/카테고리/지역 시각화 |
| `data/processed/rfm_segments.parquet` | 고객 RFM 세그먼트 |
| `data/processed/model_report.json` | 예측 모델 성능/피처 |
| `models/next_purchase_model.pkl` | 다음 구매 시기 회귀 모델 |

### FastAPI 엔드포인트

| Method | Path | 설명 |
| --- | --- | --- |
| GET | `/health` | 상태 확인 |
| GET | `/metrics/summary` | 매출 총괄 지표 및 시각화 경로 |
| GET | `/metrics/monthly` | 월별 매출 타임시리즈 |
| GET | `/metrics/categories?top_k=10` | 상위 카테고리 매출 |
| GET | `/metrics/territories` | 지역(테리토리)별 매출 |
| GET | `/rfm/segments` | RFM 세그먼트 빈도 |
| GET | `/rfm/customers/{customer_id}` | 특정 고객 RFM 점수/세그먼트 |
| GET | `/customers/{customer_id}/orders?limit=25` | 최근 주문 히스토리 |
| POST | `/forecast/next-purchase` | 다음 구매일까지 예상 일수 (피처 입력 필요) |

`/forecast/next-purchase` 요청 예시:

```json
POST /forecast/next-purchase
{
  "days_since_prev": 45,
  "order_sequence": 3,
  "total_due": 1800.5,
  "avg_order_value_to_date": 1500.0,
  "tenure_days": 400,
  "territory_id": 1,
  "online_order_flag": 0
}
```

응답:

```json
{
  "predicted_days_until_next_purchase": 52.31,
  "model_metrics": {
    "mae": 37.92,
    "rmse": 58.12,
    "r2": 0.47
  },
  "inputs": { ... }
}
```

### 추가 메모

- `scripts/run_pipeline.py --skip-download` 옵션으로 기존 CSV를 재사용할 수 있으며, `--force-download`로 갱신 가능합니다.
- 모든 산출물은 `data/processed`와 `reports/figures`에 저장되므로 대시보드/노트북에서 재사용할 수 있습니다.
- 모델 훈련 데이터는 주문 수준 피처(`days_since_prev`, `order_sequence`, `total_due`, `avg_order_value_to_date`, `tenure_days`, `territory_id`, `online_order_flag`)와 목표값 `days_until_next`로 구성되었습니다.
