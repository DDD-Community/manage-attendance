import json
import os
from urllib.parse import urlencode

from django.conf import settings
from django.core.management.base import BaseCommand
from django.test import Client


class Command(BaseCommand):
    help = "Replay logged requests using Django's test client"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default=settings.REQUEST_LOG_FILE,
            help="Path to request log file",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        if not os.path.exists(file_path):
            self.stderr.write(f"File not found: {file_path}")
            return

        client = Client()
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                method = record.get("method", "get").lower()
                path = record.get("path", "/")
                params = record.get("query_params", {})
                body = record.get("body")

                url = path
                if params:
                    url = f"{path}?{urlencode(params)}"

                http_method = getattr(client, method, None)
                if not http_method:
                    self.stderr.write(f"Unsupported method: {method}")
                    continue

                if body is not None and method in {"post", "put", "patch", "delete"}:
                    response = http_method(url, data=json.dumps(body), content_type="application/json")
                else:
                    response = http_method(url)
                self.stdout.write(f"{method.upper()} {url} -> {response.status_code}")
