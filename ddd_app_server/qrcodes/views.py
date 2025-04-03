from django.utils.timezone import now
from django.contrib.auth.models import User
from django.conf import settings
from datetime import timedelta

from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.backends import TokenBackend
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import QRLog
from .serializers import QRLogSerializer
from common.mixins import BaseResponseMixin

class QRCodeGenerateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 코드 생성",
        operation_description="로그인한 사용자의 ID를 JWT로 암호화한 QR 코드를 생성합니다. QR 코드는 생성 후 5분간 유효합니다.",
        responses={
            201: openapi.Response(
                description="QR 문자열(JWT) 생성 성공",
                examples={
                    "application/json": {
                        "qr_string": "jwt-token-string"
                    }
                }
            )
        }
    )
    def post(self, request):
        user = request.user
        token = AccessToken.for_user(user)
        token.set_exp(lifetime=timedelta(minutes=5))  # 5분간 유효
        token["username"] = user.username

        qr_string = str(token)

        # QR 로그 저장
        QRLog.objects.create(user=user, qr_string=qr_string)

        return self.create_response(
            code=201,
            message="QR JWT가 생성되었습니다.",
            data={"qr_string": qr_string},
            status_code=status.HTTP_201_CREATED
        )

class QRCodeValidateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 코드 검증",
        operation_description="QR 코드 JWT를 검증하고 사용자 정보를 반환합니다.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["qr_string"],
            properties={
                "qr_string": openapi.Schema(type=openapi.TYPE_STRING, description="검증할 JWT QR 문자열")
            }
        ),
        responses={
            200: openapi.Response(
                description="QR 코드가 유효한 경우",
                examples={
                    "application/json": {
                        "valid": True, 
                        "user_id": 1, 
                        "username": "example"
                    }
                }
            ),
            400: "유효하지 않은 QR 코드",
            410: "QR 코드가 만료된 경우"
        }
    )
    def post(self, request):
        qr_string = request.data.get("qr_string")

        if not qr_string:
            return self.create_response(
                code=400,
                message="QR 데이터를 제공해야 합니다.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        token_backend = TokenBackend(
            algorithm='HS256', 
            signing_key=settings.SECRET_KEY
        )

        try:
            valid_data = token_backend.decode(qr_string, verify=True)
            user_id = valid_data.get("user_id")
            username = valid_data.get("username")

            if not User.objects.filter(id=user_id).exists():
                raise InvalidToken("존재하지 않는 사용자입니다.")

            return self.create_response(
                code=200,
                message="QR 코드가 유효합니다.",
                data={"valid": True, "user_id": user_id, "username": username}
            )

        except TokenError as e:
            error_str = str(e).lower()
            if "expired" in error_str:
                return self.create_response(
                    code=410,
                    message="QR 코드가 만료되었습니다.",
                    data={"valid": False},
                    status_code=status.HTTP_410_GONE
                )
            return self.create_response(
                code=400,
                message="유효하지 않은 QR 코드입니다.",
                data={"valid": False},
                status_code=status.HTTP_400_BAD_REQUEST
            )

class QRLogListView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 로그 조회",
        operation_description="로그인 사용자의 QR 로그 목록을 조회합니다.",
        responses={200: QRLogSerializer(many=True)}
    )
    def get(self, request):
        logs = QRLog.objects.filter(user=request.user).order_by('-created_at')
        serializer = QRLogSerializer(logs, many=True)

        return self.create_response(
            code=200,
            message="QR 로그를 성공적으로 조회했습니다.",
            data=serializer.data
        )
