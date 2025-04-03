# Generated by Django 5.1.2 on 2025-04-03 08:34

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Schedule",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField()),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Attendance",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("tbd", "미정"),
                            ("present", "출석"),
                            ("late", "지각"),
                            ("absent", "결석"),
                            ("exception", "예외"),
                        ],
                        default="tbd",
                        max_length=10,
                    ),
                ),
                ("attendance_time", models.DateTimeField(blank=True, null=True)),
                (
                    "method",
                    models.CharField(
                        blank=True,
                        choices=[("qr", "QR출석"), ("manual", "수동출석")],
                        max_length=10,
                        null=True,
                    ),
                ),
                ("note", models.TextField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendances",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "schedule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="attendances",
                        to="schedules.schedule",
                    ),
                ),
            ],
            options={
                "ordering": ["-schedule__start_time"],
                "unique_together": {("user", "schedule")},
            },
        ),
    ]
