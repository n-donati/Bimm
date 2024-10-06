import matplotlib.pyplot as plt
from obspy import Stream, Trace, UTCDateTime, read
import pandas as pd
import numpy as np
from scipy.stats import entropy
from scipy.signal import welch
from io import BytesIO
import base64

def sampling_rate(time):
    # Calculate sampling rate
    sampling_rate = 1 / np.mean(np.diff(time))
    print(f"sampling rate: {sampling_rate}")
    return sampling_rate

def graphing(time, amplitude, title):
    # Crear la gráfica
    plt.figure(figsize=(10, 4))
    plt.plot(time, amplitude, label=f"{title}")
    plt.title(f"{title}")
    plt.xlabel("Tiempo (segundos)")
    plt.ylabel("Amplitud")
    plt.grid(True)

    # Guardar la gráfica en un buffer en formato PNG
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    # Convertir la imagen a base64 para que sea insertable en HTML
    image_png = buffer.getvalue()
    buffer.close()

    # Devolver la imagen en formato PNG
    return image_png


def cleaning(file):
    # cleaning.py
    df = pd.read_csv(file)
    # df['column_name'] = pd.to_numeric(df['column_name'], errors='coerce')
    df['time_rel(sec)'] = df['time_rel(sec)'].fillna(method='ffill')
    df['velocity(m/s)'] = df['velocity(m/s)'].fillna(method='ffill')

    # Drop still null values (if any)
    df = df.dropna()

    df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] = pd.to_datetime(df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'])
    df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] = (df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] -       
    df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'].iloc[0]).dt.total_seconds()
    time = df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'].values  # Time in seconds
    amplitude = df['velocity(m/s)'].values  # Not really amplitude but velocity
    print('done extracting')
    return time, amplitude

def fft(time, amplitude):
    # Compute power spectral density (PSD) using Welch's method
    freqs, psd = welch(amplitude, fs=sampling_rate(time))
    # Normalize the PSD
    psd_norm = psd / np.sum(psd)
    # Compute spectral entropy
    spectral_entropy = entropy(psd_norm)
    max_entropy = np.log(len(psd))
    normalized_entropy = spectral_entropy / max_entropy

    print(f"Spectral Entropy: {spectral_entropy}, Sending {normalized_entropy} frequencies")

    # make entropy determine 100% of data kept
    threshold_percentile = 100 - (normalized_entropy * 100)

    # Perform FFT on the amplitude data
    fft_result = np.fft.fft(amplitude)
    # Frequencies corresponding to the FFT result
    frequencies = np.fft.fftfreq(len(amplitude), 1 / sampling_rate(time))

    threshold = np.percentile(np.abs(fft_result), threshold_percentile) # HACE FALTA ENTROPY
    positions = np.where(np.abs(fft_result) >= threshold)[0]

    fft_result = fft_result[positions]
    frequencies = frequencies[positions]

    print(np.abs(fft_result)[0:10])

    # Perform inverse FFT to reconstruct the signal
    reconstructed_data = np.fft.ifft(fft_result)

    x = np.arange(time[0], time[len(time)-1], (time[len(time)-1]-time[0])/len(reconstructed_data.real))
    scale_factor = np.max(amplitude) / np.max(reconstructed_data.real)
    reconstructed_data.real *= scale_factor
    
    return reconstructed_data.real, x


# reconstruct into MINISEED
def save_miniseed(reconstructed_data, time):
    reconstructed_amplitude = reconstructed_data.real.astype(np.float32)

    # Crea una traza para el miniSEED
    trace = Trace(data=reconstructed_amplitude)  # Datos reconstruidos

    # Agrega información de metadatos
    trace.stats.network = 'XX'  # Código de red
    trace.stats.station = 'ABC'  # Código de estación
    trace.stats.location = 'MARS'    # Código de ubicación (opcional)
    trace.stats.channel = 'BHZ'  # Canal (BHZ: vertical, alta ganancia)
    trace.stats.starttime = UTCDateTime(time[0])  # Usar el primer timestamp
    trace.stats.sampling_rate = sampling_rate(time)  # Usa la tasa de muestreo
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


# time, amplitude = cleaning('data/xa.s12.00.mhz.1970-01-19HR00_evid00002.csv')
# graphing(time, amplitude, 'Raw Seismic Data')
# reconstructed_data, x = fft(time, amplitude)
# graphing(x, reconstructed_data, 'Reconstructed Seismic Data')
# save_miniseed(reconstructed_data, time)