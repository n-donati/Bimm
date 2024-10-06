from sedenoss.sedenoss.models import FaSNet_base
import torch
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('xa.s12.00.mhz.1970-01-19HR00_evid00002.csv')
relative_time = df['time_rel(sec)'].values
absolute_time = df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'].values

# Load the model
model = FaSNet_base()
state_dict = torch.load('trained_196.pt', map_location=torch.device('cpu'))
model.load_state_dict(state_dict, strict=False)
model.eval()

# Load and prepare the data
file_path = 'output_data.nc'
data = xr.open_dataset(file_path)
print(data)

# Reshape the input data
input_data = data['wave'].values
input_data = input_data.reshape(-1, input_data.shape[-1])
input_data = torch.tensor(input_data).float()

# Save the model's state_dict (weights) and architecture
# torch.save(model, 'encoder.pth')

# Process each channel separately
outputs = []
with torch.no_grad():
    for channel in input_data:
        channel_input = channel.unsqueeze(0)  # Add batch dimension
        channel_output = model(channel_input)
        outputs.append(channel_output.squeeze().numpy())
        
# print('Done infering...')

output_data = np.array(outputs).T


min_length = min(len(relative_time), len(output_data))
absolute_time = absolute_time[:min_length]
relative_time = relative_time[:min_length]
print("relative_time", relative_time.shape)
output_data = output_data[:min_length, 0]
print("output_data", output_data.shape)

combined_df = pd.DataFrame({
    'time_abs(%Y-%m-%dT%H:%M:%S.%f)': absolute_time,
    'time_rel(sec)': relative_time,
    'velocity(m/s)': output_data.flatten()  
})

print("Processing complete. Output saved to 'output_data_with_time.csv'.")


