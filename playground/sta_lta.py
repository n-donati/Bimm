
from obspy import read
from obspy.signal.invsim import cosine_taper
from obspy.signal.filter import highpass
from obspy.signal.trigger import classic_sta_lta, plot_trigger, trigger_onset
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from obspy import Trace, Stream

n1 = "xa.s12.00.mhz.1970-01-19HR00_evid00002"
n2 = "xa.s12.00.mhz.1970-03-25HR00_evid00003"
n3 = "xa.s12.00.mhz.1970-03-26HR00_evid00004"
n4 = "xa.s12.00.mhz.1970-04-25HR00_evid00006"
n5 = "xa.s12.00.mhz.1970-11-12HR00_evid00015"

used_filename = n3

filename = "output"
st = read(f'data/{filename}.mseed')
tr = st.traces[0].copy()
tr_times = tr.times()
tr_data = tr.data

df = tr.stats.sampling_rate

sta_len = 500
lta_len = 5000

cft = classic_sta_lta(tr_data, int(sta_len), int(lta_len))

fig,ax = plt.subplots(1,1,figsize=(12,3))
ax.plot(tr_times,cft)
ax.set_xlim([min(tr_times),max(tr_times)])
ax.set_xlabel('Time (s)')
ax.set_ylabel('Characteristic function')
plt.show()

thr_on = 3
thr_off = 1
on_off = np.array(trigger_onset(cft, thr_on, thr_off))

# fig,ax = plt.subplots(1,1,figsize=(12,3))

# Plot seismogram
#x = np.arange(time[0], time[len(time)-1], (time[len(time)-1]-time[0])/len(tr_data))
# ax.plot(tr_times,tr_data)
# ax.set_xlim([min(tr_times),max(tr_times)])
# ax.legend()

for i in np.arange(0,len(on_off)):
    triggers = on_off[i]
    print(triggers)
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
    trace = Trace()
    trace.data = tr_data[beginning:end]
    trace.stats.starttime = tr_times[beginning]
    trace.stats.sampling_rate = (end-beginning) / (tr_times[end]-tr_times[beginning])
    stream = Stream(traces=[trace])
    filename = f"Quake_{used_filename}_{i}"
    stream.write(f"data/{filename}.mseed", format='MSEED')

print(end-beginning)
# ax.legend()

plt.show()
