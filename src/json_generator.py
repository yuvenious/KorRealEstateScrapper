import json
import pandas as pd

sido_list = ['서울특별시', '경기도', '인천광역시', '부산광역시', '대전광역시']
apt_code_path = '../stat/aptCode.json'
admin_code_path = '../stat/adminCode.json'

with open('../stat/sidoSigunguCode.json', 'r') as f:
    locs_dict = json.load(f)
locs_dict_r = {}
for sido, v in locs_dict.items():
    for sigungu, code in v.items():
        locs_dict_r[code] = ('', '')
        locs_dict_r[code] = sido, sigungu

def get_output_table_path(sido):
    return '../output/db/output_{}.txt'.format(sido)

adminCode = {}
aptCode = {}

for sido in sido_list:
    adminCode[sido] = {}
    output_filepath = get_output_table_path(sido)
    df = pd.read_csv(output_filepath, sep=';', na_filter=False)

    df["시도명"] = df["지역코드"].astype(str).map(locs_dict_r).apply(lambda x: x[0])
    df["시군구명"] = df["지역코드"].astype(str).map(locs_dict_r).apply(lambda x: x[1])
    df['법정동읍면동코드'] = df['지역코드'].astype(str) + df['법정동읍면동코드'].astype(str)

    sigungus = sorted(df["시군구명"].unique())
    for sigungu in sigungus:
        adminCode[sido].update({sigungu:{}})
        for i, group in df[df['시군구명'] == sigungu].groupby(['법정동', '법정동읍면동코드']):
            adminCode[sido][sigungu].update({i[0]: str(i[1])})

    for i, group in df.groupby(['시도명', '시군구명', '법정동읍면동코드']):
        aptCode[i[-1]] = sorted(group['아파트'].unique().tolist())

with open(admin_code_path, 'w') as f:
    json.dump(adminCode, f, separators=(",", ":"), indent=2, ensure_ascii=False)

with open(apt_code_path, 'w') as f:
    json.dump(aptCode, f, separators=(",", ":"), indent=2, ensure_ascii=False)