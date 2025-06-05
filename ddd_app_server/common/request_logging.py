import logging
import re
import time
from datetime import datetime, UTC


logger = logging.getLogger(__name__)


class RequestLoggingMiddleware:
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
        if request.method == "POST" and request.content_type == "application/json":
            body = request.body
        response = self.get_response(request)
        if self.is_ping_req(request.get_full_path()):
            return response

        elapsed_time = round(time.time() - request_at, 3)
        tag = "-"
        if elapsed_time > 1:
            tag = "SLOW_API"

        logger.info(
            f"{datetime.now(UTC)} ACCESS LOG {tag} {request.method} {request.get_full_path()} "
            f"status={response.status_code} elapsed={elapsed_time} headers={self._headers(request)} "
            f"body={body}"
        )

        return response
