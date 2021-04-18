
import investpy
import pkg_resources
import pandas as pd
import argparse
import time
import random

def get_last_etf(keyword, country='united states'):
    metal = ['Gold', 'Silver', 'Copper', 'Metal']
    etf = pd.DataFrame(investpy.get_etfs_dict())
    if keyword == 'Energy':
        temp = etf[etf.full_name.str.contains(keyword)]
        temp = temp.append(etf[etf.full_name.str.contains('Oil')])
    elif keyword == 'Metal':
        temp = pd.DataFrame()
        for i in metal:
            temp = temp.append(etf[etf.full_name.str.contains(i)])
        temp.drop_duplicates(inplace=True)
    elif keyword == 'commodity':
        temp = etf[etf.asset_class == keyword]
        metal.append('Oil')
        for i in metal:
            temp = temp.append(etf[~etf.full_name.str.contains(i)])
    else:
        temp = etf[etf.asset_class == keyword]
    temp = temp[temp.country == country]
    history = pd.DataFrame()
    for i in temp.name.values:
        try:
            print(i)
            data = investpy.get_etf_recent_data(
                i, country=country)
            data.reset_index(inplace=True)
            data['name'] = i
            history = history.append(data.tail(1))
            time.sleep(random.choice(list(range(5, 16))))
        except:
            pass
    return history

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--country", help="enter a country", type=str, default='united states')
    parser.add_argument("-k", "--keyword", help="keyword of etf", type=str)
    args = parser.parse_args()
    keyword = args.keyword.lower()
    country = args.country.lower()
    etf = get_last_etf(keyword, country)
    etf.to_csv('investing/etf_{}.csv'.format(keyword), index=False, header=False, mode='a')

if __name__ == '__main__':
    main()
