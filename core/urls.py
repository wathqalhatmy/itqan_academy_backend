from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render

# Customize Django Admin Header and Titles
admin.site.site_header = "إدارة إتقان أكاديمي"
admin.site.site_title = "إتقان أكاديمي"
admin.site.index_title = "مرحباً بك في لوحة تحكم إتقان أكاديمي"

def landing_page(request):
    return render(request, 'index.html')

urlpatterns = [
    path('', landing_page, name='home'),
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/halaqat/', include('apps.halaqat.urls')),
    path('api/v1/', include('apps.halaqat.urls')),  # Backward compatibility
    path('api/v1/reports/', include('apps.reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
