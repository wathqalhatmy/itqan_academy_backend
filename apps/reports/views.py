from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count
from apps.halaqat.models import Circle, Student, Attendance, MemorizationRecord, JuzTest

def dashboard_view(request):
    return render(request, 'reports/dashboard.html')

class DashboardStatsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_circles = Circle.objects.count()
        total_students = Student.objects.count()
        active_students = Student.objects.filter(status='active').count()
        total_records = MemorizationRecord.objects.count()
        total_tests = JuzTest.objects.count()
        avg_behavior = Student.objects.aggregate(Avg('behavior_rating'))['behavior_rating__avg'] or 5.0
        attendance_stats = Attendance.objects.values('status').annotate(count=Count('id'))

        return Response({
            'total_circles': total_circles,
            'total_students': total_students,
            'active_students': active_students,
            'total_records': total_records,
            'total_tests': total_tests,
            'avg_behavior_rating': round(avg_behavior, 2),
            'attendance_breakdown': list(attendance_stats)
        })
