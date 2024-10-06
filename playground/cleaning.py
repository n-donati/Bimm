import pandas as pd
import numpy as np

df = pd.read_csv('data/playground/data/xa.s12.00.mhz.1970-01-19HR00_evid00002.csv')

df['column_name'] = pd.to_numeric(df['column_name'], errors='coerce')

# Step 2: Fill null values in 'time_rel(sec)' and 'velocity(m/s)' columns with the previous row's value
df['time_rel(sec)'] = df['time_rel(sec)'].fillna(method='ffill')
df['velocity(m/s)'] = df['velocity(m/s)'].fillna(method='ffill')

# Drop still null values (if any)
df_cleaned = df.dropna()

# Save the cleaned DataFrame to a new CSV
df_cleaned.to_csv('cleaned_data.csv', index=False)


