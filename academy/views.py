from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Circle, Student, Attendance, MemorizationRecord, JuzTest
from .serializers import (
    CircleSerializer, StudentSerializer, AttendanceSerializer,
    MemorizationRecordSerializer, JuzTestSerializer
)

class CircleViewSet(viewsets.ModelViewSet):
    queryset = Circle.objects.all()
    serializer_class = CircleSerializer

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

class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer

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
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        queryset = Attendance.objects.all()
        circle_id = self.request.query_params.get('circle_id')
        date = self.request.query_params.get('date')
        if circle_id:
            queryset = queryset.filter(circle_id=circle_id)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    @action(detail=False, methods=['post'], url_path='bulk-save')
    def bulk_save(self, request):
        data = request.data
        if not isinstance(data, list):
            return Response({'error': 'Expected a list of attendance records'}, status=status.HTTP_400_BAD_REQUEST)

        for item in data:
            student_id = item.get('studentId')
            circle_id = item.get('circleId')
            date = item.get('date').split('T')[0]

            Attendance.objects.update_or_create(
                student_id=student_id,
                circle_id=circle_id,
                date=date,
                defaults={
                    'status': item.get('status'),
                    'arrival_time': item.get('arrivalTime'),
                    'note': item.get('note')
                }
            )
        return Response({'status': 'attendance saved'})

class MemorizationRecordViewSet(viewsets.ModelViewSet):
    queryset = MemorizationRecord.objects.all()
    serializer_class = MemorizationRecordSerializer

class JuzTestViewSet(viewsets.ModelViewSet):
    queryset = JuzTest.objects.all()
    serializer_class = JuzTestSerializer
