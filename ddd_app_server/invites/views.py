from rest_framework.views import APIView
from rest_framework import permissions, status, serializers
from django.utils.timezone import now
from .models import InviteCode
from .serializers import InviteCodeSerializer
from drf_yasg.utils import swagger_auto_schema
from common.mixins import BaseResponseMixin
from common.serializers import ErrorResponseSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

# 초대 코드 생성 성공 응답 Serializer
class InviteCodeCreateSuccessSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=201)
    message = serializers.CharField(default="초대 코드가 생성되었습니다.")
    data = InviteCodeSerializer()

# 초대 코드 검증 성공 응답 Serializer
class InviteCodeValidateSuccessSerializer(serializers.Serializer):
    code = serializers.IntegerField(default=200)
    message = serializers.CharField(default="초대 코드가 유효합니다.")
    data = serializers.DictField(child=serializers.CharField())

# 초대 코드 생성 뷰 using APIView
class InviteCodeCreateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["invites"],
        operation_summary="초대 코드 생성",
        operation_description="초대 코드를 생성합니다.",
        request_body=InviteCodeSerializer,
        responses={
            201: InviteCodeCreateSuccessSerializer,
            400: ErrorResponseSerializer
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = InviteCodeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return self.create_response(201, "초대 코드가 생성되었습니다.", serializer.data, status.HTTP_201_CREATED)
        return self.create_response(400, "초대 코드 생성에 실패했습니다.", serializer.errors, status.HTTP_400_BAD_REQUEST)

# 초대 코드 검증 요청 Serializer
class InviteCodeValidateRequestSerializer(serializers.Serializer):
    invite_code = serializers.CharField(required=True, help_text="검증할 초대 코드입니다.")

# 초대 코드 검증 뷰 using APIView
class InviteCodeValidateView(BaseResponseMixin, APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        tags=["invites"],
        operation_summary="초대 코드 검증",
        operation_description="초대 코드를 검증하여 유효성을 확인합니다.",
        request_body=InviteCodeValidateRequestSerializer,
        responses={
            200: InviteCodeValidateSuccessSerializer,
            400: ErrorResponseSerializer
        },
    )
    def post(self, request, *args, **kwargs):
        serializer = InviteCodeValidateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data['invite_code']

        try:
            invite_code = InviteCode.objects.get(code=code, expire_time__gte=now(), used=False)
            response_data = {
                "valid": True,
                "invite_code_id": invite_code.id,
                "invite_type": invite_code.invite_type,
                "expire_time": invite_code.expire_time.isoformat(),
                "one_time_use": invite_code.one_time_use
            }
            return self.create_response(200, "초대 코드가 유효합니다.", response_data, status.HTTP_200_OK)
        except InviteCode.DoesNotExist:
            return self.create_response(400, "유효하지 않은 초대 코드입니다.", {
                    "valid": False,
                    "error": "유효하지 않은 초대 코드입니다."
                }, status.HTTP_400_BAD_REQUEST)
