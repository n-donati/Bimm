from django.shortcuts import render, redirect
from .forms import UploadMiniSeedForm
from .models import Record, Line, Simulation
from obspy import read
from django.http import JsonResponse
import random
from datetime import datetime
import threading 
import time
from django.views.decorators.csrf import csrf_exempt

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


data_list = []
min_range = 0
max_range = 2.5
start = False
end = True

def simulation(request):
    global end, start
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
    return render(request, 'simulation.html')

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
    


    
    
