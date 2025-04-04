from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import APIException
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)

class StandardizedErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # 로깅
        logger.error(f"Error occurred: {str(exception)}", exc_info=True)

        # APIException 처리
        if isinstance(exception, APIException):
            return JsonResponse({
                "code": exception.status_code,
                "message": str(exception),
                "data": getattr(exception, 'data', None)
            }, status=exception.status_code)

        # ValidationError 처리
        if isinstance(exception, ValidationError):
            return JsonResponse({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "유효성 검사 실패",
                "data": exception.message_dict if hasattr(exception, 'message_dict') else str(exception)
            }, status=status.HTTP_400_BAD_REQUEST)

        # IntegrityError 처리
        if isinstance(exception, IntegrityError):
            return JsonResponse({
                "code": status.HTTP_400_BAD_REQUEST,
                "message": "데이터 무결성 오류",
                "data": str(exception)
            }, status=status.HTTP_400_BAD_REQUEST)

        # 기타 예외 처리
        return JsonResponse({
            "code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "서버 내부 오류가 발생했습니다.",
            "data": str(exception) if settings.DEBUG else None
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 