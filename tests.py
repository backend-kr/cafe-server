from django.test import TestCase

# Create your tests here.
# FEP에서 주소만 넣엇 카페 정보 read
# FEP에서 return 받은값 cafe server에 저장

import requests
import time



naver_url = "http://localhost:8080/api/v1/cafe/naver/"
local_url = "http://localhost:8001/api/v1/cafe/"

def process_data(json_list=None):
    for items in json_list:
        time.sleep(1)
        requests.post(local_url, json=items)

params = {
    "caller": "pcweb",
    "query": "광화문",
    "page": "1",
    "type": "all",
    "recommandation": "true",
    "latitude": "37.6943312",
    "longitude": "126.764245",
    "display_count": 100,
    "lang": "ko"
}

# 첫 번째 요청을 보냅니다.
response = requests.post(naver_url, params=params)

if response.ok:

    total_page = (response.json()["total_count"] // params["display_count"]) + 1

    # 모든 페이지에서 데이터를 추출합니다.
    for page in range(1, total_page + 1):
        params["page"] = page
        response = requests.post(naver_url, params=params)
        if response.ok:
            process_data(json_list=response.json()["result"])
    print("Request finish")
else:
    print(f"Request failed: {response.status_code}")



