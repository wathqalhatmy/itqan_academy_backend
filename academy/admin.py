from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Circle, Student, Attendance, MemorizationRecord, JuzTest, Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'إحصائيات الدور (Profile)'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

# إعادة تسجيل الـ User ليتضمن الـ Profile
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, UserAdmin)

@admin.register(Circle)
class CircleAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher_user', 'level')
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


