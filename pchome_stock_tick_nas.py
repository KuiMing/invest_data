import os
import re
import time
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup


def stock_code():
    res = requests.get("https://isin.twse.com.tw/isin/C_public.jsp?strMode=2")
    soup = BeautifulSoup(res.content.decode("MS950"), "html.parser")
    table_rows = soup.find_all("tr")
    stock = []
    for tr in table_rows:
        td = tr.find_all("td")
        row = [tr.text for tr in td]
        stock.append(row)
    code_table = pd.DataFrame(
        stock[2:],
        columns=[
            "code_name",
            "ISINCode",
            "date",
            "market",
            "industry",
            "CFIcode",
            "note",
        ],
    )
    code_table.dropna(inplace=True)
    code = []
    name = []
    for i in code_table.code_name.values:
        code.append(i.split("\u3000")[0])
        name.append(i.split("\u3000")[1])
    code_table["code"] = code
    code_table["code"] = code_table.code.str.replace(" ", "")
    code_table["name"] = name
    return code_table


def pchome_stock_tick(code, date):
    url = "http://pchome.megatime.com.tw/stock/sto0/ock3/sid{}.html".format(code)
    ref = "http://pchome.megatime.com.tw/stock/sto0/ock2/sid{}.html".format(code)
    res = requests.get(url, headers={"Referer": ref})
    html = re.findall(
        "<table id=tb_chart cellpadding=0 cellspacing=1 style=margin-top:10px>.*</table>",
        res.text,
    )
    soup = BeautifulSoup(html[0], "html.parser")
    table = soup.find_all("td")
    data = []
    for i in table[7:]:
        data.append(i.text)
    data = np.array(data)
    col = ["time", "bid", "ask", "price", "change", "volume", "total_volume"]
    data = pd.DataFrame(data.reshape(int(len(data) / 7), 7), columns=col)
    for i in col[1:]:
        data.loc[data[i] == "--", i] = None
        data.loc[data[i] == "市價", i] = data.loc[data[i] == "市價", "price"]
        if i == "volume" or i == "total_volume":
            data[i] = data[i].astype(int)
        else:
            data[i] = data[i].astype(float)
    data["code"] = code
    data["date"] = date
    return data


def download_upload():
    code_table = stock_code()
    date = datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
    file_path = os.path.join(os.getenv("HOME"), "pchome", "pchome_{}.csv".format(date))
    count = 0
    big_table = pd.DataFrame()
    for i in code_table.code.values:
        print(i)
        try:
            data = pchome_stock_tick(i, date)
            big_table = big_table.append(data)
        except:
            print("something wrong")

        count += 1
        time.sleep(1)
        if count % 10 == 0:
            if count == 10:
                big_table.to_csv(file_path, index=False)
            else:
                big_table.to_csv(file_path, index=False, header=False, mode="a")
            big_table = pd.DataFrame()
        print(count)
    if len(big_table) > 0:
        big_table.to_csv(file_path, index=False, header=False, mode="a")


if __name__ == "__main__":
    download_upload()