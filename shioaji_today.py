import os
import glob
from datetime import datetime
import time
import pandas as pd
import shioaji as sj
from shioaji_history import stock_code, login_info


def main(person_id, passwd):
    api = sj.Shioaji()
    api.login(
        person_id=person_id,
        passwd=passwd,
        contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done."),
    )

    code_table = stock_code()
    code_table = code_table[code_table.industry != ""]
    today = datetime.now().strftime("%Y-%m-%d")
    files = glob.glob("/Users/ben/shioaji_history/*.csv")
    exist_code = []
    for i in files:
        exist_code.append(i.split("/")[-1].split(".")[0])
    for i in code_table.code.values:
        try:
            kbars = api.kbars(api.Contracts.Stocks[str(i)], start=today, end=today)
            data_frame = pd.DataFrame({**kbars})
            data_frame.ts = pd.to_datetime(data_frame.ts)
            dates = []
            times = []
            for t_s in data_frame.ts.values:
                dates.append(str(t_s).split("T")[0])
                times.append(str(t_s).split("T")[1].split(".")[0])
            data_frame["Date"] = dates
            data_frame["Time"] = times
            data_frame = data_frame[
                ["Date", "Time", "Open", "High", "Low", "Close", "Volume"]
            ]
            file_path = os.path.join(
                os.getenv("HOME"), "shioaji_history", "{}.csv".format(i)
            )
            if len(set([i]) - set(exist_code)) > 0:
                data_frame.to_csv(file_path, index=False)
            else:
                data_frame.to_csv(file_path, index=False, mode="a", header=False)
        except:
            print(i)
        time.sleep(10)
    api.logout()


if __name__ == "__main__":
    ID, PASSWD = login_info()
    main(ID, PASSWD)
