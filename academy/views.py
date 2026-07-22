from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Circle, Student, Attendance, MemorizationRecord, JuzTest
from .serializers import (
    CircleSerializer, StudentSerializer, AttendanceSerializer,
    MemorizationRecordSerializer, JuzTestSerializer
)
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsAdminUser

from django.db import models
from django.db.models import Count, Avg, Q
from django.utils import timezone
import calendar

from .permissions import IsAdminUser, IsTeacherOrAdmin

class CircleViewSet(viewsets.ModelViewSet):
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            return [IsAdminUser()]
        return [IsTeacherOrAdmin()]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile'):
            return Circle.objects.none()
        if user.profile.role == 'ADMIN':
            return Circle.objects.all()
        return Circle.objects.filter(teacher_user=user)

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        circle = self.get_object()
        serializer = StudentSerializer(circle.students.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='remove-student')
    def remove_student(self, request, pk=None):
        student_id = request.data.get('student_id')
        try:
            student = Student.objects.get(id=student_id, circle_id=pk)
            student.circle = None
            student.save()
            return Response({'status': 'student removed from circle'})
        except Student.DoesNotExist:
            return Response({'error': 'Student not found in this circle'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], url_path='monthly-stats')
    def monthly_stats(self, request, pk=None):
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        circle = self.get_object()

        # تحسين الأداء: جلب الطلاب مع سجلاتهم وحضورهم بطلب واحد
        students = circle.students.prefetch_related(
            models.Prefetch(
                'attendances',
                queryset=Attendance.objects.filter(date__year=year, date__month=month, circle=circle),
                to_attr='month_attendances'
            ),
            models.Prefetch(
                'records',
                queryset=MemorizationRecord.objects.filter(date__year=year, date__month=month, circle=circle),
                to_attr='month_records'
            )
        )

        report_data = []
        for student in students:
            # Attendance Stats from prefetch
            attendance = student.month_attendances
            total_days = len(attendance)
            present_days = len([a for a in attendance if a.status in ['present', 'late']])
            absent_days = len([a for a in attendance if a.status == 'absent'])

            # Achievement Stats from prefetch
            records = student.month_records
            mem_count = len([r for r in records if r.type == 'memorization'])
            rev_count = len([r for r in records if r.type == 'revision'])

            # Mapping grades to points
            grade_map = {'excellent': 4, 'veryGood': 3, 'good': 2, 'acceptable': 1}
            total_points = sum(grade_map.get(r.grade, 0) for r in records)
            avg_grade_val = total_points / len(records) if records else 0

            report_data.append({
                'studentId': str(student.id),
                'studentName': student.name,
                'attendance': {
                    'present': present_days,
                    'absent': absent_days,
                    'rate': round((present_days / total_days * 100), 0) if total_days > 0 else 0
                },
                'achievement': {
                    'memorizationCount': mem_count,
                    'revisionCount': rev_count,
                    'avgGrade': round(avg_grade_val, 1)
                }
            })

        return Response(report_data)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if not hasattr(user, 'profile'):
            return Student.objects.none()
        if user.profile.role == 'ADMIN':
            return Student.objects.all()
        return Student.objects.filter(circle__teacher_user=user)

    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        records = MemorizationRecord.objects.filter(student_id=pk).order_by('-date')
        serializer = MemorizationRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def tests(self, request, pk=None):
        tests = JuzTest.objects.filter(student_id=pk).order_by('-date')
        serializer = JuzTestSerializer(tests, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def attendance(self, request, pk=None):
        attendance = Attendance.objects.filter(student_id=pk).order_by('-date')
        serializer = AttendanceSerializer(attendance, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='report-details')
    def report_details(self, request, pk=None):
        year = int(request.query_params.get('year', timezone.now().year))
        month = int(request.query_params.get('month', timezone.now().month))
        student = self.get_object()

        # Records for the month
        records = MemorizationRecord.objects.filter(
            student=student,
            date__year=year, date__month=month
        ).order_by('date')

        # Attendance for the month
        attendance = Attendance.objects.filter(
            student=student,
            date__year=year, date__month=month
        )
        present_days = attendance.filter(status__in=['present', 'late']).count()
        total_days = attendance.count()

        # Performance Summary
        grade_map = {'excellent': 4, 'veryGood': 3, 'good': 2, 'acceptable': 1}
        total_points = sum(grade_map.get(r.grade, 0) for r in records)
        avg_grade_val = total_points / records.count() if records.exists() else 0

        return Response({
            'studentName': student.name,
            'behaviorRating': student.behavior_rating,
            'summary': {
                'attendanceRate': round((present_days / total_days * 100), 0) if total_days > 0 else 0,
                'memorizationCount': records.filter(type='memorization').count(),
                'revisionCount': records.filter(type='revision').count(),
                'avgGrade': round(avg_grade_val, 1),
            },
            'dailyLogs': MemorizationRecordSerializer(records, many=True).data
        })

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        queryset = Attendance.objects.all()
        user = self.request.user

        if user.profile.role != 'ADMIN':
            queryset = queryset.filter(circle__teacher_user=user)

        circle_id = self.request.query_params.get('circle_id')
        date = self.request.query_params.get('date')
        if circle_id:
            queryset = queryset.filter(circle_id=circle_id)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    @action(detail=False, methods=['post'], url_path='bulk-save')
    def bulk_save(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)

        for validated_data in serializer.validated_data:
            student = validated_data.get('student')
            circle = validated_data.get('circle')
            date = validated_data.get('date')

            Attendance.objects.update_or_create(
                student=student,
                circle=circle,
                date=date,
                defaults={
                    'status': validated_data.get('status'),
                    'arrival_time': validated_data.get('arrival_time'),
                    'note': validated_data.get('note')
                }
            )
        return Response({'status': 'attendance saved'}, status=status.HTTP_200_OK)

class MemorizationRecordViewSet(viewsets.ModelViewSet):
    queryset = MemorizationRecord.objects.all()
    serializer_class = MemorizationRecordSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'ADMIN':
            return MemorizationRecord.objects.all()
        return MemorizationRecord.objects.filter(circle__teacher_user=user)

class JuzTestViewSet(viewsets.ModelViewSet):
    queryset = JuzTest.objects.all()
    serializer_class = JuzTestSerializer
    permission_classes = [IsTeacherOrAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'ADMIN':
            return JuzTest.objects.all()
        return JuzTest.objects.filter(circle__teacher_user=user)

from django.shortcuts import render
import datetime
from django.contrib.auth.models import User

def dashboard_view(request):
    # Total counts
    students_count = Student.objects.count()
    active_students_count = Student.objects.filter(status__in=['active', 'newStudent']).count()
    circles_count = Circle.objects.count()
    
    # Teachers count
    teachers_count = User.objects.filter(profile__role='TEACHER').count()
    
    # Today's attendance rate
    today = datetime.date.today()
    attendance_stats = Attendance.objects.filter(date=today).aggregate(
        total=Count('id'),
        present_or_late=Count('id', filter=Q(status__in=['present', 'late']))
    )

    total_marked = attendance_stats['total']
    present_or_late = attendance_stats['present_or_late']
    
    attendance_rate = 0
    if total_marked > 0:
        attendance_rate = round((present_or_late / total_marked) * 100)
    
    # Recent activity
    recent_records = MemorizationRecord.objects.select_related('student', 'circle').order_by('-date')[:10]
    recent_tests = JuzTest.objects.select_related('student', 'circle').order_by('-date')[:10]
    
    # All students with circle info for the directory
    students_list = Student.objects.select_related('circle').all()
    
    # All circles for circles grid
    circles_list = Circle.objects.select_related('teacher_user').all()
    
    # Calculate grade distributions for Chart.js using aggregate
    grade_stats = MemorizationRecord.objects.aggregate(
        excellent=Count('id', filter=Q(grade='excellent')),
        veryGood=Count('id', filter=Q(grade='veryGood')),
        good=Count('id', filter=Q(grade='good')),
        acceptable=Count('id', filter=Q(grade='acceptable'))
    )
    
    context = {
        "students_count": students_count,
        "active_students_count": active_students_count,
        "circles_count": circles_count,
        "teachers_count": teachers_count,
        "attendance_rate": attendance_rate,
        "recent_records": recent_records,
        "recent_tests": recent_tests,
        "students_list": students_list,
        "circles_list": circles_list,
        "grades_chart_data": [
            grade_stats['excellent'],
            grade_stats['veryGood'],
            grade_stats['good'],
            grade_stats['acceptable']
        ],
    }
    
    return render(request, 'dashboard.html', context)

@api_view(['GET'])
def dashboard_summary(request):
    """
    إرجاع إحصائيات شاملة للوحة التحكم بتنسيق JSON
    """
    user = request.user
    is_admin = hasattr(user, 'profile') and user.profile.role == 'ADMIN'

    # الإحصائيات الأساسية
    if is_admin:
        students_count = Student.objects.count()
        circles_count = Circle.objects.count()
        teachers_count = User.objects.filter(profile__role='TEACHER').count()
    else:
        # إذا كان معلماً، يرى فقط ما يخص حلقاته
        managed_circles = Circle.objects.filter(teacher_user=user)
        students_count = Student.objects.filter(circle__in=managed_circles).count()
        circles_count = managed_circles.count()
        teachers_count = 1

    # حضور اليوم
    today = datetime.date.today()
    att_qs = Attendance.objects.filter(date=today)
    if not is_admin:
        att_qs = att_qs.filter(circle__teacher_user=user)

    att_stats = att_qs.aggregate(
        total=Count('id'),
        present=Count('id', filter=Q(status__in=['present', 'late']))
    )

    # توزيع التقديرات (لآخر 30 يوم)
    last_month = timezone.now() - datetime.timedelta(days=30)
    rec_qs = MemorizationRecord.objects.filter(date__gte=last_month)
    if not is_admin:
        rec_qs = rec_qs.filter(circle__teacher_user=user)

    grade_dist = rec_qs.values('grade').annotate(count=Count('id'))

    # النشاطات الأخيرة
    recent_qs = MemorizationRecord.objects.select_related('student', 'circle').order_by('-date')
    if not is_admin:
        recent_qs = recent_qs.filter(circle__teacher_user=user)

    recent_activities = []
    for r in recent_qs[:5]:
        recent_activities.append({
            'studentName': r.student.name,
            'circleName': r.circle.name,
            'type': r.get_type_display(),
            'grade': r.get_grade_display(),
            'date': r.date.isoformat()
        })

    return Response({
        'counts': {
            'students': students_count,
            'circles': circles_count,
            'teachers': teachers_count,
        },
        'attendanceToday': {
            'total': att_stats['total'],
            'present': att_stats['present'],
            'rate': round((att_stats['present'] / att_stats['total'] * 100), 0) if att_stats['total'] > 0 else 0
        },
        'gradeDistribution': {item['grade']: item['count'] for item in grade_dist},
        'recentActivities': recent_activities,
        'isOfflineMode': False
    })

