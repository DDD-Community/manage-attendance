from django.utils.timezone import now
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import QRLog
from .serializers import QRLogSerializer
from common.mixins import BaseResponseMixin
from rest_framework_simplejwt.authentication import JWTAuthentication

# QR 코드 생성 뷰
class QRCodeGenerateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 코드 생성",
        operation_description="현재 로그인한 사용자의 ID와 현재 시간을 기반으로 QR 문자열을 생성하고, 해당 정보를 로그에 저장합니다.",
        request_body=None,
        responses={
            201: openapi.Response(
                description="QR 문자열 생성 성공",
                examples={
                    "application/json": {
                        "qr_string": "1|2023-04-03T12:34:56"
                    }
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        timestamp = now().isoformat()
        qr_string = f"{user.id}|{timestamp}"

        # QR 로그 저장
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
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 코드 검증",
        operation_description="제공된 QR 문자열을 검증하여 해당 사용자의 정보를 반환합니다. (QR 코드는 생성 후 5분 이내에만 유효합니다.)",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["qr_string"],
            properties={
                "qr_string": openapi.Schema(type=openapi.TYPE_STRING, description="검증할 QR 문자열")
            }
        ),
        responses={
            200: openapi.Response(
                description="QR 코드가 유효한 경우",
                examples={"application/json": {"valid": True, "user_id": 1, "username": "example"}}
            ),
            400: openapi.Response(description="유효하지 않은 QR 코드 또는 요청 데이터 누락"),
            410: openapi.Response(description="QR 코드가 만료된 경우")
        }
    )
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
            
            # QR 유효성 검사 (생성 후 5분 이내 유효)
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
class QRLogListView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 로그 조회",
        operation_description="현재 로그인한 사용자의 QR 로그 목록을 조회합니다.",
        responses={200: QRLogSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        queryset = QRLog.objects.filter(user=request.user).order_by('-created_at')
        serializer = QRLogSerializer(queryset, many=True)
        return self.create_response(
            code=200,
            message="QR 로그를 성공적으로 조회했습니다.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )
