import datetime
from django.contrib.auth.models import User
from .models import Student, Circle, Attendance, MemorizationRecord, JuzTest

def dashboard_callback(request, context):
    # Total counts
    students_count = Student.objects.count()
    active_students_count = Student.objects.filter(status__in=['active', 'newStudent']).count()
    circles_count = Circle.objects.count()
    
    # Teachers count
    teachers_count = User.objects.filter(profile__role='TEACHER').count()
    
    # Today's attendance rate
    today = datetime.date.today()
    today_attendance = Attendance.objects.filter(date=today)
    total_marked = today_attendance.count()
    present_or_late = today_attendance.filter(status__in=['present', 'late']).count()
    
    attendance_rate = 0
    if total_marked > 0:
        attendance_rate = round((present_or_late / total_marked) * 100)
    
    # Recent activity
    recent_records = MemorizationRecord.objects.select_related('student', 'circle').order_by('-date')[:5]
    recent_tests = JuzTest.objects.select_related('student', 'circle').order_by('-date')[:5]
    
    context.update({
        "students_count": students_count,
        "active_students_count": active_students_count,
        "circles_count": circles_count,
        "teachers_count": teachers_count,
        "attendance_rate": attendance_rate,
        "recent_records": recent_records,
        "recent_tests": recent_tests,
    })
    
    return context
