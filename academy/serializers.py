from rest_framework import serializers
from .models import Circle, Student, Attendance, MemorizationRecord, JuzTest

class CircleSerializer(serializers.ModelSerializer):
    studentIds = serializers.SerializerMethodField()

    class Meta:
        model = Circle
        fields = ['id', 'name', 'teacher_name', 'level', 'studentIds']

    def get_studentIds(self, obj):
        return [str(s.id) for s in obj.students.all()]

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'notes', 'behavior_rating', 'completed_juz', 'age', 'phone_number', 'status', 'circle']
        # تحويل الأسماء لتطابق فلاتر (camelCase vs snake_case) سيتم التعامل معه في Mapping بسيط أو هنا
        # للتبسيط سنبقيها snake_case ونعدل DjangoRepository في فلاتر إذا لزم الأمر

class AttendanceSerializer(serializers.ModelSerializer):
    studentId = serializers.PrimaryKeyRelatedField(source='student', queryset=Student.objects.all())
    circleId = serializers.PrimaryKeyRelatedField(source='circle', queryset=Circle.objects.all())

    class Meta:
        model = Attendance
        fields = ['id', 'studentId', 'circleId', 'date', 'status', 'arrival_time', 'note']

class MemorizationRecordSerializer(serializers.ModelSerializer):
    studentId = serializers.PrimaryKeyRelatedField(source='student', queryset=Student.objects.all())
    circleId = serializers.PrimaryKeyRelatedField(source='circle', queryset=Circle.objects.all())

    class Meta:
        model = MemorizationRecord
        fields = [
            'id', 'studentId', 'circleId', 'date', 'type', 'surah_name',
            'from_verse', 'to_verse', 'lesson_name', 'page_number',
            'tajweed_rules', 'grade', 'notes'
        ]

class JuzTestSerializer(serializers.ModelSerializer):
    studentId = serializers.PrimaryKeyRelatedField(source='student', queryset=Student.objects.all())
    circleId = serializers.PrimaryKeyRelatedField(source='circle', queryset=Circle.objects.all())

    class Meta:
        model = JuzTest
        fields = ['id', 'studentId', 'circleId', 'date', 'juz_number', 'score', 'grade', 'tester_name', 'notes']
