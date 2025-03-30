from rest_framework.response import Response
from rest_framework import status

class BaseResponseMixin:
    def create_response(self, code, message, data=None, status_code=status.HTTP_200_OK):
        """
        Create a standardized API response.
        
        Args:
            code (int): Response code (usually same as HTTP status code)
            message (str): Response message
            data (dict, list, None): Response data
            status_code (int): HTTP status code
            
        Returns:
            Response: DRF Response object with standardized format
        """
        response_data = {
            "code": code,
            "message": message,
            "data": data
        }
        return Response(response_data, status=status_code) 