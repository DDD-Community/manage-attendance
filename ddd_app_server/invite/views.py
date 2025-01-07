from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import InviteCode
import uuid
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class InviteCodeCreateView(View):
    @method_decorator(swagger_auto_schema(
        operation_description="Create new invitation code.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'invite_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['normal', 'moderator'], description='Invite code type (normal or moderator)'),
            },
            required=['invite_type']
        ),
        responses={
            201: openapi.Response(
                description='Invitation code created successfully.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'code': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'code': openapi.Schema(type=openapi.TYPE_STRING, description='The generated invite code.'),
                                'invite_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['normal', 'moderator'], description='The type of invite code.'),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description='Bad request data'),
            401: openapi.Response(description='Authentication failure')
        }
    ))
    def post(self, request, *args, **kwargs):
        # TODO validate user has authorization to this action
        invite_type = request.POST.get('invite_type')
        if invite_type not in ['normal', 'moderator']:
            return JsonResponse({'code': 400, 'message': 'Invalid invite type.'}, status=400)

        # Create the invite code
        invite_code = secret.random(0~9999)  # Generate a simple 4-number code, check if not exists
        InviteCode.objects.create(code=invite_code, invite_type=invite_type)

        response_data = {
            'code': 201,
            'message': 'Invite code created successfully.',
            'data': {
                'code': invite_code,
                'invite_type': invite_type
            }
        }
        return JsonResponse(response_data, status=201)


class InviteCodeValidationView(View):
    @method_decorator(swagger_auto_schema(
        operation_description="Validate invitation code.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'invite_code': openapi.Schema(type=openapi.TYPE_STRING, description='The invitation code to validate.'),
            },
            required=['invite_code']
        ),
        responses={
            200: openapi.Response(
                description='Invitation code is valid.',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'code': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'valid': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Indicates if the invite code is valid.'),
                                'invite_type': openapi.Schema(type=openapi.TYPE_STRING, enum=['normal', 'moderator'], description='Invite type (normal or moderator).'),
                            }
                        )
                    }
                )
            ),
            400: openapi.Response(description='Invalid invite code')
        }
    ))
    def post(self, request, *args, **kwargs):
        invite_code = request.POST.get('invite_code')
        if not invite_code:
            return JsonResponse({'code': 400, 'message': 'Invite code is required.'}, status=400)

        try:
            invite = InviteCode.objects.get(code=invite_code)
            response_data = {
                'code': 200,
                'message': 'Invite code is valid.',
                'data': {
                    'valid': True,
                    'invite_type': invite.invite_type
                }
            }
            return JsonResponse(response_data, status=200)
        except InviteCode.DoesNotExist:
            return JsonResponse({'code': 400, 'message': 'Invalid invite code.'}, status=400)