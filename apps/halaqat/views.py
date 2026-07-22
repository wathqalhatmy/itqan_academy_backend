from django.db import transaction
from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Circle, Student, Attendance, MemorizationRecord, JuzTest
from .serializers import (
    CircleSerializer, StudentSerializer, AttendanceSerializer,
    MemorizationRecordSerializer, JuzTestSerializer
)

def halaqat_list_view(request):
    return render(request, 'halaqat/list.html')

def record_daily_view(request):
    return render(request, 'halaqat/record_daily.html')

class CircleViewSet(viewsets.ModelViewSet):
    queryset = Circle.objects.prefetch_related('students').all()
    serializer_class = CircleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'teacher_name', 'level']
    ordering_fields = ['name', 'id', 'level']
    ordering = ['id']

    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        circle = self.get_object()
        serializer = StudentSerializer(circle.students.all(), many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='remove-student')
    def remove_student(self, request, pk=None):
        student_id = request.data.get('student_id')
        if not student_id:
            return Response({'error': 'student_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            student = Student.objects.get(id=student_id, circle_id=pk)
            student.circle = None
            student.save()
            return Response({'status': 'student removed from circle'})
        except Student.DoesNotExist:
            return Response({'error': 'Student not found in this circle'}, status=status.HTTP_404_NOT_FOUND)

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('circle').all()
    serializer_class = StudentSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'phone_number', 'notes']
    ordering_fields = ['name', 'behavior_rating', 'age', 'id', 'status']
    ordering = ['id']

    def get_queryset(self):
        queryset = super().get_queryset()
        circle_id = self.request.query_params.get('circle_id')
        status_filter = self.request.query_params.get('status')
        if circle_id:
            queryset = queryset.filter(circle_id=circle_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

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

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('student', 'circle').all()
    serializer_class = AttendanceSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date', 'id']
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        circle_id = self.request.query_params.get('circle_id')
        student_id = self.request.query_params.get('student_id')
        date = self.request.query_params.get('date')
        if circle_id:
            queryset = queryset.filter(circle_id=circle_id)
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    @action(detail=False, methods=['post'], url_path='bulk-save')
    def bulk_save(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({'error': 'Expected a list of attendance records'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                for item in data:
                    student_id = item.get('studentId') or item.get('student_id')
                    circle_id = item.get('circleId') or item.get('circle_id')
                    raw_date = item.get('date')

                    if not student_id or not circle_id or not raw_date:
                        raise ValueError(f"Each attendance record must contain studentId, circleId, and date. Problem item: {item}")

                    date_clean = str(raw_date).split('T')[0]

                    Attendance.objects.update_or_create(
                        student_id=student_id,
                        circle_id=circle_id,
                        date=date_clean,
                        defaults={
                            'status': item.get('status', 'unmarked'),
                            'arrival_time': item.get('arrivalTime') or item.get('arrival_time'),
                            'note': item.get('note')
                        }
                    )
        except ValueError as ve:
            return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as exc:
            return Response({'error': f"Failed to save attendance records: {str(exc)}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'attendance saved'}, status=status.HTTP_200_OK)

class MemorizationRecordViewSet(viewsets.ModelViewSet):
    queryset = MemorizationRecord.objects.select_related('student', 'circle').all()
    serializer_class = MemorizationRecordSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['surah_name', 'lesson_name', 'notes']
    ordering_fields = ['date', 'grade', 'id']
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        circle_id = self.request.query_params.get('circle_id')
        record_type = self.request.query_params.get('type')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if circle_id:
            queryset = queryset.filter(circle_id=circle_id)
        if record_type:
            queryset = queryset.filter(type=record_type)
        return queryset

class JuzTestViewSet(viewsets.ModelViewSet):
    queryset = JuzTest.objects.select_related('student', 'circle').all()
    serializer_class = JuzTestSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['tester_name', 'notes']
    ordering_fields = ['date', 'score', 'juz_number', 'id']
    ordering = ['-id']

    def get_queryset(self):
        queryset = super().get_queryset()
        student_id = self.request.query_params.get('student_id')
        circle_id = self.request.query_params.get('circle_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if circle_id:
            queryset = queryset.filter(circle_id=circle_id)
        return queryset
