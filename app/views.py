from django.shortcuts import render, redirect
from .forms import UploadMiniSeedForm
from .models import Record, Line
from obspy import read

def home(request):
    if request.method == 'POST':
        form = UploadMiniSeedForm(request.POST, request.FILES)
        if form.is_valid():
            mseed_file = request.FILES['file']
            st = read(mseed_file) 
            
            for trace in st:
                time_start = trace.stats.starttime
                time_end = trace.stats.endtime
                sampling_rate = trace.stats.sampling_rate
                record = Record.objects.create(time_start=str(time_start), time_end=str(time_end))
                for i, data in enumerate(trace.data):
                    current_time = time_start + (i / sampling_rate)
                    Line.objects.create(time=str(current_time), amplitude=data, record=record) 
                    if (i == 100):
                        break

    else:
        form = UploadMiniSeedForm()
    records = Record.objects.all()
    return render(request, 'home.html', {'form': form, 'records': records})
