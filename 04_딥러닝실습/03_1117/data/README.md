# 데이터 디렉토리 구성

이 폴더는 실습에 필요한 데이터 자산을 보관합니다. 대용량 원본 파일은 Git에 포함하지 않고, 메타데이터만 버전관리합니다.

## 구조

- `images/`: 이미지 파일 저장 위치 (Git에는 기본적으로 미추적)
- `extras/`: 추가 리소스(예: 사전, 체크포인트 등) 저장 위치 (미추적)
- `annotations.csv`: 주석/라벨 메타데이터 (예: 파일명, 라벨, split 등)
- `LICENSE.txt`: 데이터셋 라이선스 또는 출처 명시

## annotations.csv 스키마

- `image_id` 또는 `filename`: 실제 이미지 파일명
- `class`: 객체 클래스 이름
- `geometry`: 폴리곤 좌표 문자열 (`[(x1, y1), (x2, y2), ...]`)
- `split` (옵션): 데이터 분할 정보 (`train`/`val`/`test`)

노트북에서는 `geometry`를 자동으로 bounding box로 변환하고, `split`이 없으면 파일 단위로 무작위 분할을 생성합니다.

## 데이터 다운로드/동기화

- Colab 노트북 `colab_kaggle_setup.ipynb`에서 기본 저장 경로가 `data/`로 설정됩니다.
- Kaggle에서 받은 원본 파일은 `images/` 또는 하위 폴더로 정리하고, 필요한 경우 `annotations.csv`에 반영하세요.

## 주의

- 원본 데이터는 용량이 크므로 Git에 올리지 않습니다.
- Kaggle 약관 및 각 데이터셋 라이선스를 준수하세요.
