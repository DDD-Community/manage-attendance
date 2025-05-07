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
from common.serializers import ErrorResponseSerializer
from rest_framework import serializers
from .serializers import QRLogSerializer
from common.mixins import BaseResponseMixin

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
        operation_summary="QR 로그 조회",
        operation_description="로그인 사용자의 QR 생성/사용 로그 목록을 조회합니다.",
        responses={
            200: QRLogListSuccessResponseSerializer,
            400: ErrorResponseSerializer
        }
    )
    def get(self, request):
        logs = QRLog.objects.filter(user=request.user).order_by('-created_at')
        # The data from QRLogSerializer(many=True) directly fits the 'data' field of QRLogListSuccessResponseSerializer
        serializer = QRLogSerializer(logs, many=True)
        return self.create_response(
            code=200,
            message="QR 로그를 성공적으로 조회했습니다.",
            data=serializer.data,
            status_code=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 코드 생성",
        operation_description="로그인한 사용자의 ID와 username을 JWT로 암호화한 QR 코드를 생성합니다. QR 코드는 생성 후 5분간 유효합니다.",
        responses={
            200: QRCodeGenerateSuccessResponseSerializer,
            400: ErrorResponseSerializer,
        }
    )
    def post(self, request):
        user = request.user
        token = AccessToken.for_user(user)
        token.set_exp(lifetime=timedelta(minutes=5))  # 5분간 유효
        token["username"] = user.username

        qr_string = str(token)
        QRLog.objects.create(user=user, qr_string=qr_string)
        response_data = {"qr_string": qr_string}
        return self.create_response(
            code=201,
            message="QR JWT가 생성되었습니다.",
            data=response_data,
            status_code=status.HTTP_201_CREATED
        )

class QRCodeValidateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["qr"],
        operation_summary="QR 코드 검증",
        operation_description="QR 코드 JWT를 검증하고 사용자 정보를 반환합니다.",
        request_body=QRLogSerializer,
        responses={
            200: QRCodeValidateSuccessResponseSerializer,
            410: QRCodeValidateFailedResponseSerializer,
            400: ErrorResponseSerializer
        }
    )
    def post(self, request):
        request_serializer = QRLogSerializer(data=request.data)
        if not request_serializer.is_valid():
            error_messages = ". ".join([f"{key}: {', '.join(value)}" for key, value in request_serializer.errors.items()])
            return self.create_response(
                code=400,
                message=f"잘못된 입력입니다: {error_messages}",
                data={"valid": False}, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        qr_string = request_serializer.validated_data["qr_string"]
        token_backend = TokenBackend(
            algorithm=settings.SIMPLE_JWT.get('ALGORITHM', 'HS256'),
            signing_key=settings.SECRET_KEY
        )

        qr_log = QRLog.objects.filter(qr_string=qr_string).first()
        if qr_log and qr_log.decoded_at:
            return self.create_response(
                code=410,
                message="QR 코드가 이미 사용되었습니다.",
                data={"valid": False},
                status_code=status.HTTP_410_GONE
            )
        if qr_log:
            qr_log.decoded_at = now()
            qr_log.save()

        try:
            valid_data_payload = token_backend.decode(qr_string, verify=True)
            user_id = valid_data_payload.get("user_id")
            username = valid_data_payload.get("username")

            if user_id is None:
                 raise InvalidToken("토큰에 사용자 ID 정보가 없습니다.")
            user = User.objects.filter(id=user_id, is_active=True).first()
            if not user:
                raise InvalidToken("존재하지 않거나 활성 상태가 아닌 사용자입니다.")

            response_data = {"valid": True, "user_id": user_id, "username": username if username else user.username}
            return self.create_response(
                code=200,
                message="QR 코드가 유효합니다.",
                data=response_data,
                status_code=status.HTTP_200_OK
            )
        except InvalidToken as e:
             # This data structure matches QRErrorDataSerializer
             return self.create_response(
                code=400, 
                message=str(e),
                data={"valid": False},
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except TokenError as e:
            error_str = str(e).lower()
            if "expired" in error_str or ("token_not_valid" in error_str and "Expired" in str(e)):
                 # This data structure matches QRErrorDataSerializer
                return self.create_response(
                    code=410,
                    message="QR 코드가 만료되었습니다.",
                    data={"valid": False},
                    status_code=status.HTTP_410_GONE
                )
            # This data structure matches QRErrorDataSerializer
            return self.create_response(
                code=400, 
                message=f"유효하지 않은 QR 코드 형식입니다: {str(e)}",
                data={"valid": False}, 
                status_code=status.HTTP_400_BAD_REQUEST
            )
