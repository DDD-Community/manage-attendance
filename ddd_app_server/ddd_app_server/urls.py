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
        description="DDD 커뮤니티 출석 관리를 위한 API 서비스입니다.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="cfi02222@gmail.com"),
        license=openapi.License(name="none"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    
    # API v1
    path('api/v1/', include([
        path('profiles/', include('profiles.urls')),
        path('qrcodes/', include('qrcodes.urls')),
        path('schedules/', include('schedules.urls')),
        path('invites/', include('invites.urls')),
    ])),
    
    # # JWT Token Refresh
    # path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += [
        # API Documentation
        path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 