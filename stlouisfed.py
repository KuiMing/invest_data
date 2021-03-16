import requests
import wget
import os
from lxml import etree
import pandas as pd
import glob
from datetime import datetime
import argparse

def stlouisfed(url="https://fred.stlouisfed.org/graph/?g=puCo"):
    try:
        os.remove('fredgraph.zip')
    except:
        pass

    try:
        os.remove('fredgraph.csv')
    except:
        pass

    try:
        os.system('rm -r /fed')
    except:
        pass
        

    response = requests.request("GET", url)
    html = etree.HTML(response.content)
    temp = html.xpath("//div/div/a/span[@class='fred-notes-title']")
    index = []
    for i in temp:
        index.append(i.text.replace('\xa0', ''))

    temp = html.xpath("//div/div/a/span[@class='text-muted smaller-80']")    
    code = []
    for i in temp:
        code.append(i.text[1:-1])
    file_name = wget.download('https://fred.stlouisfed.org/graph/fredgraph.csv?id={}'.format(','.join(code)))
    code_index = pd.DataFrame({"variable":code, "index":index})

    if file_name[-3:] == "csv":
        data = pd.read_csv(file_name)
        data = pd.melt(data, id_vars='DATE', value_vars=data.columns[1:])
    elif file_name[-3:] == "zip":
        os.system('unzip fredgraph.zip -d /fed')
        files = glob.glob("/fed/*.csv")
        data = pd.DataFrame()
        for i in files:
            temp_df = pd.read_csv(i)
            temp_df = pd.melt(temp_df, id_vars='DATE', value_vars=temp_df.columns[1:])
            data = data.append(temp_df)
            os.remove(i)
        os.system('rm -r /fed')

    data = data.merge(code_index, on='variable')
    data.to_csv('stlouisfed/fed_{}.csv'.format(url.split("g=")[1]))  
    os.remove(file_name)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--id", help="graph ID of data from https://fred.stlouisfed.org/", type=str)
    args = parser.parse_args()
    url = "https://fred.stlouisfed.org/graph/?g={}".format(args.id)
    stlouisfed(url)
    
    
if __name__ == "__main__":
    main()
