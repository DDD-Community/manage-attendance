from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.utils.timezone import now
from .models import InviteCode
from .serializers import InviteCodeSerializer
from django.contrib.auth.models import User, Group

# 초대 코드 생성 뷰
class InviteCodeCreateView(generics.CreateAPIView):
    queryset = InviteCode.objects.all()
    serializer_class = InviteCodeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 201,
                "message": "초대 코드가 생성되었습니다.",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "code": 400,
            "message": "초대 코드 생성에 실패했습니다.",
            "data": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

# 초대 코드 검증 및 사용자 그룹 설정 뷰
class InviteCodeValidateView(generics.GenericAPIView):
    serializer_class = InviteCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        code = request.data.get('invite_code')
        if not code:
            return Response({
                "code": 400,
                "message": "초대 코드를 입력하세요.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            invite_code = InviteCode.objects.get(code=code, expire_time__gte=now(), used=False)
            
            # Return invite code information without setting user group
            return Response({
                "code": 200,
                "message": "초대 코드가 유효합니다.",
                "data": {
                    "valid": True,
                    "invite_code_id": invite_code.id,
                    "invite_type": invite_code.invite_type,
                    "expire_time": invite_code.expire_time,
                    "one_time_use": invite_code.one_time_use
                }
            }, status=status.HTTP_200_OK)
        except InviteCode.DoesNotExist:
            return Response({
                "code": 400,
                "message": "유효하지 않은 초대 코드입니다.",
                "data": {
                    "valid": False,
                    "error": "유효하지 않은 초대 코드입니다."
                }
            }, status=status.HTTP_400_BAD_REQUEST)

# 초대 코드 목록 조회 뷰
class InviteCodeListView(generics.ListAPIView):
    serializer_class = InviteCodeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return InviteCode.objects.filter(created_by=self.request.user).order_by('-created_at')
