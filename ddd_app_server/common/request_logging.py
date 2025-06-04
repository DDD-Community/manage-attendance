import json
import os
from django.conf import settings


class RequestLoggingMiddleware:
    """Middleware that logs incoming HTTP requests."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, "ENABLE_REQUEST_LOGGING", False)
        self.log_file = getattr(
            settings,
            "REQUEST_LOG_FILE",
            os.path.join(settings.BASE_DIR, "logs", "request_logs.jsonl"),
        )
        if self.enabled:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

    def __call__(self, request):
        if self.enabled:
            self.log_request(request)
        response = self.get_response(request)
        return response

    def log_request(self, request):
        data = {
            "method": request.method,
            "path": request.path,
            "headers": {k: v for k, v in request.headers.items()},
            "query_params": request.GET.dict(),
            "body": self.get_body(request),
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def get_body(self, request):
        if not request.body:
            return None
        try:
            return json.loads(request.body.decode("utf-8"))
        except Exception:
            try:
                return request.body.decode("utf-8")
            except Exception:
                return str(request.body)
