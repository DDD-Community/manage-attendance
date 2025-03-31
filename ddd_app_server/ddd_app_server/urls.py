from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from ddd_app_server.health import health_check

schema_view = get_schema_view(
    openapi.Info(
        title="DDD Attendance Management API",
        default_version='v1',
        description="""
            DDD 커뮤니티 출석 관리를 위한 API 서비스입니다.
            
            ## 주요 기능
            - JWT 기반 인증
            - 소셜 로그인 (Google, Kakao)
            - QR 코드 생성 및 검증
            - 프로필 관리
            - 초대 시스템
            - 일정 관리
            
            ## 응답 형식
            모든 API 응답은 다음 형식을 따릅니다:
            ```json
            {
              "code": 200,
              "message": "작업 성공 메시지",
              "data": { ... }
            }
            ```
            
            ## 에러 코드
            - 200: 성공
            - 201: 생성 성공
            - 400: 잘못된 요청
            - 401: 인증 실패
            - 403: 권한 없음
            - 404: 리소스 없음
            - 500: 서버 에러
        """,
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="cfi02222@gmail.com"),
        license=openapi.License(name="none"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("health/", health_check),
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    
    # API v1
    path('api/v1/', include([
        path('profiles/', include('profiles.urls')),
        path('qrcodes/', include('qrcodes.urls')),
        path('schedules/', include('schedules.urls')),
        path('invites/', include('invites.urls')),
    ])),
    
    # # JWT Token Refresh
    # path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 