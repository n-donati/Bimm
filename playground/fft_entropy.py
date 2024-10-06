import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import entropy
from scipy.signal import welch

# Load CSV data without parsing dates
data = pd.read_csv("data/xa.s12.00.mhz.1970-01-19HR00_evid00002.csv")
data['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] = pd.to_datetime(data['time_abs(%Y-%m-%dT%H:%M:%S.%f)'])
# Convert datetime to seconds (relative to the first timestamp)
data['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] = (data['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] - data['time_abs(%Y-%m-%dT%H:%M:%S.%f)'].iloc[0]).dt.total_seconds()
# Extract the time and amplitude columns
time = data['time_abs(%Y-%m-%dT%H:%M:%S.%f)'].values  # Time in seconds
amplitude = data['velocity(m/s)'].values  # Amplitude (seismic data) column  (Assuming 'Sample' is the amplitude column)
print('done extracting')


# Determine the sampling rate? (assuming evenly spaced timestamps)
# sampling_rate = 16  # In Hz
sampling_rate = 1 / np.mean(np.diff(time))
print(f"sampling rate: {sampling_rate}")


# Compute power spectral density (PSD) using Welch's method
freqs, psd = welch(amplitude, fs=sampling_rate)

# Normalize the PSD
psd_norm = psd / np.sum(psd)

# Compute spectral entropy
spectral_entropy = entropy(psd_norm)

max_entropy = np.log(len(psd))

normalized_entropy = spectral_entropy / max_entropy

print(f"Spectral Entropy: {spectral_entropy}, Sending {normalized_entropy} frequencies")



# Raw data plot
plt.figure(figsize=(10, 4))
plt.plot(time, amplitude, label="Raw Data")
plt.title("Raw Seismic Data")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()

# make entropy determine 10% of the data kept
threshold_percentile = (100 - (normalized_entropy * 100)) * 0.1

# Perform FFT on the amplitude data
fft_result = np.fft.fft(amplitude)

# Frequencies corresponding to the FFT result
frequencies = np.fft.fftfreq(len(amplitude), 1 / sampling_rate)

threshold = np.percentile(np.abs(fft_result), threshold_percentile) # HACE FALTA ENTROPY
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