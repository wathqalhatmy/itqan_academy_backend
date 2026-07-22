from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.models import User
from .models import Circle, Student, Attendance, MemorizationRecord, JuzTest, Profile

class StringPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        if value is None:
            return None
        return str(value.pk)

class CircleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    teacherName = serializers.CharField(source='teacher_name')
    teacherUserId = StringPrimaryKeyRelatedField(source='teacher_user', queryset=User.objects.all(), required=False, allow_null=True)
    studentIds = serializers.SerializerMethodField()

    class Meta:
        model = Circle
        fields = ['id', 'name', 'teacherName', 'teacherUserId', 'level', 'studentIds']

    def get_studentIds(self, obj):
        return [str(s.id) for s in obj.students.all()]

    def create(self, validated_data):
        # استخراج قائمة المعرفات من البيانات الأولية
        student_ids = self.initial_data.get('studentIds', [])
        circle = Circle.objects.create(**validated_data)

        if student_ids:
            # ربط الطلاب بالحلقة الجديدة
            Student.objects.filter(id__in=student_ids).update(circle=circle)
        return circle

    def update(self, instance, validated_data):
        student_ids = self.initial_data.get('studentIds')
        
        # تحديث الحقول الأساسية
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if student_ids is not None:
            # إزالة الطلاب القدامى وإضافة الجدد (لضمان التزامن مع فلاتر)
            instance.students.update(circle=None)
            Student.objects.filter(id__in=student_ids).update(circle=instance)
            
        return instance

class StudentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    behaviorRating = serializers.FloatField(source='behavior_rating', required=False)
    completedJuz = serializers.JSONField(source='completed_juz', required=False)
    phoneNumber = serializers.CharField(source='phone_number', required=False, allow_null=True, allow_blank=True)
    circle = StringPrimaryKeyRelatedField(queryset=Circle.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Student
        fields = ['id', 'name', 'notes', 'behaviorRating', 'completedJuz', 'age', 'phoneNumber', 'status', 'circle']

class AttendanceSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    studentId = StringPrimaryKeyRelatedField(source='student', queryset=Student.objects.all())
    circleId = StringPrimaryKeyRelatedField(source='circle', queryset=Circle.objects.all())
    arrivalTime = serializers.DateTimeField(source='arrival_time', required=False, allow_null=True)

    class Meta:
        model = Attendance
        fields = ['id', 'studentId', 'circleId', 'date', 'status', 'arrivalTime', 'note']

class MemorizationRecordSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    studentId = StringPrimaryKeyRelatedField(source='student', queryset=Student.objects.all())
    circleId = StringPrimaryKeyRelatedField(source='circle', queryset=Circle.objects.all())
    surahName = serializers.CharField(source='surah_name', required=False, allow_null=True, allow_blank=True)
    fromVerse = serializers.IntegerField(source='from_verse', required=False, allow_null=True)
    toVerse = serializers.IntegerField(source='to_verse', required=False, allow_null=True)
    lessonName = serializers.CharField(source='lesson_name', required=False, allow_null=True, allow_blank=True)
    pageNumber = serializers.IntegerField(source='page_number', required=False, allow_null=True)
    tajweedRules = serializers.CharField(source='tajweed_rules', required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = MemorizationRecord
        fields = [
            'id', 'studentId', 'circleId', 'date', 'type', 'surahName',
            'fromVerse', 'toVerse', 'lessonName', 'pageNumber',
            'tajweedRules', 'grade', 'notes'
        ]

class JuzTestSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    studentId = StringPrimaryKeyRelatedField(source='student', queryset=Student.objects.all())
    circleId = StringPrimaryKeyRelatedField(source='circle', queryset=Circle.objects.all())
    juzNumber = serializers.IntegerField(source='juz_number')
    testerName = serializers.CharField(source='tester_name')

    class Meta:
        model = JuzTest
        fields = ['id', 'studentId', 'circleId', 'date', 'juzNumber', 'score', 'grade', 'testerName', 'notes']


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = f"{user.first_name} {user.last_name}".strip() or user.username
        try:
            token['role'] = user.profile.role
        except Profile.DoesNotExist:
            token['role'] = 'TEACHER'
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['name'] = f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
        try:
            data['role'] = self.user.profile.role
        except Profile.DoesNotExist:
            data['role'] = 'TEACHER'
        return data
