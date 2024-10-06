from rest_framework.views import APIView
from rest_framework.response import Response
from app.models import Line
from .serializers import LineSerializer

class LineDataView(APIView):
    def get(self, request):
        record_id = request.query_params.get('record_id')
        lines = Line.objects.filter(record=record_id)
        serializer = LineSerializer(lines, many=True)
        return Response(serializer.data)