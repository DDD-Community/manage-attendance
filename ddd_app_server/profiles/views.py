from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ProfileSerializer
from django.views.decorators.csrf import csrf_exempt

class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
