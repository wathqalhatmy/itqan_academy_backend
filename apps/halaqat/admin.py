from django.contrib import admin
from .models import Circle, Student, Attendance, MemorizationRecord, JuzTest

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher_name', 'level')
    search_fields = ('name', 'teacher_name')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('name', 'circle', 'status', 'age')
    list_filter = ('status', 'circle')
    search_fields = ('name', 'phone_number')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'circle', 'date', 'status')
    list_filter = ('date', 'status', 'circle')

@admin.register(MemorizationRecord)
class MemorizationRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'type', 'surah_name', 'grade', 'date')
    list_filter = ('type', 'grade')

@admin.register(JuzTest)
class JuzTestAdmin(admin.ModelAdmin):
    list_display = ('student', 'juz_number', 'score', 'grade', 'date')
