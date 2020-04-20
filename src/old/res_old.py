import os, itertools, json, urllib

import pandas as pd

import requests
import xmltodict

from tqdm import tqdm

class RealEstateScrapper(object):
    def __init__(self, city, loc_names, start_ym, end_ym, api_keys, output_filename):

        # URL 및 API KEY지정
        self.call_back_url = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
        self.api_keys = api_keys
        self.api_key = next(self.api_keys)

        # 기저장된 데이터 불러오기
        if 'archive' not in os.listdir('.'):
            os.mkdir('./archive')
        if 'archive.json' in os.listdir('./archive'):
            with open('./archive/archive.json', 'r') as fp:
                self.archive = json.load(fp)
        else:
            print('create new dictionary')
            self.archive = dict()

        # 지역코드 사전 불러오기
        f = open('./params/code.txt', 'r', encoding='utf-8')
        s = f.read().strip('\n')
        json_acceptable_string = s.replace("'", "\"")
        locs_dict = json.loads(json_acceptable_string)

        self.locs_dict_r = {}
        for v in locs_dict.values():
            for k, v in v.items():
                self.locs_dict_r[v] = k

        # 행정코드
        if loc_names:
            self.locs = []
            for loc_name in loc_names:
                self.locs.append(locs_dict[city][loc_name])
        else:
            self.locs = list(locs_dict[city].values())

        # 연월
        start = str(start_ym)[:4], int(str(start_ym)[4:])
        end = str(end_ym)[:4], int(str(end_ym)[4:])

        if start[0] == end[0]:
            self.yms = [start[0]+'{:02}'.format(m) for m in range(start[1], end[1]+1)]
        else:
            yms = [start[0]+'{:02}'.format(m) for m in range(start[1], 13)]+[end[0]+'{:02}'.format(m) for m in range(1, end[1]+1)]
            self.yms = sorted(yms)

        self.output_filename = output_filename

        self.scrap()

    def scrap(self):
        self.n_iter = 0
        for loc, ym in itertools.product(self.locs, self.yms):
            print(self.locs_dict_r[loc], ym)
            # 첫 요청
            page = 1
            req_params = loc, ym, page
            xmlstring = self.get_xmlstring(req_params)
            xmldict = xmltodict.parse(xmlstring)['response']['body']
            # 몇번 더 요청해야하는지?
            count = int(xmldict['totalCount'])
            print('total count: %d'%count)
            n_req = count//10
            if count%10 == 0:
                n_req -= 1
            # 추가 요청
            for i in range(n_req):
                page += 1
                req_params = loc, ym, page
                xmlstring = self.get_xmlstring(req_params)


    def get_xmlstring(self, req_params):
        if str(req_params) in self.archive:
            print(req_params, ':already have')
            xmlstring = self.archive[str(req_params)]
        else:
            print(req_params, ':need to request')
            xmlstring = self.get_resp(req_params)
            self.archive[str(req_params)] = xmlstring
            with open('./archive/archive.json', 'w') as fp:
                json.dump(self.archive, fp)
        self.n_iter += 1
        # if self.n_iter%1000 == 0:
        #     print(self.n_iter)
        return xmlstring

    def get_resp(self, req_params):
        params = dict(zip(['LAWD_CD', 'DEAL_YMD', 'pageNo'], req_params))

        validity_checked = False
        while not validity_checked:
            params.update({'serviceKey':urllib.parse.unquote(self.api_key)})
            resp = requests.get(self.call_back_url, params)
            xmlstring = resp.content.decode('UTF-8')
            if "LIMITED NUMBER OF SERVICE REQUESTS EXCEEDS ERROR" in xmlstring:
                with open('./archive/archive.json', 'w') as fp:
                    json.dump(self.archive, fp)
                print('Update API KEYS from %s'%self.api_key)
                try:
                    self.api_key = next(self.api_keys)
                    print('Update API KEYS to %s'%self.api_key)
                except:
                    print('All API KEYs are exhausted, start exporting.')
                    # self.export()
                    print('Data exported in csv format.')
                    raise Exception("Program terminated due to API keys exhaustion.")
            elif 'SERVICE KEY IS NOT REGISTERED ERROR' in xmlstring:
                self.error_xmlstring = xmlstring
                raise Exception("Service Key is not registered")
            else:
                validity_checked = True

        return xmlstring

    def export(self):
        filepath = './archive/%s.csv'%self.output_filename
        header = open('./params/header.txt', 'r', encoding='utf-8').readline()

        with open('./archive/archive.json', 'r') as fp:
            archive = json.load(fp)

        f = open(filepath, 'w', encoding='utf-8')
        print(header, file=f)
        for params, xmlstring in tqdm(archive.items()):
            xmldict = xmltodict.parse(xmlstring)['response']['body']['items']['item']
            if len(xmldict) > 10:
                row = ';'.join([v for k, v in xmldict.items() if k in header])
                print(row, file=f)
            else:
                for item in xmldict:
                    row = ';'.join([v for k, v in item.items() if k in header])
                    print(row, file=f)
        f.close()
