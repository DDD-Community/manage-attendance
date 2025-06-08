from django.utils.timezone import now
from django.contrib.auth.models import User
from django.conf import settings
from datetime import timedelta

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import serializers

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import QRLog
from common.serializers import ErrorResponseSerializer
from .serializers import QRLogSerializer
from common.mixins import BaseResponseMixin
from attendances.models import Attendance

# QR 코드 생성 응답 Serializer
class QRCodeGenerateSuccessResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=201)
    message = serializers.CharField(default="QR JWT가 생성되었습니다.")
    data = QRLogSerializer()

# QR 코드 검증 응답 Serializer
class QRCodeValidateSuccessResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="QR 코드가 유효합니다.")
    data = QRLogSerializer()

# QR 코드 검증 실패 응답 Serializer
class QRCodeValidateFailedResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=410)
    message = serializers.CharField(default="QR 코드가 만료되었습니다.")
    data = serializers.SerializerMethodField()

    def get_data(self, obj):
        return {
            "valid": False
        }

# QR 코드 목록 응답 Serializer
class QRLogListSuccessResponseSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="QR 로그를 성공적으로 조회했습니다.")
    data = QRLogSerializer(many=True)


class QRCodeGenerateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 로그 목록 조회",
        operation_description="로그인된 사용자가 생성한 QR 코드 목록을 조회합니다.",
        responses={
            200: QRLogListSuccessResponseSerializer,
            400: ErrorResponseSerializer
        }
    )
    def get(self, request):
        logs = QRLog.objects.filter(user=request.user).order_by('-created_at')
        serializer = QRLogSerializer(logs, many=True)
        return self.create_response(
            code=status.HTTP_200_OK,
            message="QR 로그를 성공적으로 조회했습니다.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 코드 생성",
        operation_description="레코드의 ID를 사용하여 새로운 QR 코드를 생성합니다. 5분간 유효합니다.",
        responses={
            200: QRCodeGenerateSuccessResponseSerializer,
            400: ErrorResponseSerializer,
        }
    )
    def post(self, request):
        user = request.user
        
        # 만료 시간 정의
        expire_at = now() + timedelta(minutes=5)
        
        # ID를 얻기 위해 먼저 로그 항목 생성
        qr_log = QRLog.objects.create(user=user, expire_at=expire_at)
        
        serializer = QRLogSerializer(qr_log)
        return self.create_response(
            code=status.HTTP_201_CREATED,
            message="QR 코드가 성공적으로 생성되었습니다.",
            data=serializer.data,
            status_code=status.HTTP_201_CREATED
        )

class QRCodeValidateView(BaseResponseMixin, APIView):
    """
    QR 코드 문자열(QRLog 레코드의 ID)을 검증합니다.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 코드 검증",
        operation_description="제공된 QR 코드(QRLog ID)를 검증합니다.",
        request_body=QRLogSerializer,
        responses={
            200: QRCodeValidateSuccessResponseSerializer,
            410: QRCodeValidateFailedResponseSerializer,
            400: ErrorResponseSerializer
        }
    )
    def post(self, request):
        qr_id = request.data.get('qr_string')

        if not qr_id:
            return self.create_response(
                code=status.HTTP_400_BAD_REQUEST,
                message="잘못된 입력입니다: qr_string은 유효한 ID여야 합니다.",
                data={"valid": False}, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        # 기본 키(ID)로 QR 코드 로그 항목 찾기
        try:
            qr_log = QRLog.objects.select_related('user').get(pk=qr_id)
        except QRLog.DoesNotExist:
            return self.create_response(
                code=status.HTTP_400_BAD_REQUEST,
                message="유효하지 않은 QR 코드입니다.",
                data={"valid": False},
                status_code=status.HTTP_400_BAD_REQUEST
            )

        # 사례 1: QR 코드가 이미 사용됨
        if qr_log.decoded_at:
            return self.create_response(
                code=status.HTTP_410_GONE,
                message="이미 사용된 QR 코드입니다.",
                data={"valid": False},
                status_code=status.HTTP_410_GONE
            )

        # 사례 2: QR 코드가 만료됨
        if now() > qr_log.expire_at:
            return self.create_response(
                code=status.HTTP_410_GONE,
                message="만료된 QR 코드입니다.",
                data={"valid": False},
                status_code=status.HTTP_410_GONE
            )

        # 출석 수정
        attendance = Attendance.objects.select_related('user', 'schedule').filter(
            user=qr_log.user,
            schedule__start_time__lte=now(),
            schedule__end_time__gte=now()
        ).first()

        if attendance:
            attendance.update(status='auto', method='qr')
            attendance.save()

        # 모든 확인을 통과하면 QR 코드가 유효함
        # 'decoded_at' 타임스탬프를 설정하여 사용됨으로 표시
        qr_log.decoded_at = now()
        qr_log.save()

        user = qr_log.user
        response_data = {
            "valid": True, 
            "user_id": user.id, 
            "username": user.username
        }
        
        return self.create_response(
            code=status.HTTP_200_OK,
            message="QR 코드가 유효합니다.",
            data=response_data,
            status_code=status.HTTP_200_OK
        )
