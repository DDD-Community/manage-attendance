import uuid
from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.utils.decorators import method_decorator

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from .models import InviteCode

from django.http import JsonResponse
from django.views import View
from .models import InviteCode
from members.models import Member
from datetime import timezone
import random


class InviteCodeCreateView(View):
    def post(self, request, *args, **kwargs):
        # Validate user has authorization to this action
        if not request.user.is_authenticated or not request.user.has_perm('invite.add_invitecode'):
            return JsonResponse({'code': 403, 'message': 'Permission denied.'}, status=403)

        invite_type = request.POST.get('invite_type')
        expire_time = request.POST.get('expire_time', timezone.now() + timezone.timedelta(days=365))
        one_time_use = request.POST.get('one_time_use', 'false').lower() == 'true'
        
        if invite_type not in InviteCode.INVITE_TYPE_CHOICES:
            return JsonResponse({'code': 400, 'message': 'Invalid invite type.'}, status=400)

        # Generate a unique 4-digit code
        max_attempts = 10000
        exist_codes = InviteCode.objects.filter(expire_time__gt=timezone.now()).values_list('code', flat=True)
        for _ in range(max_attempts):
            code = random.randint(0, 9999)
            if code not in exist_codes:
                break
        else:
            return JsonResponse({'code': 500, 'message': 'Failed to generate a unique invite code.'}, status=500)

        invite_code = InviteCode.objects.create(
            code=code, 
            invite_type=invite_type,
            created_by=request.user,
            expire_time=expire_time,
            one_time_use=one_time_use,
        )

        response_data = {
            'code': 201,
            'message': 'Invite code created successfully.',
            'data': {
                'code': code,
                'invite_type': invite_type,
                'created_at': invite_code.created_at.isoformat(),
            }
        }
        return JsonResponse(response_data, status=201)


class InviteCodeValidationView(View):
    # @method_decorator(swagger_auto_schema())
    def post(self, request, *args, **kwargs):
        code = request.POST.get('invite_code')
        if not code:
            return JsonResponse({'code': 400, 'message': 'Invite code is required.', 'data': {}}, status=400)

        try:
            # Get the latest invite code with the given code
            invite_code = InviteCode.objects.filter(code=code).latest('expire_time')

            # Check if the invite code is expired
            if invite_code.is_expired:
                return JsonResponse({'code': 400, 'message': 'Invite code is expired.', 'data': {}}, status=400)

            # Check if the invite code is already used
            if invite_code.one_time_use:
                # check user with the invite code
                # member = Member.objects.select_related('invite_code').get(invite_code__code=code)
                members = Member.objects.filter(invite_code__code=code)
                if members.exists():
                    return JsonResponse({'code': 400, 'message': 'Invite code is already used.', 'data': {}}, status=400)

            response_data = {
                'code': 200,
                'message': 'Invite code is valid.',
                'data': {
                    'valid': True,
                    'invite_type': invite_code.invite_type,
                    'created_by': invite_code.created_by.username,
                }
            }
            return JsonResponse(response_data, status=200)
        except InviteCode.DoesNotExist:
            return JsonResponse({'code': 400, 'message': 'Invalid invite code.', 'data': {}}, status=400)
