from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from academy.serializers import CustomTokenObtainPairSerializer
from academy.views import dashboard_view

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

urlpatterns = [
    path('', dashboard_view, name='dashboard'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('academy.urls')),
    path('api/v1/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
