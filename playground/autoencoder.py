import torch
import pandas as pd
import xarray as xr
import numpy as np

# Load the entire model (architecture + weights)
model = torch.load('encoder.pth')

# Set the model to evaluation mode (important for inference)
model.eval()

# Step 1: Load your CSV data into a pandas DataFrame
df = pd.read_csv('sample_data/xa.s12.00.mhz.1970-01-19HR00_evid00002.csv')

ds = xr.Dataset(
    {
        'wave': (['relative_time'], df['velocity(m/s)'])  # Define 'wave' as a variable dependent on 'relative_time'
    },
    coords={
        'relative_time': (['relative_time'], df['time_rel(sec)']),  # Relative relative_time as a float or integer
    }
)

ds.to_netcdf('output_data.nc')

print("CSV data successfully converted to NetCDF format!")

file_path = 'output_data.nc'
data = xr.open_dataset(file_path)

df = pd.read_csv('sample_data/xa.s12.00.mhz.1970-01-19HR00_evid00002.csv')
relative_time = df['time_rel(sec)'].values
absolute_time = df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'].values

# Reshape the input data
input_data = data['wave'].values
input_data = input_data.reshape(-1, input_data.shape[-1])
input_data = torch.tensor(input_data).float()

# Process each channel separately
outputs = []
with torch.no_grad():
    for channel in input_data:
        channel_input = channel.unsqueeze(0)  # Add batch dimension
        channel_output = model(channel_input)
        outputs.append(channel_output.squeeze().numpy())
        
print('Done infering...')

output_data = np.array(outputs).T

min_length = min(len(relative_time), len(output_data))
absolute_time = absolute_time[:min_length]
relative_time = relative_time[:min_length]
print("relative_time", relative_time.shape)
output_data = output_data[:min_length, 0]
print("output_data", output_data.shape)

# Step 6: Combine the relative_time and output data into a pandas DataFrame
combined_df = pd.DataFrame({
    'time_abs(%Y-%m-%dT%H:%M:%S.%f)': absolute_time,
    'time_rel(sec)': relative_time,
    'velocity(m/s)': output_data.flatten()  # Use the first output channel (or modify if needed)
})

# Step 7: Save the DataFrame to a CSV file
combined_df.to_csv('output_data_with_time.csv', index=False)

print("Processing complete. You fucking did it.")
