# KorRealEstateScrapper - 한국 부동산 실거래내역 웹 스크래퍼
Web crawler of Korean Real Estate (apartment) transaction data

본 파이썬 모듈은 data.go.kr에서 제공하는 web API를 활용하여 부동산 실거래내역을 일괄적으로 다운받아서 테이블 형태(csv)의 데이터로 저장하는 기능을 가지고 있습니다.

## How to use
```python
from res import *

api_key = 'DATA.GO.KR로부터 본인이 받은 API KEY' #개발용 계정은 일 1,000회 제한
city = '서울특별시'
loc_names = ['종로구'] # 모든 지역구를 하고 싶다면 loc_names = None
start_ym, end_ym = 201805, 201806 # 수집을 원하는 시작/종료 지점을 YYYYMM 형태로 입력
output_filename = 'output' # archive directory가 자동 생성된 후, 확장자 csv 테이블형 자료가 저장됨

res = RealEstateScrapper(city, loc_names, start_ym, end_ym, api_key, output_filename)
```
