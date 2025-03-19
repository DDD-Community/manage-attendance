from django.shortcuts import render

# Create your views here.
import qrcode
import io
import base64
from django.utils.timezone import now
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import QRLog
from .serializers import QRLogSerializer

# QR 코드 생성 뷰
class QRCodeGenerateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        timestamp = now().isoformat()
        qr_data = f"{user.id}|{timestamp}"
        
        # QR 코드 생성
        qr = qrcode.make(qr_data)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        # 로그 저장
        QRLog.objects.create(user=user, qr_string=qr_data)
        
        return Response({"qr_code": qr_base64, "qr_data": qr_data}, status=status.HTTP_201_CREATED)

# QR 코드 검증 뷰
class QRCodeValidateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        qr_data = request.data.get("qr_data")
        if not qr_data:
            return Response({"error": "QR 데이터를 제공해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_id, timestamp = qr_data.split("|")
            user = User.objects.get(id=user_id)
            
            # QR 유효성 검사 (예: 5분 이내 유효)
            qr_time = now() - now().fromisoformat(timestamp)
            if qr_time.total_seconds() > 300:
                return Response({"valid": False, "message": "QR 코드가 만료되었습니다."}, status=status.HTTP_410_GONE)
            
            return Response({"valid": True, "user_id": user.id, "username": user.username}, status=status.HTTP_200_OK)
        except (ValueError, User.DoesNotExist):
            return Response({"valid": False, "message": "유효하지 않은 QR 코드입니다."}, status=status.HTTP_400_BAD_REQUEST)

# QR 로그 조회 뷰
class QRLogListView(generics.ListAPIView):
    serializer_class = QRLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QRLog.objects.filter(user=self.request.user).order_by('-created_at')
