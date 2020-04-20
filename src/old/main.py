from res import RealEstateScrapper

api_keys = iter([
    # Naver (drakane)
    # "wCNa%2FMBnfJIeZDVFlzEJo%2F%2FphsLnOKjvk0tS%2FxDHXnw95QZ87nbgtr7i3okgYlaZqGiHgVKfuMpruC8NPEQ1Iw%3D%3D",
    "%2BMU8%2FJTCgZ%2BCwG%2FpuO3KiZcbpAEFvfjCA9hHAJ6fobm7Wrt1Ar%2BlroFUuZoqd%2B3uz2otc4OEUEZk4H4w5kNP8w%3D%3D",
    # Gmail (yuvenious)
    # "yh5d7u8tLTrzl5kw8vDHvRLugGIjEsJ5j6SOhRnXma1%2F2IvWtUzc%2BhxmVtDFw1SRW2lREd%2BPZNpgUWmG6LI6yg%3D%3D",
    # # Daum (drakane85)
    # "a%2FvRarhLAb3kwKJfKtz5XA6HR1%2F4EtTBwD%2Bp42sznlZzxhKZu1Uk0EyN34vJYIvGZLDagtqGxvmEk5yj8hR5Kw%3D%3D",
    # # mySNU (drakane8)
    # "kpCf4%2B86hQm%2FFEFGoCZVysiA4dy60JFu4YnrxKpTW6JEd4MC0Q3er91tMAvgvL2zcAqxUxsStIFmWj9y0NU8oQ%3D%3D",
])

def main():
    city = '서울특별시'
    loc_names = None # 모든 지역구를 하고 싶다면 loc_names = None
    start_ym, end_ym = 201701, 201712 # 수집을 원하는 시작/종료 지점을 YYYYMM 형태로 입력
    output_filename = 'output' # archive directory가 자동 생성된 후, 확장자 csv 테이블형 자료가 저장됨

    res = RealEstateScrapper(city, loc_names, start_ym, end_ym, api_keys, output_filename)

    # res.export()
if __name__ == '__main__':

    main()
