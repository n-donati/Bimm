import pandas as pd
import numpy as np

df = pd.read_csv('data/iris.csv')
df_cleaned = df.dropna()

df['column_name'] = pd.to_numeric(df['column_name'], errors='coerce')
df_cleaned = df.dropna(subset=['column_name'])

