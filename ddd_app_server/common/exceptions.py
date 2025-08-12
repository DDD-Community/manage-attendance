from rest_framework import status

class APIException(Exception):
    """
    Custom API Exception class to handle API-specific errors.
    """
    def __init__(self, code, message, status_code=status.HTTP_400_BAD_REQUEST, data=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.data = data
        super().__init__(self.message)

    def __str__(self):
        return f"APIException: [Code: {self.code}, Message: {self.message}, Status: {self.status_code}]"

    def to_dict(self):
        return {
            "code": self.code,
            "message": self.message,
            "data": self.data
        }
    
    
class CustomAPIException(APIException):
    """
    A more specific custom API Exception for common API errors.
    """
    def __init__(self, message="An API error occurred.", status_code=status.HTTP_400_BAD_REQUEST, data=None):
        super().__init__(code=status_code, message=message, status_code=status_code, data=data)

class BadRequestException(CustomAPIException):
    def __init__(self, message="Bad Request.", data=None):
        super().__init__(message=message, status_code=status.HTTP_400_BAD_REQUEST, data=data)

class UnauthorizedException(CustomAPIException):
    def __init__(self, message="Unauthorized.", data=None):
        super().__init__(message=message, status_code=status.HTTP_401_UNAUTHORIZED, data=data)

class ForbiddenException(CustomAPIException):
    def __init__(self, message="Forbidden.", data=None):
        super().__init__(message=message, status_code=status.HTTP_403_FORBIDDEN, data=data)

class NotFoundException(CustomAPIException):
    def __init__(self, message="Not Found.", data=None):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND, data=data)

class InternalServerErrorException(CustomAPIException):
    def __init__(self, message="Internal Server Error.", data=None):
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, data=data)

class ServiceUnavailableException(CustomAPIException):
    def __init__(self, message="Service Unavailable.", data=None):
        super().__init__(message=message, status_code=status.HTTP_503_SERVICE_UNAVAILABLE, data=data)
