from django.db import models
from datetime import date

class Record(models.Model):

    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    file_name = models.CharField(max_length=255, unique=True, default='')

    def __str__(self):
        return f"Record {self.id}: {self.time_start} - {self.time_end}"

class Line(models.Model):
    time = models.DateTimeField()
    amplitude = models.FloatField()
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='lines')

    def __str__(self):
        return f"Line {self.id} at {self.time}: {self.amplitude}"