import os, re, json
import pandas as pd
from tqdm import tqdm
import pymysql

def main():
    global aptCode
    sido_list = ['서울특별시', '경기도', '인천광역시', '부산광역시', '대전광역시']
    with open('../stat/aptCode.json', 'r') as f:
        aptCode = json.load(f)
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='zmfpaapd1',
                                 db='KorRealEstate')

    cursor = connection.cursor()
    for sido in sido_list:
        print(sido)
        df = get_cleaned_df(sido)
        for vals in tqdm(df.itertuples(index=False)):
            insert_query = 'INSERT INTO aptprice (년, 월, 일, 거래금액, 전용평수, 코드, 법정동, 아파트, 아파트번호, 건축년도) '
            insert_query += 'VALUES ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(*vals)
            try:
                cursor.execute(insert_query)
            except Exception as e:
                print(e)
                raise

    connection.commit()

def get_apt_index(x):
    global aptCode
    return aptCode[x[0]].index(x[1])

def get_cleaned_df(sido):
    print('Start cleaning the original dataframe...')
    filepath = os.path.join('../output/db', 'output_{}.txt'.format(sido))
    df = pd.read_csv(filepath, sep=';')
    df = df[['년', '월', '일', '거래금액', '전용면적', '법정동', '아파트', '건축년도', '법정동시군구코드', '법정동읍면동코드']]
    if df.isnull().sum().sum() != 0:
        raise

    df['거래금액'] = df['거래금액'].apply(lambda x: int(re.sub(',', '', x)))
    df['전용면적'] = (df['전용면적']/3.3).round().astype(int)
    df.rename({'전용면적': '전용평수'}, axis=1, inplace=True)
    df['코드'] = df['법정동시군구코드'].astype(str) + df['법정동읍면동코드'].astype(str)

    df['아파트번호'] = df[['코드', '아파트']].apply(lambda x: get_apt_index(x), axis=1)
    df = df[['년', '월', '일', '거래금액', '전용평수', '코드', '법정동', '아파트', '아파트번호', '건축년도']]
    df = df.sort_values(['년', '월', '일', '법정동', '아파트']).reset_index(drop=True)
    print('Finished cleaning.')
    return df

if __name__ == "__main__":
    main()