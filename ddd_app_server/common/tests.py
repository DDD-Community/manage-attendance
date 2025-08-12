import json
import logging
from unittest.mock import patch
from django.test import TestCase, RequestFactory
from django.http import HttpResponse
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from .middleware import StandardizedErrorMiddleware, RequestLoggingMiddleware
from .mixins import BaseResponseMixin
from .exceptions import (
    APIException,
    CustomAPIException,
    BadRequestException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    InternalServerErrorException,
    ServiceUnavailableException
)


class StandardizedErrorMiddlewareTest(TestCase):

    def setUp(self):
        self.middleware = StandardizedErrorMiddleware(lambda req: HttpResponse("OK"))
        self.factory = RequestFactory()

    def test_process_exception_api_exception(self):
        request = self.factory.get('/')
        exception = APIException(code=400, message="Test API Exception", status_code=status.HTTP_400_BAD_REQUEST)
        response = self.middleware.process_exception(request, exception)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_json['code'], 400)
        self.assertEqual(response_json['message'], "Test API Exception")

    def test_process_exception_validation_error(self):
        request = self.factory.get('/')
        exception = ValidationError({'field': 'Error message'})
        response = self.middleware.process_exception(request, exception)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_json['code'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json['message'], "유효성 검사 실패")
        self.assertEqual(response_json['data'], {'field': 'Error message'})

    def test_process_exception_integrity_error(self):
        request = self.factory.get('/')
        exception = IntegrityError("Integrity constraint violation")
        response = self.middleware.process_exception(request, exception)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response_json = json.loads(response.content.decode('utf-8'))
        self.assertEqual(response_json['code'], status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json['message'], "데이터 무결성 오류")
        self.assertEqual(response_json['data'], "Integrity constraint violation")

    def test_process_exception_generic_exception(self):
        request = self.factory.get('/')
        exception = ValueError("Generic error")
        with self.settings(DEBUG=True):
            response = self.middleware.process_exception(request, exception)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            response_json = json.loads(response.content.decode('utf-8'))
            self.assertEqual(response_json['code'], status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response_json['message'], "서버 내부 오류가 발생했습니다.")
            self.assertEqual(response_json['data'], "Generic error")

        with self.settings(DEBUG=False):
            response = self.middleware.process_exception(request, exception)
            self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            response_json = json.loads(response.content.decode('utf-8'))
            self.assertEqual(response_json['code'], status.HTTP_500_INTERNAL_SERVER_ERROR)
            self.assertEqual(response_json['message'], "서버 내부 오류가 발생했습니다.")
            self.assertIsNone(response_json['data'])


class RequestLoggingMiddlewareTest(TestCase):

    def setUp(self):
        self.middleware = RequestLoggingMiddleware(lambda req: HttpResponse("OK"))
        self.factory = RequestFactory()

    @patch('common.middleware.RequestLoggingMiddleware.logger.info')
    def test_request_logging_get(self, mock_logger_info):
        request = self.factory.get('/test-path/?param=value')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        mock_logger_info.assert_called_once()
        log_message = mock_logger_info.call_args[0][0]
        self.assertIn('GET /test-path/?param=value', log_message)
        self.assertIn('status=200', log_message)
        self.assertIn('body=', log_message)

    @patch('common.middleware.RequestLoggingMiddleware.logger.info')
    def test_request_logging_post_json(self, mock_logger_info):
        request = self.factory.post('/test-post/', data={'key': 'value'}, content_type='application/json')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        mock_logger_info.assert_called_once()
        log_message = mock_logger_info.call_args[0][0]
        self.assertIn('POST /test-post/', log_message)
        self.assertIn('status=200', log_message)
        self.assertIn('body=b\'{\"key\": \"value\"}\'', log_message)

    @patch('common.middleware.RequestLoggingMiddleware.logger.info')
    def test_request_logging_ping_request(self, mock_logger_info):
        request = self.factory.get('/ping')
        response = self.middleware(request)
        self.assertEqual(response.status_code, 200)
        mock_logger_info.assert_not_called()


class BaseResponseMixinTest(TestCase):

    class DummyAPIView(BaseResponseMixin, APIView):
        def get(self, request):
            return self.create_response(200, "Success", {'data': 'test'})

    def setUp(self):
        self.factory = RequestFactory()

    def test_create_response(self):
        request = self.factory.get('/')
        view = self.DummyAPIView()
        response = view.get(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['code'], 200)
        self.assertEqual(response.data['message'], "Success")
        self.assertEqual(response.data['data'], {'data': 'test'})


class CustomExceptionsTest(TestCase):

    def test_api_exception(self):
        exception = APIException(code=1000, message="API Error", status_code=400, data={'detail': 'error'})
        self.assertEqual(exception.code, 1000)
        self.assertEqual(exception.message, "API Error")
        self.assertEqual(exception.status_code, 400)
        self.assertEqual(exception.data, {'detail': 'error'})
        self.assertEqual(str(exception), "APIException: [Code: 1000, Message: API Error, Status: 400]")
        self.assertEqual(exception.to_dict(), {'code': 1000, 'message': 'API Error', 'data': {'detail': 'error'}})

    def test_bad_request_exception(self):
        exception = BadRequestException(message="Invalid input")
        self.assertEqual(exception.message, "Invalid input")
        self.assertEqual(exception.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_exception(self):
        exception = UnauthorizedException(message="Authentication required")
        self.assertEqual(exception.message, "Authentication required")
        self.assertEqual(exception.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_exception(self):
        exception = ForbiddenException(message="Access denied")
        self.assertEqual(exception.message, "Access denied")
        self.assertEqual(exception.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_found_exception(self):
        exception = NotFoundException(message="Resource not found")
        self.assertEqual(exception.message, "Resource not found")
        self.assertEqual(exception.status_code, status.HTTP_404_NOT_FOUND)

    def test_internal_server_error_exception(self):
        exception = InternalServerErrorException(message="Server issue")
        self.assertEqual(exception.message, "Server issue")
        self.assertEqual(exception.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_service_unavailable_exception(self):
        exception = ServiceUnavailableException(message="Service down")
        self.assertEqual(exception.message, "Service down")
        self.assertEqual(exception.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
