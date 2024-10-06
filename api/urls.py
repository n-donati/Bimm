from django.urls import path
from .views import LineDataView

urlpatterns = [
    path('line-data/', LineDataView.as_view(), name='line_data'),
]