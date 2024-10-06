import os
from django.shortcuts import render, redirect
from django.urls import reverse
import numpy as np
from numpy.fft import fft
from .models import Record, Line, Simulation
from obspy import read, Stream, Trace
from obspy.core import UTCDateTime
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse
import csv
from .forms import UploadCSVForm
from django.http import JsonResponse
import random
from datetime import datetime
import threading 
import time
from django.views.decorators.csrf import csrf_exempt
import base64
from playground.pipeline import cleaning, graphing, fft, save_miniseed



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
    else:
        form = UploadCSVForm()
    
    # If it's a GET request, or after redirecting from POST
    records = Record.objects.all().order_by('-id')
    qty_records = Record.objects.count()
    return render(request, 'home.html', {'records': records, 'qty_records': qty_records, 'form': form})

data_list = []
min_range = 0
max_range = 2.5
start = False
end = False

def simulation(request):
    global end, start

    # Pasar la imagen como contexto a la plantilla
    
    form = UploadCSVForm()
    graph_image = None
    graph_image2 = None
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            time, amplitude = cleaning(csv_file)

            # Obtener la imagen en base64
            image_png = graphing(time, amplitude, 'Clean Data Graphic')
            reconstructed_data, x = fft(time, amplitude)
            image2_png = graphing(x, reconstructed_data, 'Reconstructed Seismic Data')
            # save_miniseed(reconstructed_data, time)

            # Convertir la imagen a base64 para incluirla en HTML
            graph_image = base64.b64encode(image_png).decode('utf-8')
            graph_image2 = base64.b64encode(image2_png).decode('utf-8')
            # st = read(csv_file) 
            
            # for trace in st:
            #     time_start = trace.stats.starttime
            #     time_end = trace.stats.endtime
            #     sampling_rate = trace.stats.sampling_rate
            #     record = Record.objects.create(time_start=str(time_start), time_end=str(time_end), file_name=csv_file)
            #     for i, data in enumerate(trace.data):
            #         current_time = time_start + (i / sampling_rate)
            #         Line.objects.create(time=str(current_time), amplitude=data, record=record) 
            #         if (i == 1000):
            #             break


    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        random_number = round(random.uniform(min_range, max_range), 14)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = Simulation.objects.create(time=current_time, amplitude=random_number, start_event=start, end_event=end)
        start = False
        end = False

        data_list.insert(0, {'number': random_number, 'timestamp': current_time})

        if len(data_list) > 10:
            data_list.pop()

        return JsonResponse({'data': data_list})
    
    return render(request, 'simulation.html', {'form': form, 'graph_image': graph_image, 'graph_image2': graph_image2})

@csrf_exempt
def change_parameters(request):
    global min_range, max_range, start
    min_range = 2.5
    max_range = 10
    start = True
    threading.Thread(target=reset_parameters).start()
    return JsonResponse({'status': 'Parameters changed'})
    
def reset_parameters():
    global min_range, max_range, end
    time.sleep(10)
    min_range = 0
    max_range = 2.5
    end = True

@csrf_exempt  
def get_events(request):
    simulations = Simulation.objects.all()
    start_event = simulations.filter(start_event=1)
    print("\n\n", start_event, "\n\n")
    if len(start_event) > 0:
        end_event = simulations.filter(end_event=1)
        print("\n\n", end_event, "\n\n")
        record = Record.objects.create(time_start=str(start_event.first().time), time_end=str(end_event.first().time))
    Simulation.objects.all().delete()
    return JsonResponse({'status': 'Get Events'})

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