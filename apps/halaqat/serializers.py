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
    behaviorRating = serializers.FloatField(source='behavior_rating', required=False)
    completedJuz = serializers.JSONField(source='completed_juz', required=False)
    phoneNumber = serializers.CharField(source='phone_number', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Student
        fields = [
            'id', 'name', 'notes', 'behavior_rating', 'completed_juz', 'age', 'phone_number', 'status', 'circle',
            'behaviorRating', 'completedJuz', 'phoneNumber'
        ]
        extra_kwargs = {
            'behavior_rating': {'required': False},
            'completed_juz': {'required': False},
            'phone_number': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

    def validate_completed_juz(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError("completed_juz must be a list of integers.")
        for item in value:
            if not isinstance(item, int) or item < 1 or item > 30:
                raise serializers.ValidationError("Each juz number must be an integer between 1 and 30.")
        return value

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

    def validate(self, data):
        from_verse = data.get('from_verse')
        to_verse = data.get('to_verse')
        if from_verse is not None and to_verse is not None:
            if from_verse > to_verse:
                raise serializers.ValidationError({"to_verse": "to_verse must be greater than or equal to from_verse."})
        return data

class JuzTestSerializer(serializers.ModelSerializer):
    studentId = serializers.PrimaryKeyRelatedField(source='student', queryset=Student.objects.all())
    circleId = serializers.PrimaryKeyRelatedField(source='circle', queryset=Circle.objects.all())

    class Meta:
        model = JuzTest
        fields = ['id', 'studentId', 'circleId', 'date', 'juz_number', 'score', 'grade', 'tester_name', 'notes']
