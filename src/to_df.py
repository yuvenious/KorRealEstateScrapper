import json
import pandas as pd
from tqdm import tqdm

def main():
    sido_list = ['서울특별시', '경기도', '인천광역시', '부산광역시', '대전광역시']
    for sido in sido_list:
        json_to_dataframe(sido)

def json_to_dataframe(sido):
    print('Loading {} archive...'.format(sido))
    with open('../archive/archive_{}.json'.format(sido)) as f:
        archive = json.load(f)
    print('Loaded.')

    output_filepath = '../output/db/output_{}.txt'.format(sido)
    output_file = open(output_filepath, 'w', encoding='utf-8-sig')

    # header
    header = open('../stat/header.txt', 'r').read()
    print(header, file=output_file)
    
    # field value
    for req, resp in tqdm(archive.items()):
        if int(resp['response']['body']['totalCount']) < 1:
            print(req, 'XML Response doesn\'t contain any data.')
        else:
            deals = resp['response']['body']['items']['item']
            deals_ssv_string = pd.DataFrame(deals)[header.split(';')].to_csv(index=False, header=None, sep=';')
            print(deals_ssv_string.strip('\n'), file=output_file)
    output_file.close()

if __name__ == "__main__":
    main()