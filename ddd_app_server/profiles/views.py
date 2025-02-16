from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from invite.models import InviteCode

class ProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @csrf_exempt
    def get(self, request, *args, **kwargs):
        profile = request.user.profile

        # Construct response data manually
        data = {
            "id": profile.id,
            "name": profile.name,
            "invite_code": None
        }

        if profile.invite_code is not None:
            data["invite_code"] = profile.invite_code.code

        return Response(data)

    @csrf_exempt
    def put(self, request, *args, **kwargs):
        """
        Manually parse the request data, link the InviteCode, and save.
        """
        try:
            profile = request.user.profile

            # Pull "name" and "invite_code" from the request body
            new_name = request.data.get("name")
            code_str = request.data.get("invite_code")

            if new_name:
                profile.name = new_name

            if code_str:
                # Get InviteCode object by "code" field
                invite_code = InviteCode.objects.filter(code=code_str).latest("expire_time")
                profile.invite_code = invite_code

            # Save changes to the Profile
            profile.save()

            # Return JSON structure manually
            data = {
                "id": profile.id,
                "name": profile.name,
                "invite_code": None,
            }
            if profile.invite_code is not None:
                data["invite_code"] = profile.invite_code.code

            return Response(data)

        except InviteCode.DoesNotExist:
            return JsonResponse({"code": 400, "message": "Invalid invite code.", "data": {}}, status=400)
