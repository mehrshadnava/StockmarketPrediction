#!/usr/bin/env python3.12

import mysql.connector # type: ignore
from mysql.connector import Error # type: ignore
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Define output CSV file path
OUTPUT_CSV = "delivery_traded_ratio_analysis_data.csv"

try:
    # Connect to MySQL
    connection = mysql.connector.connect(
        host='localhost',
        user='sa',
        password='laser4050',
        database='CHANAKYA'
    )

    if connection.is_connected():
        print("Connected to MySQL database")

        query = """
        SELECT
            BH_SYMBOL,BH_OPEN, BH_HIGH, BH_LOW, BH_CLOSE,
            BH_TIMESTAMP, DEL_QTY, TRADED_QTY, DEL_TRADED_RATIO 
        FROM NSE_CM_BHAVCOPY
        WHERE BH_SERIES='EQ'
        """
        df = pd.read_sql(query, con=connection)
        print("Data fetched from MySQL")

        # Convert and sort by timestamp and symbol
        df['BH_TIMESTAMP'] = pd.to_datetime(df['BH_TIMESTAMP'])
        df.sort_values(['BH_TIMESTAMP'], inplace=True)
        print("Timestamp converted")

        # Price change calculations
        df['Price_Change_Daily'] = df['BH_CLOSE'] - df['BH_CLOSE'].shift(1)
        df['Price_Change_3Days'] = df['BH_CLOSE'] - df['BH_CLOSE'].shift(3)
        df['Price_Change_5Days'] = df['BH_CLOSE'] - df['BH_CLOSE'].shift(5)
        df['Price_Change_7Days'] = df['BH_CLOSE'] - df['BH_CLOSE'].shift(7)
        df['Price_Change_10Days'] = df['BH_CLOSE'] - df['BH_CLOSE'].shift(10)
        print("Price changes calculated")

        # Calculate returns
        df['Returns_Daily'] = (df['BH_CLOSE']-df['BH_OPEN'])/df['BH_OPEN']
        df['Returns_Day3'] = (df['BH_CLOSE'].shift(3)-df['BH_OPEN'].shift(3))/df['BH_OPEN'].shift(3)
        df['Returns_Day5'] = (df['BH_CLOSE'].shift(5)-df['BH_OPEN'].shift(5))/df['BH_OPEN'].shift(5)
        df['Returns_Day3'] = (df['BH_CLOSE'].shift(7)-df['BH_OPEN'].shift(7))/df['BH_OPEN'].shift(7)
        df['Returns_Day3'] = (df['BH_CLOSE'].shift(10)-df['BH_OPEN'].shift(10))/df['BH_OPEN'].shift(10)
        print("Returns calculated")

        # Delivery ratio features
        df['DTR'] = df['DEL_TRADED_RATIO']

        # DTR changes
        df['DTR_Change_Daily'] = df['DTR'].diff()
        df['DTR_Change_3Days'] = df['DTR'].diff(3)
        df['DTR_Change_5Days'] = df['DTR'].diff(5)
        df['DTR_Change_7Days'] = df['DTR'].diff(7)

        # DTR spikes using median
        df['DTR_Spike_3'] = df['DTR'] - df['DTR'].rolling(3).median()
        df['DTR_Spike_5'] = df['DTR'] - df['DTR'].rolling(5).median()
        df['DTR_Spike_7'] = df['DTR'] - df['DTR'].rolling(7).median()

        # DTR volatility and moving averages
        df['DTR_Volatility_3'] = df['DTR'].rolling(3).std()
        df['DTR_Volatility_5'] = df['DTR'].rolling(5).std()
        df['DTR_MA3'] = df['DTR'].rolling(3).mean()
        df['DTR_MA5'] = df['DTR'].rolling(5).mean()
        df['DTR_MA7'] = df['DTR'].rolling(7).mean()
        print("DTR features calculated")

        # Save to CSV
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"All processed data saved to {OUTPUT_CSV}")

except Error as e:
    print("Error while connecting to MySQL:", e)

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
        print("MySQL connection closed.")

