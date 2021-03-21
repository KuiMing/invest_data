
import investpy
import pkg_resources
import pandas as pd
import argparse

def get_last_bond(country):

    bond_list = pd.read_csv(pkg_resources.resource_filename('investpy', '/'.join(('resources', 'bonds.csv'))))
    query_bond = bond_list[bond_list.country == country].name.values
    result = pd.DataFrame()
    for bond in query_bond:
        df = investpy.get_bond_recent_data(bond=bond)
        df.reset_index(inplace=True)
        df = df.tail(n=1)
        df['bond'] = bond
        result = result.append(df)
    return result

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--country", help="enter a country", type=str)
    args = parser.parse_args()
    country = args.country.lower()
    country.replace(' ', '-')
    country_bond = get_last_bond(country)
    country_bond.to_csv('investing/{}_bond.csv'.format(country), index=False, header=False, mode='a')

if __name__ == '__main__':
    main()
