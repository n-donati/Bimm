import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from obspy import Stream, Trace, UTCDateTime, read

# Load CSV data without parsing dates
filename = "xa.s12.00.mhz.1970-01-19HR00_evid00002" # UPDATE DEPENDING ON FILE
data = pd.read_csv(f"{filename}.csv")

# Convert 'Time' column to datetime objects
data['Time'] = pd.to_datetime(data[f'time_abs(%Y-%m-%dT%H:%M:%S.%f)'])
data['Sample'] = data['velocity(m/s)']

# Convert datetime to seconds (relative to the first timestamp)
data['time_seconds'] = (data['Time'] - data['Time'].iloc[0]).dt.total_seconds()

# Extract the time and amplitude columns
time = data['time_seconds'].values  # Time in seconds
amplitude = data['Sample'].values  # Amplitude (seismic data) column  (Assuming 'Sample' is the amplitude column)

# Determine the sampling rate? (assuming evenly spaced timestamps)
sampling_rate = 1/(time[1]-time[0])  # In Hz

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

threshold = np.percentile(np.abs(fft_result), 80) # HACE FALTA ENTROPY
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

# x = np.arange(0, len(reconstructed_data.real), time[1]-time[0])

x = np.arange(time[0], time[len(time)-1], (time[len(time)-1]-time[0])/len(reconstructed_data.real))
scale_factor = np.max(data['Sample']) / np.max(reconstructed_data.real)
reconstructed_data.real *= scale_factor

# Plot the reconstructed signal
plt.figure(figsize=(10, 4))
plt.plot(x, reconstructed_data.real, label="Reconstructed Data", linestyle='dashed')
plt.title("Reconstructed Seismic Data (IFFT)")
plt.xlabel("Time (seconds)")
plt.ylabel("Amplitude")
plt.grid(True)
plt.show()

reconstructed_amplitude = reconstructed_data.real.astype(np.float32)

# Crea una traza para el miniSEED
trace = Trace(data=reconstructed_amplitude)  # Datos reconstruidos

# Agrega información de metadatos
trace.stats.network = 'XX'  # Código de red
trace.stats.station = 'ABC'  # Código de estación
trace.stats.location = ''    # Código de ubicación (opcional)
trace.stats.channel = 'BHZ'  # Canal (BHZ: vertical, alta ganancia)
trace.stats.starttime = UTCDateTime(data['Time'].iloc[0])  # Usar el primer timestamp es 0
trace.stats.sampling_rate = sampling_rate  # Usa la tasa de muestreo calculada previamente

# Crear un objeto Stream para guardar la Trace
st = Stream([trace])

# Guardar los datos reconstruidos como archivo miniSEED
output_filename = "output_reconstructed_data.mseed"
st.write(output_filename, format='MSEED')

print(f"Datos reconstruidos guardados en {output_filename}")

# Leer el archivo miniSEED generado
stream = read(output_filename)

# Obtener la primera traza del stream
trace = stream[0]

# Imprimir información básica de la traza
print(f"Datos guardados: {len(trace.data)} puntos de amplitud")

# Verificar que los datos coincidan
print(f"Primeros 10 datos de amplitud:\n{trace.data[:10]}")

# Graficar los datos para visualización
plt.figure(figsize=(10, 4))
plt.plot(trace.times(), trace.data, label="Datos del miniSEED reconstruidos")
plt.title("Datos del archivo miniSEED reconstruidos")
plt.xlabel("Tiempo (segundos)")
plt.ylabel("Amplitud")
plt.grid(True)
plt.show()