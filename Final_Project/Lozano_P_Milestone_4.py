import pandas as pd
import requests
import time
from Lozano_P_Milestone_3 import df_wiki # Importing the web scraped

# --- PRE-STEP: Define the Target List ---
# We only want to fetch stock data for companies that we have layoff data for.
# This saves time and API credits.

# Get unique tickers from your Wiki S&P 500 dataset
# (Assuming you loaded df_wiki from your previous milestone code)
sp500_tickers = df_wiki['Ticker'].unique()

# 3. Find the intersection (Companies in BOTH lists)
# This is our "Target List" for the API loop.
# target_tickers = list(set(sp500_tickers))

print(f"Fetching data for {len(sp500_tickers)} companies...")

# --- DATA EXTRACTION LOOP ---
# --- Premium API Key ---
api_key = "INSERT_API_KEY_HERE"
all_stock_data = []

# --- DATA EXTRACTION LOOP ---
for ticker in sp500_tickers:
    # Premium Call: We use 'outputsize=full' to get 20+ years of history.
    # This ensures we capture the exact dates of all layoffs (2020-2024).
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize=full&apikey={api_key}'
    
    try:
        r = requests.get(url)
        data = r.json()
        
        if "Time Series (Daily)" in data:
            # Convert the JSON dictionary to a DataFrame
            temp_df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
            
            # Transformation 1: Add Ticker Column to dataframe
            temp_df['Ticker'] = data['Meta Data']['2. Symbol']
            
            # Transformation 2: Reset index
            # Reset index to make Date a column
            temp_df = temp_df.reset_index().rename(columns={'index': 'Date'})
            
            # CRITICAL FILTER: Reduce Data Size
            # We convert to datetime immediately so we can filter.
            temp_df['Date'] = pd.to_datetime(temp_df['Date'])
            
            # We only keep data from 2020 onwards (covering the recent layoff waves).
            # This discards the 1990-2019 data we don't need.
            temp_df = temp_df[temp_df['Date'] >= '2020-03-11']
            
            all_stock_data.append(temp_df)
        else:
            print(f"Error for {ticker}: {data.get('Note', 'Unknown Error')}")
            
    except Exception as e:
        print(f"Failed for {ticker}: {e}")
        
    # RATE LIMIT: Premium allows much faster calls (e.g., 75/min). 
    # A tiny sleep ensures we don't accidentally hit the concurrency limit.
    time.sleep(0.5)

# --- MERGING & CLEANING ---
if all_stock_data:
    df_api = pd.concat(all_stock_data, ignore_index=True)

    # --- Transformation Step #3: Header Standardization ---
    # Alpha Vantage returns columns like '1. open', '2. high'.
    # We rename them to standard SQL-friendly names ('Open', 'High') and remove the numbers.
    df_api = df_api.rename(columns={
        '1. open': 'Open',
        '2. high': 'High',
        '3. low': 'Low',
        '4. close': 'Close',
        '5. volume': 'Volume'
    })

    # --- Transformation Step #4: Type Conversion & Date Filtering ---
    # 1. Convert columns to numeric (floats/ints) so we can do math.
    # 2. Convert Date to datetime objects.
    # 3. Filter for data > 2020. 'outputsize=full' returns data back to 1999.
    #    We drop the old data to keep our database size manageable and focused on the layoff era.
    cols_to_convert = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in cols_to_convert:
        df_api[col] = pd.to_numeric(df_api[col])
        
    df_api['Date'] = pd.to_datetime(df_api['Date'])
    
    # FILTER: Only keep data relevant to your project scope (2020-Present)
    df_api = df_api[df_api['Date'] >= '2020-11-01']

    # --- Transformation Step #5: Feature Engineering (Volatility) ---
    # We calculate 'Daily_Change_Pct' ((Close - Open) / Open).
    # This transformation creates a new metric to measure market reaction intensity
    # on the specific days layoffs were announced.
    df_api['Daily_Change_Pct'] = ((df_api['Close'] - df_api['Open']) / df_api['Open']) * 100
    
    print("Processing Complete.")
    print(f"Total Rows: {len(df_api)}")
    print(f"Date Range: {df_api['Date'].min()} to {df_api['Date'].max()}")
    print(df_api.head())

else:
    print("No data fetched. Check API key.")

# --- FINAL STEP: Write to File ---
if not df_api.empty:
    # Option A (Recommended): Save as Pickle (Keeps data types intact)
    df_api.to_pickle("Lozano_P_Milestone_4_Data.pkl")
    print("Success! Data saved to 'Lozano_P_Milestone_4_Data.pkl'")
    
    # Option B (If you really want CSV):
    # df_api.to_csv("Lozano_P_Milestone_4_Data.csv", index=False)
else:
    print("Dataframe is empty. Nothing to save.")