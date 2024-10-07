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
from datetime import datetime
import threading 
import time
from django.views.decorators.csrf import csrf_exempt
import base64
from .processing.pipeline import *
import io
import pandas as pd



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

data_list = []
min_range = 0
max_range = 2.5
start = False
end = False

import csv
import base64
from dateutil import parser
from datetime import datetime
import random
from django.http import JsonResponse
from .models import Record, Line, Simulation
from .forms import UploadCSVForm
from playground.pipeline import graphing, fft  # Assuming these functions are in a utils.py file

from django.shortcuts import render
from .forms import UploadCSVForm
from datetime import datetime
import csv
import pandas as pd
import base64
from .processing.pipeline import cleaning, graphing, autoencoder, sta_lta, fft, save_miniseed

def simulation(request):
    graph_image = None
    graph_image2 = None
    graph_image3 = None
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            
            # Read and process the CSV file
            csv_content = csv_file.read().decode('utf-8').splitlines()
            csv_reader = csv.reader(csv_content)
            
            # Skip header if it exists
            header = next(csv_reader, None)
            
            # Initialize variables
            time_start = None
            time_end = None
            times_abs = []
            times_rel = []
            velocities = []
            
            # Process each row
            for row in csv_reader:
                if len(row) >= 3:  # Ensure the row has at least 3 columns
                    try:
                        time = datetime.strptime(row[0], "%Y-%m-%dT%H:%M:%S.%f")
                        time_rel = float(row[1])
                        velocity = float(row[2])
                        
                        # Update time range
                        if time_start is None or time < time_start:
                            time_start = time
                        if time_end is None or time > time_end:
                            time_end = time
                        
                        times_abs.append(time)
                        times_rel.append(time_rel)
                        velocities.append(velocity)

                    except (ValueError, IndexError) as e:
                        print(f"Error processing row: {row}. Error: {e}")
            
            # Check if valid data was found
            if time_start and time_end:
                # Create DataFrame for processing
                df = pd.DataFrame({
                    'time_abs(%Y-%m-%dT%H:%M:%S.%f)': times_abs,
                    'time_rel(sec)': times_rel,
                    'velocity(m/s)': velocities
                })
                
                # Generate graphs
                relative_time, absolute_time, amplitude = cleaning(df)
                image_png = graphing(relative_time, amplitude, 'Raw Seismic Data')
                
                dataframe = autoencoder(relative_time, absolute_time, amplitude)
                image_png2 = graphing(relative_time, dataframe['time_rel(sec)'], 'Autoencoder Seismic Data')
                quakes = sta_lta(dataframe)

                image_png3 = None
                if quakes:
                    reconstructed_data, x = fft(relative_time, quakes[-1])
                    image_png3 = graphing(x, reconstructed_data, 'Reconstructed Seismic Data')
                    
                    for i, quake in enumerate(quakes, 1):
                        save_miniseed(quake, absolute_time, i)
                
                # Convert images to base64 for HTML inclusion
                graph_image = base64.b64encode(image_png).decode('utf-8') if image_png else ""
                graph_image2 = base64.b64encode(image_png2).decode('utf-8') if image_png2 else ""
                graph_image3 = base64.b64encode(image_png3).decode('utf-8') if image_png3 else ""

                
                return render(request, 'simulation.html', {
                    'message': f'File "{csv_file.name}" processed successfully.',
                    'data_points': len(times_abs),
                    'graph_image': graph_image,
                    'graph_image2': graph_image2,
                    'graph_image3': graph_image3,
                    'form': form
                })
            else:
                return render(request, 'simulation.html', {
                    'message': 'Error: No valid data found in the CSV file.',
                    'form': form
                })
    else:
        form = UploadCSVForm()
    
    return render(request, 'simulation.html', {'form': form, 'graph_image': graph_image,
                    'graph_image2': graph_image2,
                    'graph_image3': graph_image3,})

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

counter = 0
@csrf_exempt  
def get_events(request):
    global counter
    simulations = Simulation.objects.all().order_by('id')
    start_event = simulations.filter(start_event=True).first()
    end_event = simulations.filter(end_event=True).first()
    
    if start_event and end_event:
        # Crea un registro en Record con los tiempos de inicio y fin
        record = Record.objects.create(
            time_start=start_event.time,
            time_end=end_event.time,
            file_name=f'record_{counter}'
        )
        counter += 1

        # Filtra los simulations entre el evento de inicio y el evento de fin
        simulations_in_range = simulations.filter(id__gt=start_event.id, id__lt=end_event.id)

        # Crea los objetos Line para cada simulation en el rango
        for sim in simulations_in_range:
            Line.objects.create(
                record=record,  # Vincula con el record creado
                time=sim.time,  # Información de la simulación
                amplitude=sim.amplitude  # Campo adicional
            )
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

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatgpt import ChatGPT

@csrf_exempt
def generate_response(request):
    if request.method == 'POST':
        message = request.POST.get('message')
        chatgpt = ChatGPT()  # No need to pass the API key here
        response = chatgpt.get_response(message)  # Changed from generate_response to get_response
        return JsonResponse({'response': response})