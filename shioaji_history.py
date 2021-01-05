import os
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
import shioaji as sj
from datetime import datetime


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


def main(person_id, passwd):
    api = sj.Shioaji()
    login = api.login(
        person_id=person_id,
        passwd=passwd,
        contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done."),
    )

    code_table = stock_code()
    code_table = code_table[code_table.industry != ""]
    stock_list = pd.read_csv("stock_200.csv")
    code_table = code_table[~code_table.code.isin(stock_list.code)]
    date = datetime.now().strftime("%Y-%m-%d")
    for i in code_table.code.values:
        kbars = api.kbars(api.Contracts.Stocks[str(i)], start="2011-01-02", end=date)
        df = pd.DataFrame({**kbars})
        df.ts = pd.to_datetime(df.ts)
        df["code"] = i
        file_path = os.path.join(
            os.getenv("HOME"), "shiaoji_history", "{}.csv".format(i)
        )
        df.to_csv(file_path, index=False)
        print(i)
        time.sleep(10)


if __name__ == "__main__":
    ID = input("ID:")
    PSSWD = input("Password:")
    main(ID, PSSWD)
