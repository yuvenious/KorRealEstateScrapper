import re, os, itertools, json, urllib, time
import pandas as pd
import xmltodict, requests
from tqdm import tqdm

def main():
    scrapper = Scrapper()
    start_ym = 201001
    end_ym = 202002
    sido_list = ['서울특별시', '경기도', '인천광역시', '부산광역시', '대전광역시']
    sigungu = None

    for sido in sido_list[:]:
        scrapper.setup(start_ym, end_ym, sido, sigungu)
        scrapper.scrap()

class Scrapper(object):
    def __init__(self, service_key_path='../stat/apikey'):
        self._service_key = open(service_key_path, 'r').readline()
        self._call_back_url = open('../stat/callbackURL', 'r').readline()

        self._query_string_fields = ['LAWD_CD', 'DEAL_YMD', 'pageNo', 'numOfRows']
        self._set_init_query_string_params()

    def _set_init_query_string_params(self):
        self._query_string_params = {k:'' for k in self._query_string_fields}
        self._query_string_params['serviceKey'] = urllib.parse.unquote(self._service_key)

    def _get_LAWD_CD(self, sido, sigungu):
        #LAWD_CD
        with open('../stat/sidoSigunguCode.json', 'r') as f:
            locs_dict = json.load(f)
        if sigungu:
            locs = []
            for loc_string in sigungu:
                locs.append(locs_dict[sido][loc_string])
        else:
            locs = locs_dict[sido].values()
        return sorted(locs)

    def _get_DEAL_YMD(self, start_ym, end_ym):
        #DEAL_YMD
        start = str(start_ym)[:4], int(str(start_ym)[4:])
        end = str(end_ym)[:4], int(str(end_ym)[4:])
        if start[0] == end[0]:
            yms = [start[0]+'{:02}'.format(m) for m in range(start[1], end[1]+1)]
        else:
            yms = [start[0]+'{:02}'.format(m) for m in range(start[1], 13)]
            for year in range(int(start[0])+1, int(end[0])):
                yms += [str(year)+'{:02}'.format(m) for m in range(1, 13)]
            yms += [end[0]+'{:02}'.format(m) for m in range(1, end[1]+1)]
            yms = sorted(yms)
        return yms

    def setup(self, start_ym, end_ym, sido, sigungu):

        self._scrap_iterator = itertools.product(self._get_LAWD_CD(sido, sigungu), self._get_DEAL_YMD(start_ym, end_ym))
        self.archive_filepath = '../archive/archive_{}.json'.format(sido)
        if os.path.exists(self.archive_filepath):
            print('Loading archive for {}...'.format(sido))
            with open(self.archive_filepath, 'r') as fp:
                self.archive = json.load(fp)
            print('Loaded.')

        else:
            print('There is no archived data yet. Create a new one')
            self.archive = {}

    def _update_query_string_params(self, key, nrows):
        loc, ym = eval(key)
        query_string_vals = loc, ym, 1, nrows
        print(query_string_vals)
        self._query_string_params.update(dict(zip(self._query_string_fields, query_string_vals)))

    def _archive(self):
        print('start archiving')
        s = time.time()
        with open(self.archive_filepath, 'w') as fp:
            json.dump(self.archive, fp, separators=(",", ":"), indent=2, ensure_ascii=False)
        e = time.time()
        print('archived in %.2fsec'%(e-s))

    def scrap(self):
        for i, (loc, ym) in enumerate(self._scrap_iterator):
            key = str((loc, ym))
            self._collect(key)
        # self._archive()

    def _collect(self, key):
        if key not in self.archive:
            raise
            print('{} data should be requested.'.format(key))
            xml = self._API_request(key)
            json = xmltodict.parse(xml, dict_constructor=dict)
            self.archive[key] = json
        else:
            print('{} data is already archived.'.format(key))

    def _request_norm(self, key, nrows):
        self._update_query_string_params(key, nrows)
        xml = requests.get(self._call_back_url, self._query_string_params).content.decode('utf-8')
        result_code = re.search('<resultCode>(.*?)</resultCode>', xml).group(1)
        if result_code != '00':
            self._archive()
            raise ValueError(re.search('<resultMsg >(.*?)</resultMsg >', xml).group(1))
        return xml

    def _API_request(self, key):
        try:
            # request only to check total count
            xml = self._request_norm(key, nrows=0)
            total_count = re.search('<totalCount>(.*?)</totalCount>', xml).group(1)
            print(key, ":", total_count)
            # request the full data
            xml = self._request_norm(key, nrows=total_count)
        except:
            print('Request/Respons error occurs in '+key)
            self._archive()
            print('sleep for 5 seconds')
            time.sleep(5)
            print('do it again')
            xml = self._API_request(key)
        return xml

if __name__ == "__main__":
    main()