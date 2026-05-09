# EV Charge Finder

EV Charge Finder는 공공데이터포털 API를 활용하여 전기차 충전소 정보를 검색하고 지도에 표시하는 웹앱입니다.

## 프로젝트 주제

공공데이터포털 API 인증키를 활용한 전기차 충전소 검색 웹 개발

## 주요 기능

- 지역별 전기차 충전소 검색
- 충전소명 또는 주소 검색
- 충전기 상태 표시
- 충전기 타입 표시
- 지도에 충전소 위치 표시
- Python 버전 앱 제공

## 사용 API

한국환경공단 전기자동차 충전소 정보 API

## 파일 설명

- `EV_charge.html` : 지도 포함 웹앱
- `ev_charge.py` : Python 버전 앱
- `README.md` : 프로젝트 설명서

## 실행 방법

### HTML 버전

1. `index.html` 파일을 실행한다.
2. 지역을 선택한다.
3. 검색 버튼을 누른다.
4. 지도와 충전소 목록을 확인한다.

### Python 버전

터미널에서 다음 명령어를 입력한다.

```bash
python ev_charge_finder.py
