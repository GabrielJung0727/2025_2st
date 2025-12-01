# 딥러닝 실습 · Colab + Kaggle 환경 구성

이 저장소에는 Google Colab에서 Kaggle 데이터를 내려받아 실습할 수 있도록 준비된 노트북과 설정 파일이 포함되어 있습니다.

## 빠른 시작

1) Colab에서 `colab_kaggle_setup.ipynb`를 열어 위에서 아래로 순서대로 실행합니다.
   - kaggle, opendatasets 설치
   - `kaggle.json` 업로드 및 권한 설정
   - (옵션) Google Drive 마운트
   - 다운로드 종류/슬러그/경로 설정 후 다운로드 실행

2) Kaggle 데이터셋/대회 슬러그 예시
   - 데이터셋: `zynicide/wine-reviews`
   - 대회: `titanic`

3) 참고: Kaggle API 토큰 발급
   - Kaggle 웹 > 우측 상단 개인 메뉴 > Account > API > Create New API Token
   - 내려받은 `kaggle.json`은 절대 저장소에 커밋하지 마세요. (`.gitignore`로 제외 처리)

## 파일 설명

- `colab_kaggle_setup.ipynb`: Colab에서 Kaggle API 설정 및 데이터 다운로드 자동화 노트북
- `.gitignore`: 민감정보(`kaggle.json`)와 대용량 데이터/캐시 제외
- `requirements.txt`: 로컬 환경에서 동일 패키지가 필요할 때 사용(Colab은 노트북에서 설치)

## 로컬 환경(선택)

Colab이 아닌 로컬에서 동일한 패키지가 필요하다면:

```
pip install -r requirements.txt
```

## 저장 경로 기본값

- 로컬: 현재 작업 디렉토리의 `data/` 폴더 (예: `/Users/gabriel/Documents/school/딥러닝실습/1117/data`)
- Colab + Drive: `/content/drive/MyDrive/school/딥러닝실습/1117/data`
  - 노트북에서 `USE_DRIVE=True`로 설정하면 위 경로에 폴더가 생성되고 데이터가 저장됩니다.

## 주의

- `kaggle.json`(API 토큰)은 개인 정보입니다. 절대 버전관리(Git)에 올리지 마세요.
- Kaggle 이용약관을 준수하고, 대회 규칙에 따라 데이터를 사용하세요.
