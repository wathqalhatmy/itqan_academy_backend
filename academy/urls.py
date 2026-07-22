from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CircleViewSet, StudentViewSet, AttendanceViewSet,
    MemorizationRecordViewSet, JuzTestViewSet
)
from . import views

router = DefaultRouter()
router.register(r'circles', CircleViewSet)
router.register(r'students', StudentViewSet)
router.register(r'attendance', AttendanceViewSet)
router.register(r'records', MemorizationRecordViewSet)
router.register(r'tests', JuzTestViewSet)

urlpatterns = [
    path('dashboard/summary/', views.dashboard_summary, name='dashboard-summary'),
    path('', include(router.urls)),
]
