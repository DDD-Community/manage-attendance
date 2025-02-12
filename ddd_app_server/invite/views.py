import random
from django.utils import timezone
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import InviteCode
from profiles.models import Profile
from django.viewes.decorators.csrf import csrf_exempt

class InviteCodeCreateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        invite_type = request.data.get("invite_type")
        expire_time = request.data.get("expire_time", timezone.now() + timezone.timedelta(days=365))
        one_time_use = str(request.data.get("one_time_use", "false")).lower() == "true"

        if invite_type not in dict(InviteCode.INVITE_TYPE_CHOICES):
            return JsonResponse({
                "code": 400,
                "message": "Invalid invite type.",
                "data": {
                    "your_input": invite_type,
                    "supported_input": list(dict(InviteCode.INVITE_TYPE_CHOICES).keys())
                }
            }, status=400)

        # Generate a unique 4-digit code
        existing_codes = set(InviteCode.objects.filter(expire_time__gt=timezone.now()).values_list("code", flat=True))
        code = next((f"{random.randint(0, 9999):04}" for _ in range(10000) if f"{random.randint(0, 9999):04}" not in existing_codes), None)
        
        if not code:
            return JsonResponse({"code": 500, "message": "Failed to generate a unique invite code."}, status=500)

        invite_code = InviteCode.objects.create(
            code=code,
            invite_type=invite_type,
            created_by=request.user,
            expire_time=expire_time,
            one_time_use=one_time_use,
        )

        return JsonResponse({
            "code": 201,
            "message": "Invite code created successfully.",
            "data": {
                "code": code,
                "invite_type": invite_type,
                "created_at": invite_code.created_at.isoformat(),
            }
        }, status=201)

class InviteCodeValidationView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        code = request.data.get("invite_code")
        if not code:
            return JsonResponse({"code": 400, "message": "Invite code is required.", "data": {}}, status=400)

        try:
            invite_code = InviteCode.objects.filter(code=code).latest("expire_time")

            if invite_code.is_expired:
                return JsonResponse({"code": 400, "message": "Invite code is expired.", "data": {}}, status=400)

            if invite_code.one_time_use and Profile.objects.filter(invite_code__code=code).exists():
                return JsonResponse({"code": 400, "message": "Invite code is already used.", "data": {}}, status=400)

            return JsonResponse({
                "code": 200,
                "message": "Invite code is valid.",
                "data": {
                    "valid": True,
                    "invite_type": invite_code.invite_type,
                    "created_by": invite_code.created_by.username,
                }
            }, status=200)
        except InviteCode.DoesNotExist:
            return JsonResponse({"code": 400, "message": "Invite code does not exist.", "data": {}}, status=400)
