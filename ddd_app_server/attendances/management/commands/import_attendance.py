import csv
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from schedules.models import Schedule
from attendances.models import Attendance
from profiles.models import Profile

class Command(BaseCommand):
    help = 'Imports attendance data from a CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to import.')

    def handle(self, *args, **options):
        file_path = options['csv_file']
        self.stdout.write(self.style.SUCCESS(f'Starting attendance import from "{file_path}"...'))

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader)

                schedule_titles = [h.split('\n')[0] for h in header[4:13]]
                schedules = {}
                for title in schedule_titles:
                    try:
                        schedules[title] = Schedule.objects.get(title__icontains=title)
                    except Schedule.DoesNotExist:
                        raise CommandError(f'Schedule with title containing "{title}" does not exist.')
                    except Schedule.MultipleObjectsReturned:
                        raise CommandError(f'Multiple schedules found for title containing "{title}". Please make the title more specific.')

                for row_num, row in enumerate(reader, start=2):
                    if not any(row):
                        continue
                    
                    user_name = row[2]
                    try:
                        profile = Profile.objects.get(name=user_name)
                        user = profile.user
                    except Profile.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'WARNING: User "{user_name}" in row {row_num} not found. Skipping.'))
                        continue
                    except Profile.MultipleObjectsReturned:
                        self.stdout.write(self.style.WARNING(f'WARNING: Multiple users found for name "{user_name}" in row {row_num}. Skipping.'))
                        continue

                    for i, status_str in enumerate(row[4:13]):
                        schedule_title = schedule_titles[i]
                        schedule = schedules[schedule_title]

                        status_map = {
                            '출석': 'present',
                            '지각': 'late',
                            '불참': 'absent',
                            '병결': 'exception',
                        }
                        status = status_map.get(status_str, 'tbd')

                        if status == 'tbd' and not status_str:
                            continue

                        Attendance.objects.update_or_create(
                            user=user,
                            schedule=schedule,
                            defaults={'status': status, 'method': 'manual'}
                        )

        except FileNotFoundError:
            raise CommandError(f'File "{file_path}" not found.')

        self.stdout.write(self.style.SUCCESS('Successfully imported attendance data.'))

# sudo docker compose exec ddd_app_server python manage.py import_attendance /app/attendances/management/cleaned_attendance.csv