import matplotlib.pyplot as plt
from obspy import Stream, Trace, UTCDateTime, read
import pandas as pd
import numpy as np
from scipy.stats import entropy
from scipy.signal import welch
from obspy.signal.trigger import classic_sta_lta, trigger_onset
import torch
import xarray as xr
from .sedenoss.sedenoss.models import FaSNet_base
import torch
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def sampling_rate(time):
    # Calculate sampling rate
    sampling_rate = 1 / np.mean(np.diff(time))
    print(f"sampling rate: {sampling_rate}")
    return sampling_rate

def graphing(time, amplitude, title):
    plt.figure(figsize=(10, 4))
    plt.plot(time, amplitude, label=f"{title}")
    plt.title(f"{title}")
    plt.xlabel("Tiempo (segundos)")
    plt.ylabel("Amplitud")
    plt.grid(True)
    plt.show()


def cleaning(df):
    # cleaning.py
    # df = pd.read_csv(file)
    # df['column_name'] = pd.to_numeric(df['column_name'], errors='coerce')
    df['time_rel(sec)'] = df['time_rel(sec)'].fillna(method='ffill')
    df['velocity(m/s)'] = df['velocity(m/s)'].fillna(method='ffill')

    df = df.dropna()

    df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] = pd.to_datetime(df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'])
    df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] = (df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'] -       
    df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'].iloc[0]).dt.total_seconds()
    absolute_time = df['time_abs(%Y-%m-%dT%H:%M:%S.%f)'].values  # Time in seconds
    relative_time = df['time_rel(sec)'].values  # Time in seconds
    amplitude = df['velocity(m/s)'].values  # Not really amplitude but velocity
    print('done cleaning')
    return relative_time, absolute_time, amplitude

def autoencoder(relative_time, absolute_time, amplitude):
    # Load the model
    model = FaSNet_base()
    state_dict = torch.load('app/processing/trained_196.pt', map_location=torch.device('cpu'))
    model.load_state_dict(state_dict, strict=False)
    model.eval()

    # Load and prepare the data
    file_path = 'app/processing/output_data.nc'
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
    return combined_df

    
def sta_lta(dataframe):
    absolute_time = dataframe['time_abs(%Y-%m-%dT%H:%M:%S.%f)']
    denoised_data = dataframe['velocity(m/s)']
    # sta_lta.py
    sta_len = 500 # Longitud de ventana del STA
    lta_len = 5000 # Longitud de ventana del LTA
    cft = classic_sta_lta(denoised_data, int(sta_len), int(lta_len))
    thr_on = 9 # On threshold 
    thr_off = 1 # Off threshold
    on_off = np.array(trigger_onset(cft, thr_on, thr_off))

    res = []

    for i in np.arange(0, len(on_off)):

        # Definir rango del sismo
        triggers = on_off[i]
        beginning = max(triggers[0]-10000, 0)
        for j in range(int(triggers[0])-1, int(beginning), -1):
            if (cft[j] <= 0.5*cft[triggers[0]]):
                beginning = j
                break
        end = min(triggers[1]+10000, len(denoised_data)-1)
        for j in range(int(triggers[1])+1, int(end)):
            if (cft[j] <= 0.3*cft[triggers[1]]):
                end = j
                break

        # Guardar pedazo de gráfica con sismo
        res.append(denoised_data[beginning:end])

    return res

def fft(time, amplitude):
    print("time", time.shape)
    print("amplitude", amplitude.shape)
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
def save_miniseed(reconstructed_data, time, count):
    # reconstructed_amplitude = reconstructed_data.real.astype(np.float32)
    # reconstructed_amplitude = reconstructed_data.astype(np.float32)
    reconstructed_amplitude = np.array(reconstructed_data).astype(np.float32)

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
    output_filename = f"static/data/processed/output_reconstructed_data{count}.mseed"
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
