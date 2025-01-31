from django.shortcuts import get_object_or_404
from django.views import View
from django.http import JsonResponse
from .models import Member
from django.core.serializers import serialize
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class MemberListView(View):
    @swagger_auto_schema(
        operation_description="Retrieve a list of all members.",
        responses={200: openapi.Response(description="List of members in JSON format")}
    )
    def get(self, request):
        members = Member.objects.all()
        data = serialize("json", members)
        return JsonResponse(data, safe=False)

class MemberDetailView(View):
    @swagger_auto_schema(
        operation_description="Retrieve details of a specific member by UUID.",
        manual_parameters=[
            openapi.Parameter(
                "member_id",
                openapi.IN_PATH,
                description="UUID of the member",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
            )
        ],
        responses={200: openapi.Response(description="Member details in JSON format")}
    )
    def get(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)
        data = {
            "id": str(member.id),
            "name": member.name,
            "email": member.email,
            # Add other member fields here as necessary
        }
        return JsonResponse(data)

class MemberMemberAttendanceView(View):
    @swagger_auto_schema(
        operation_description="Retrieve MemberAttendance records for a specific member by UUID.",
        manual_parameters=[
            openapi.Parameter(
                "member_id",
                openapi.IN_PATH,
                description="UUID of the member",
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_UUID,
            )
        ],
        responses={200: openapi.Response(description="MemberAttendance records in JSON format")}
    )
    def get(self, request, member_id):
        member = get_object_or_404(Member, id=member_id)
        # MemberAttendances = MemberAttendance.objects.filter(member=member)
        data = serialize("json", member)# MemberAttendances)
        return JsonResponse(data, safe=False)
