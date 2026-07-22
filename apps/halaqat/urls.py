from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CircleViewSet, StudentViewSet, AttendanceViewSet,
    MemorizationRecordViewSet, JuzTestViewSet,
    halaqat_list_view, record_daily_view
)

router = DefaultRouter()
router.register(r'circles', CircleViewSet)
router.register(r'students', StudentViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'records', MemorizationRecordViewSet)
router.register(r'tests', JuzTestViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('pages/list/', halaqat_list_view, name='halaqat_list_page'),
    path('pages/record-daily/', record_daily_view, name='record_daily_page'),
]
