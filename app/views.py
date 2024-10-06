import os
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import Record, Line
from obspy import read
from django.conf import settings
from django.utils import timezone

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
                            if i == 100:
                                break
        
        # After processing, redirect to the same page
        return redirect(reverse('home'))
    
    # If it's a GET request, or after redirecting from POST
    records = Record.objects.all().order_by('-id')
    return render(request, 'home.html', {'records': records})