from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from datetime import datetime
import pandas as pd

app = FastAPI()

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'ALL:@SECLEVEL=1'


def get_ipo_elements(page_no):
    url = 'https://www.38.co.kr/html/fund/index.htm?o=nw&page={}'.format(page_no)
    html = requests.get(url, verify=False).text
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup('table')
    table_ipo_list = list(filter(lambda x: x.attrs.get('summary') == '신규상장종목', tables))[0]

    head = table_ipo_list('thead')[0]
    th = head('tr')[0]('th')
    column_headers = [x.text for x in th]

    result = []
    tbody = table_ipo_list('tbody')[0]
    rows = tbody('tr')
    for row in rows:
        td = row('td')
        info = OrderedDict()
        for i, e in enumerate(td):
            header_text = column_headers[i]
            if len(header_text) == 0:
                continue
            temp = e.text.replace('\xa0', '')
            temp = temp.replace('%', '')
            if header_text in ['공모가(원)', '시초가(원)', '첫날종가(원)', '현재가(원)']:
                if temp in ['-', '예정', '상장']:
                    info[header_text] = ''
                else:
                    info[header_text] = int(temp.replace(',', ''))
            elif header_text in ['공모가대비등락률(%)', '시초/공모(%)', '전일비(%)']:
                if temp in ['-'] or len(temp) == 0:
                    info[header_text] = ''
                else:
                    info[header_text] = float(temp)
            elif header_text in ['신규상장일']:
                info[header_text] = datetime.strptime(e.text, '%Y/%m/%d')
            elif header_text in ['기업명']:
                info[header_text] = temp.replace('(유가)', '')
            else:
                info[header_text] = e.text
        result.append(info)
    return result


def get_all_ipo_list(year: int) -> pd.DataFrame:
    result = list()


@app.get("/")
async def root():
    print(get_ipo_elements(1))
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
