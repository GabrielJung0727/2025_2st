# School 📚

학습용 코드와 실습 자료가 담긴 저장소입니다. 특히 `인공지능모델운영/0915/mini01.py`는 Gradio 기반의 데모 앱으로, 한국어 Faker와 외부 주소 API를 활용해 가짜 사용자 데이터를 생성·조회·다운로드할 수 있습니다.

## 주요 기능

- 10명(가변) 가짜 사용자 생성: 이름, 주소, 전화번호, 이메일, 직업, 나이
- 정렬: 항상 이름 → 나이 순으로 표 정렬
- 전화번호 형식 고정: `010-XXXX-XXXX`
- 실제 주소 검색: Kakao Local API(주소 검색) 연동, 키워드로 지역 지정
- 재현성 보장: 시드(Seed)로 동일 입력 시 동일 결과 재생성
- CSV 다운로드: 현재 표시 중인 표를 바로 CSV로 저장(UTF-8 BOM)

## 빠른 시작

사전 준비: Python 3.8+ 권장

```bash
pip install -U gradio faker pandas requests python-dotenv
```

앱 실행:

```bash
python 인공지능모델운영/0915/mini01.py
```

브라우저에서 표시되는 Gradio 링크로 접속합니다.

## 환경변수(.env)

Kakao Local API 사용을 위해 REST API Key를 환경변수로 설정하세요. 루트 디렉토리에 `.env` 파일을 만들고 아래를 추가합니다.

```
KAKAO_REST_API_KEY=여기에_카카오_REST_API_KEY
```

참고: `.gitignore`에 `.env`가 이미 제외되어 있어 실수로 커밋되지 않습니다. `python-dotenv`가 설치되어 있으면 앱 시작 시 자동으로 `.env`를 로드합니다. 환경변수를 직접 `export`해서 사용해도 됩니다.

## 사용 방법(Gradio UI)

- 생성 인원수: 1–50 사이에서 선택(기본 10명)
- 시드(선택): 같은 시드와 같은 입력이면 동일한 결과 재생성, 비우면 매번 랜덤
- 주소 키워드: 예) 서울, 부산, 강남구 등 — Kakao Local API로 해당 키워드 기반 주소 검색
- 새로 생성: 표를 갱신하고 상태에 보관
- CSV 다운로드: 현재 표 그대로 CSV 파일 다운로드(Excel 호환 UTF-8 BOM)

주소 API가 비활성화(키 미설정/네트워크 오류)거나 결과가 부족하면 Faker 주소로 자동 보충합니다.

## 폴더 안내

- `인공지능모델운영/0915/mini01.py`: Gradio 데모 앱 소스
- `인공지능모델운영/0915/.env`(옵션): 로컬 실행용 환경변수 파일

## 개발 메모

- 외부 API: Kakao Local(주소 검색) — `KAKAO_REST_API_KEY` 필요
- 의존성: `gradio`, `faker`, `pandas`, `requests`, `python-dotenv`
- CSV 인코딩: `utf-8-sig`로 저장해 Excel에서 한글이 깨지지 않도록 처리

## 문제 해결

- 주소가 전부 Faker로 보일 때: API Key 설정 여부와 네트워크 접근 가능 여부 확인
- CSV에서 한글 깨짐: 다른 뷰어 사용 또는 Excel에서 UTF-8로 열기
- 포트 충돌: Gradio 실행 시 다른 포트 지정 `demo.launch(server_port=7861)` 등으로 변경 가능

즐거운 실습 되세요! 🚀

