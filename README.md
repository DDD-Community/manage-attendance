
## 실행 커맨드
```bash
# 로컬개발
DJANGO_SETTINGS_MODULE=ddd_app_server.settings.local python manage.py runserver --settings=settings.local

# 프로덕션
## 일반 포트 사용
export DJANGO_SETTINGS_MODULE=ddd_app_server.settings.production
gunicorn ddd_app_server.wsgi:application --bind 0.0.0.0:8000
## unix 소켓 사용
export DJANGO_SETTINGS_MODULE=ddd_app_server.settings.production
gunicorn ddd_app_server.wsgi:application --bind unix:/tmp/gunicorn.sock

```

## 레퍼런스
- [셋팅 설정](https://djangostars.com/blog/configuring-django-settings-best-practices/)
- [셋팅 설정 공식](https://docs.djangoproject.com/en/5.1/topics/settings/)
- [정식 코딩 스타일](https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/)

- [웹 프로젝트](https://github.com/dddstudy/ddd-web)
- [gunicorn 설정](https://blog.hwahae.co.kr/all/tech/5567)
- [AWS gunicorn 추가](https://velog.io/@odh0112/Django-Nginx-Gunicorn-%EC%97%B0%EB%8F%99)
