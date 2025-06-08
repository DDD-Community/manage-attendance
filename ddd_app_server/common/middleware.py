import re
import time
import json
import logging
from datetime import datetime, UTC
from rest_framework import status
from rest_framework.exceptions import APIException
from django.db import IntegrityError
from django.http import JsonResponse
from django.conf import settings
from django.core.exceptions import ValidationError


class StandardizedErrorMiddleware:
    logger = logging.getLogger('standardized_error')
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        # 로깅
        self.logger.exception(f"Error occurred: {str(exception)}", exc_info=True)

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


class RequestLoggingMiddleware:
    logger = logging.getLogger("request_logging")
    ping_reg = re.compile(r".*/ping$")

    def __init__(self, get_response=None):
        self.get_response = get_response

    def is_ping_req(self, path):
        return True if self.ping_reg.match(path) else False

    @staticmethod
    def _headers(request):
        return {
            key: value
            for (key, value) in request.META.items()
            if key.startswith("HTTP_")
        }

    def __call__(self, request):
        request_at = time.time()

        body = ""
        if request.method in ["POST", "PATCH"] and request.content_type == "application/json":
            body = request.body
        response = self.get_response(request)
        if self.is_ping_req(request.get_full_path()):
            return response

        elapsed_time = round(time.time() - request_at, 3)
        tag = "-"
        if elapsed_time > 1:
            tag = "SLOW_API"

        self.logger.info(
            f"{datetime.now(UTC)} ACCESS LOG {tag} {request.method} {request.get_full_path()} "
            f"status={response.status_code} elapsed={elapsed_time} headers={self._headers(request)} "
            f"body={body}"
        )

        return response
