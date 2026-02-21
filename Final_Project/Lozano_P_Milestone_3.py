import pandas as pd

import requests

# URL to scrape
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

# 
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/144.0 Safari/537.36'
}

response = requests.get(url, headers=headers, timeout=30) # Passing timeout to avoid hanging
response.raise_for_status()  # raises a HTTPError if blocked or offline

# Converting response content to text for pandas
html = response.text

# Using 'lxml' parser to read HTML tables
tables = pd.read_html(html, flavor='lxml')

df_wiki = tables[0]

df_wiki = df_wiki.rename(columns={'Symbol': 'Ticker', 'Security': 'Company', 'GICS Sector': 'Industry'})

cols_to_drop = ['CIK', 'Date first added', 'Founded']

# Dropping unnecessary columns from the Wikipedia DataFrame ignoring errors if columns are missing
df_wiki = df_wiki.drop(columns=cols_to_drop, errors='ignore')

df_wiki['Ticker'] = df_wiki['Ticker'].str.replace('.', '-', regex=False)

df_wiki[['City', 'State']] = df_wiki['Headquarters Location'].str.split(', ', n=1, expand=True)

df_wiki = df_wiki.drop_duplicates(subset=['Ticker'])

if __name__ == "__main__":
    print("This file is being run directly.")
    print(df_wiki.head())