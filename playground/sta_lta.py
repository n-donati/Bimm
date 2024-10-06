
from obspy import read
from obspy.signal.invsim import cosine_taper
from obspy.signal.filter import highpass
from obspy.signal.trigger import classic_sta_lta, plot_trigger, trigger_onset
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

n1 = "xa.s12.00.mhz.1970-01-19HR00_evid00002"
n2 = "xa.s12.00.mhz.1970-03-25HR00_evid00003"
n3 = "xa.s12.00.mhz.1970-03-26HR00_evid00004"
n4 = "xa.s12.00.mhz.1970-04-25HR00_evid00006"
n5 = "xa.s12.00.mhz.1970-11-12HR00_evid00015"

filename = "output"
st = read(f'data/{filename}.mseed')
tr = st.traces[0].copy()
tr_times = tr.times()
tr_data = tr.data


df = tr.stats.sampling_rate

sta_len = 500
lta_len = 5000

cft = classic_sta_lta(tr_data, int(sta_len * df), int(lta_len * df))

fig,ax = plt.subplots(1,1,figsize=(12,3))
ax.plot(tr_times,cft)
ax.set_xlim([min(tr_times),max(tr_times)])
ax.set_xlabel('Time (s)')
ax.set_ylabel('Characteristic function')
plt.show()

thr_on = 3#max(1.5, )
thr_off = 1
on_off = np.array(trigger_onset(cft, thr_on, thr_off))

fig,ax = plt.subplots(1,1,figsize=(12,3))

filename = n2
data = pd.read_csv(f"data/{filename}.csv")
data['Sample'] = data['velocity(m/s)']
data['Time'] = pd.to_datetime(data[f'time_abs(%Y-%m-%dT%H:%M:%S.%f)'])
data['time_seconds'] = (data['Time'] - data['Time'].iloc[0]).dt.total_seconds()
time = data['time_seconds'].values

# Plot seismogram
#x = np.arange(time[0], time[len(time)-1], (time[len(time)-1]-time[0])/len(tr_data))
ax.plot(tr_times,tr_data)
ax.set_xlim([min(tr_times),max(tr_times)])
ax.legend()

x = np.arange(time[0], len(tr_data)-1, (len(tr_data)-1)/len(data['Sample']))
data['Sample'] = data['velocity(m/s)']
ax.plot(x,data['Sample'], color='c')

for i in np.arange(0,len(on_off)):
    triggers = on_off[i]
    beginning = max(triggers[0]-10000, 0)
    for j in range(int(triggers[0])-1, int(beginning), -1):
        if (cft[j] <= 0.5*cft[triggers[0]]):
            beginning = j
            break
    end = min(triggers[1]+10000, len(tr_data)-1)
    for j in range(int(triggers[1])+1, int(end)):
        if (cft[j] <= 0.3*cft[triggers[1]]):
            end = j
            break

    ax.axvline(x = tr_times[triggers[0]], color='red', label='Trig. On')
    ax.axvline(x = tr_times[triggers[1]], color='purple', label='Trig. Off')
    ax.axvline(x=beginning, color='green')
    ax.axvline(x=end, color='green')

# ax.legend()

plt.show()
