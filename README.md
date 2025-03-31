# DDD App Server

DDD 출석을 관리하기 위한 서버 입니다.

## 프로젝트 구조

```
ddd_app_server/
├── accounts/         # 계정 관련 도메인
├── common/          # 공통 모듈
├── invites/         # 초대 관련 도메인
├── profiles/        # 프로필 관련 도메인
├── qrcodes/         # QR 코드 관련 도메인
├── schedules/       # 일정 관련 도메인
└── ddd_app_server/  # 프로젝트 설정
```

## 기술 스택

- Python 3.11
- Django 5.1.2
- Django REST Framework 3.15.2
- PostgreSQL 15
- Nginx
- Docker & Docker Compose

## 주요 기능

- JWT 기반 인증 시스템
- 소셜 로그인 (Google, Kakao)
- QR 코드 생성 및 검증
- 프로필 관리
- 초대 시스템
- 일정 관리

## 개발 환경 설정

1. Python 가상환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. 의존성 설치
```bash
pip install -r requirements.txt
```

3. 환경 변수 설정
```bash
cp .env.template .env
# .env 파일을 편집하여 필요한 환경 변수 설정
```

4. 데이터베이스 마이그레이션
```bash
python manage.py migrate
```

5. 개발 서버 실행
```bash
python manage.py runserver
```

## Docker 환경 설정

1. Docker 이미지 빌드 및 실행
```bash
docker-compose up --build
```

2. 데이터베이스 마이그레이션
```bash
docker-compose exec ddd_app_server python manage.py migrate
```

3. 정적 파일 수집
```bash
docker-compose exec ddd_app_server python manage.py collectstatic
```

## API 문서

- Swagger UI: `/api/swagger/`
- ReDoc: `/api/redoc/`

## 배포

프로젝트는 Docker Compose를 사용하여 배포됩니다. 주요 구성 요소:

- `ddd_app_server`: Django 애플리케이션 서버
- `db`: PostgreSQL 데이터베이스
- `nginx`: 리버스 프록시 및 정적 파일 서빙

## 환경 변수

주요 환경 변수:
- `DJANGO_SETTINGS_MODULE`: Django 설정 모듈
- `DATABASE_URL`: 데이터베이스 연결 URL
- `SECRET_KEY`: Django 시크릿 키
- `ALLOWED_HOSTS`: 허용된 호스트 목록

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

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
