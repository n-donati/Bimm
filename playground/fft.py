import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Load CSV data without parsing dates
filename = "xa.s12.00.mhz.1970-01-19HR00_evid00002" # UPDATE DEPENDING ON FILE
data = pd.read_csv(f"data/{filename}.csv")

# Convert 'Time' column to datetime objects
data['Time'] = pd.to_datetime(data[f'time_abs(%Y-%m-%dT%H:%M:%S.%f)'])
data['Sample'] = data['velocity(m/s)']

# Convert datetime to seconds (relative to the first timestamp)
data['time_seconds'] = (data['Time'] - data['Time'].iloc[0]).dt.total_seconds()

# Extract the time and amplitude columns
time = data['time_seconds'].values  # Time in seconds
amplitude = data['Sample'].values  # Amplitude (seismic data) column  (Assuming 'Sample' is the amplitude column)

# Determine the sampling rate? (assuming evenly spaced timestamps)
sampling_rate = 16  # In Hz

# Plot the raw data (optional)
plt.figure(figsize=(10, 4))
plt.plot(time, amplitude, label="Raw Data")
plt.title("Raw Seismic Data")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()

# Perform FFT on the amplitude data
fft_result = np.fft.fft(amplitude)

# Frequencies corresponding to the FFT result
frequencies = np.fft.fftfreq(len(amplitude), 1 / sampling_rate)

threshold = np.percentile(np.abs(fft_result), 50) # HACE FALTA ENTROPY
positions = np.where(np.abs(fft_result) >= threshold)[0]

fft_result = fft_result[positions]
frequencies = frequencies[positions]

# Plot the FFT result (magnitude)
plt.figure(figsize=(10, 4))
plt.plot(frequencies[:len(frequencies)//2], np.abs(fft_result)[:len(frequencies)//2])
plt.title("FFT of Seismic Data")
plt.xlabel("Frequency (Hz)")
plt.ylabel("Magnitude")
plt.grid(True)
plt.show()

print(np.abs(fft_result)[0:10])

# Perform inverse FFT to reconstruct the signal
reconstructed_data = np.fft.ifft(fft_result)

# Plot the reconstructed signal
plt.figure(figsize=(10, 4))
plt.plot(reconstructed_data.real, label="Reconstructed Data", linestyle='dashed')
plt.title("Reconstructed Seismic Data (IFFT)")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()