from obspy import read

st = read("miniSEED.mseed")

print(st)
first_trace = st[0]  # Accede al primer trace
first_sample = first_trace.data[0]  # Accede a la primera muestra de datos

start_time = first_trace.stats.starttime
sampling_rate = first_trace.stats.sampling_rate

# Calcula el tiempo de la primera muestra
first_sample_time = start_time + (0 / sampling_rate)

print(f"La primera muestra de datos es: {first_sample} en el tiempo: {first_sample_time}")


st.plot()