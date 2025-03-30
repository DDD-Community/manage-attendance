from django.utils.timezone import now
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import QRLog
from .serializers import QRLogSerializer
from common.mixins import BaseResponseMixin

# QR 코드 생성 뷰
class QRCodeGenerateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        timestamp = now().isoformat()
        qr_string = f"{user.id}|{timestamp}"

        # 로그 저장
        QRLog.objects.create(user=user, qr_string=qr_string)
        
        return self.create_response(
            code=201,
            message="QR String이 생성되었습니다.",
            data={"qr_string": qr_string},
            status_code=status.HTTP_201_CREATED
        )

# QR 코드 검증 뷰
class QRCodeValidateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        qr_string = request.data.get("qr_string")
        if not qr_string:
            return self.create_response(
                code=400,
                message="QR 데이터를 제공해야 합니다.",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_id, timestamp = qr_string.split("|")
            user = User.objects.get(id=user_id)
            
            # QR 유효성 검사 (예: 5분 이내 유효)
            qr_time = now() - now().fromisoformat(timestamp)
            if qr_time.total_seconds() > 300:
                return self.create_response(
                    code=410,
                    message="QR 코드가 만료되었습니다.",
                    data={"valid": False},
                    status_code=status.HTTP_410_GONE
                )
            
            return self.create_response(
                code=200,
                message="QR 코드가 유효합니다.",
                data={
                    "valid": True,
                    "user_id": user.id,
                    "username": user.username
                }
            )
        except (ValueError, User.DoesNotExist):
            return self.create_response(
                code=400,
                message="유효하지 않은 QR 코드입니다.",
                data={"valid": False},
                status_code=status.HTTP_400_BAD_REQUEST
            )

# QR 로그 조회 뷰
class QRLogListView(BaseResponseMixin, generics.ListAPIView):
    serializer_class = QRLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return QRLog.objects.filter(user=self.request.user).order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.create_response(
            code=200,
            message="QR 로그를 성공적으로 조회했습니다.",
            data=serializer.data
        )
