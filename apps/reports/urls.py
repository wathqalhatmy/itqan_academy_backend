from django.urls import path
from .views import dashboard_view, DashboardStatsAPIView

urlpatterns = [
    path('dashboard/', dashboard_view, name='reports_dashboard_page'),
    path('stats/', DashboardStatsAPIView.as_view(), name='reports_stats_api'),
]
