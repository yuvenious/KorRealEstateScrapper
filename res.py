import re, os, datetime, itertools, json, urllib

import numpy as np
import pandas as pd

import requests
import xmltodict

# 지역코드 사전 불러오기
f = open('./params/code.txt', 'r', encoding='utf-8')
s = f.read()
exec('locs_dict=%s'%s, )

class RealEstateScrapper(object):
    def __init__(self, city, loc_names, start_ym, end_ym, api_key, output_filename):
        self.call_back_url = "http://openapi.molit.go.kr/OpenAPI_ToolInstallPackage/service/rest/RTMSOBJSvc/getRTMSDataSvcAptTradeDev"
        self.api_key = api_key

        # 하루 요청횟수 제한값
        self.req_limit = 1000

        # 기저장된 데이터 불러오기
        if 'archive' not in os.listdir():
            os.mkdir('./archive')
        if 'archive.npy' in os.listdir('./archive'):
            self.archive = np.load("./archive/archive.npy").item()
        else:
            self.archive = dict()

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

        self.scrap()
        self.export(output_filename)

    def scrap(self):
        for loc, ym in itertools.product(self.locs, self.yms):
            # 첫 요청
            page = 1
            req_params = loc, ym, page
            xmlstring = self.get_xmlstring(req_params)
            xmldict = xmltodict.parse(xmlstring)['response']['body']
            # 몇번 더 요청해야하는지?
            count = int(xmldict['totalCount'])
            n_req = count//10
            if count%10 == 0:
                n_req -= 1
            # 추가 요청
            for i in range(n_req):
                page += 1
                req_params = loc, ym, page
                xmlstring = self.get_xmlstring(req_params)

    def export(self, output_filename):
        filepath = './archive/%s.csv'%output_filename
        header = open('./params/header.txt', 'r', encoding='utf-8').readline()
        archive = np.load("./archive/archive.npy").item()
        f = open(filepath, 'w', encoding='utf-8')
        print(header, file=f)
        for params, xmlstring in archive.items():
            xmldict = xmltodict.parse(xmlstring)['response']['body']['items']['item']
            if len(xmldict) > 10:
                row = ';'.join([v for k, v in xmldict.items() if k in header])
                print(row, file=f)
            else:
                for item in xmldict:
                    row = ';'.join([v for k, v in item.items() if k in header])
                    print(row, file=f)
        f.close()

    def get_xmlstring(self, req_params):
        if req_params in self.archive:
            print(req_params, ':already have')
            xmlstring = self.archive[req_params]
        else:
            print(req_params, ':need to request')
            xmlstring = self.get_resp(req_params)
            self.archive[req_params] = xmlstring
            np.save("./archive/archive.npy", self.archive)
        return xmlstring

    def get_resp(self, req_params):
        params = dict(zip(['LAWD_CD', 'DEAL_YMD', 'pageNo'], req_params))
        params.update({'serviceKey':urllib.parse.unquote(self.api_key)})
        resp = requests.get(self.call_back_url, params)
        xmlstring = resp.content.decode('UTF-8')
        if "LIMITED NUMBER OF SERVICE REQUESTS EXCEEDS ERROR" in xmlstring:
            np.save("./archive/archive.npy", self.archive)
            raise Exception("try tomorrow")
        elif 'SERVICE KEY IS NOT REGISTERED ERROR' in xmlstring:
            raise Exception("Service Key is not registered")
        return xmlstring
