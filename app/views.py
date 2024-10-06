import os
from django.shortcuts import render, redirect
from django.urls import reverse
import numpy as np
from .models import Record, Line
from obspy import read, Stream, Trace
from obspy.core import UTCDateTime
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
import csv

def home(request):
    if request.method == 'POST':
        folder_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'processed')
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):
                # Check if the file has already been processed
                if not Record.objects.filter(file_name=filename).exists():
                    st = read(file_path)
                    for trace in st:
                        time_start = trace.stats.starttime.datetime
                        time_end = trace.stats.endtime.datetime
                        sampling_rate = trace.stats.sampling_rate
                        record = Record.objects.create(
                            time_start=time_start,
                            time_end=time_end,
                            file_name=filename
                        )
                        for i, data in enumerate(trace.data):
                            current_time = time_start + timezone.timedelta(seconds=i / sampling_rate)
                            Line.objects.create(time=current_time, amplitude=data, record=record)
                            if i == 1000:
                                break
        
        # After processing, redirect to the same page
        return redirect(reverse('home'))
    
    # If it's a GET request, or after redirecting from POST
    records = Record.objects.all().order_by('-id')
    qty_records = Record.objects.count()
    return render(request, 'home.html', {'records': records, 'qty_records': qty_records})

def download_csv(request, record_id):
    record = Record.objects.get(id=record_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="record_{record_id}.csv"'
    
    writer = csv.writer(response)
    
    writer.writerow(['Timestamp', 'Amplitude'])
    
    for line in record.lines.all():
        writer.writerow([line.time.isoformat(), line.amplitude])
    
    return response

def download_miniseed(request, record_id):
    record = Record.objects.get(id=record_id)

    stream = Stream()
    
    trace = Trace()
    
    trace.stats.network = "NET"
    trace.stats.station = "STA"
    trace.stats.location = "00"
    trace.stats.channel = "BHZ" 
    trace.stats.sampling_rate = 100.0
     
    times = []
    amplitudes = []
    
    for line in record.lines.all():
        times.append(UTCDateTime(line.time))
        amplitudes.append(line.amplitude)

    trace.times = times

    trace.data = np.array(amplitudes)

    stream.append(trace)

    response = HttpResponse(content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="record_{record_id}.mseed"'

    stream.write(response, format='MSEED')
    
    return response