# import re, json
# import pandas as pd
# from tqdm import tqdm
#
# with open('../stat/sidoSigunguCode.json', 'r') as f:
#     locs_dict = json.load(f)
#
# locs_dict_r = {}
# for sido, v in locs_dict.items():
#     for sigungu, code in v.items():
#         locs_dict_r[code] = ('', '')
#         locs_dict_r[code] = sido, sigungu
#
# output_header_string = open('../stat/header.txt', 'r', encoding='utf-8').readline()
# output_header_list = output_header_string.split(';')
#
# for sido in ['서울특별시', '경기도', '인천광역시', '부산광역시']:
#     with open('../archive/archive_modified_{}.json'.format(sido)) as f:
#         archive = json.load(f)
#     print(sido, len(archive))
#
#     output_filepath = '../output/db/output_{}.txt'.format(sido)
#     output_file = open(output_filepath, 'w', encoding='utf-8-sig')
#     print(output_header_string, file=output_file)
#
#     for k, v in tqdm(archive.items()):
#         if v['response']['body']['items']:            data = v['response']['body']['items']['item']
#             for deal in data:
#                 deal['거래금액'] = str(round(int(re.sub(',', '', deal['거래금액']))/10000, 2))
#                 deal['시도명'] = locs_dict_r[deal['지역코드']][0]
#                 deal['시군구명'] = locs_dict_r[deal['지역코드']][1]
#                 deal['전용면적'] = str(round(float(deal['전용면적']), 1))
#                 deal['전용평수'] = str(round(float(deal['전용면적']) / 3.3))
#                 if "," in deal['아파트']:
#                     deal['아파트'] = re.sub(',', '.', deal['아파트'])
#                 deal['거래일'] = '{}-{:02}-{:02}'.format(*[int(deal[k]) for k in deal if k in ["년", "월", "일"]])
#                 row = [deal[k] if k in deal and deal[k] else '' for k in output_header_list]
#                 print(';'.join(row), file=output_file)
#         else:
#             pass
#     output_file.close()
#     df = pd.read_csv(output_filepath, sep=';', na_filter=False)
#     df.sort_values(['법정동', '아파트', '거래일', '거래금액']).reset_index(drop=True).to_csv(output_filepath, sep=';', index=False, encoding='utf-8')