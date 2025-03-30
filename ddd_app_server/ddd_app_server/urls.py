from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from ddd_app_server.health import health_check

# from rest_framework.routers import DefaultRouter

# # Assuming you are using DRF viewsets
# router = DefaultRouter()

schema_view = get_schema_view(
    openapi.Info(
        title="DDD API",
        default_version='v1',
        description="API documentation for DDD application",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="cfi02222@gmail.com"),
        license=openapi.License(name="none"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# URL patterns
urlpatterns = [
    path(r'swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path(r'swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(r'redoc', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc-v1'),
    
    path("admin/", admin.site.urls),
    path("health/", health_check),
    path("auth/", include('accounts.urls')),
    
    path("invite-code/", include('invites.urls')),
    path("qrcodes/", include('qrcodes.urls')),
    path("profiles/", include('profiles.urls')),
    path("schedules/", include('schedules.urls')),
]
