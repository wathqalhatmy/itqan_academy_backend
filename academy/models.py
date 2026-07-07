from django.db import models

class Circle(models.Model):
    LEVEL_CHOICES = [
        ('memorization', 'حفظ ومراجعة'),
        ('tajweed', 'قراءة وتجويد'),
        ('alphabets', 'قراءة وكتابة'),
    ]

    name = models.CharField(max_length=200, verbose_name="اسم الحلقة")
    teacher_name = models.CharField(max_length=200, verbose_name="اسم المعلم")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='memorization', verbose_name="المستوى")

    def __str__(self):
        return self.name

class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'نشط'),
        ('newStudent', 'مستجد'),
        ('suspended', 'موقوف'),
        ('graduated', 'خريج'),
    ]

    name = models.CharField(max_length=200, verbose_name="اسم الطالب")
    notes = models.TextField(blank=True, default="", verbose_name="ملاحظات")
    behavior_rating = models.FloatField(default=5.0, verbose_name="تقييم السلوك")
    completed_juz = models.JSONField(default=list, verbose_name="الأجزاء المجتازة")
    age = models.IntegerField(null=True, blank=True, verbose_name="العمر")
    phone_number = models.CharField(max_length=20, null=True, blank=True, verbose_name="رقم الهاتف")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="الحالة")
    circle = models.ForeignKey(Circle, on_delete=models.SET_NULL, null=True, blank=True, related_name="students", verbose_name="الحلقة")

    def __str__(self):
        return self.name

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', 'حاضر'),
        ('absent', 'غائب'),
        ('excused', 'غائب بعذر'),
        ('late', 'متأخر'),
        ('unmarked', 'غير محضر'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name="attendances")
    date = models.DateField(verbose_name="التاريخ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unmarked')
    arrival_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت الوصول")
    note = models.TextField(blank=True, null=True, verbose_name="ملاحظة الحضور")

    class Meta:
        unique_together = ('student', 'circle', 'date')

class MemorizationRecord(models.Model):
    RECORD_TYPE_CHOICES = [
        ('memorization', 'حفظ جديد'),
        ('revision', 'مراجعة'),
        ('recitation', 'تلاوة'),
        ('alphabets', 'تهجي وقراءة'),
    ]

    GRADE_CHOICES = [
        ('excellent', 'ممتاز'),
        ('veryGood', 'جيد جداً'),
        ('good', 'جيد'),
        ('acceptable', 'مقبول'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="records")
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name="records")
    date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")
    type = models.CharField(max_length=20, choices=RECORD_TYPE_CHOICES)
    surah_name = models.CharField(max_length=100, null=True, blank=True)
    from_verse = models.IntegerField(null=True, blank=True)
    to_verse = models.IntegerField(null=True, blank=True)
    lesson_name = models.CharField(max_length=200, null=True, blank=True)
    page_number = models.IntegerField(null=True, blank=True)
    tajweed_rules = models.TextField(null=True, blank=True)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES)
    notes = models.TextField(null=True, blank=True)

class JuzTest(models.Model):
    GRADE_CHOICES = [
        ('excellent', 'ممتاز'),
        ('veryGood', 'جيد جداً'),
        ('good', 'جيد'),
        ('acceptable', 'مقبول'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="tests")
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name="tests")
    date = models.DateTimeField(auto_now_add=True)
    juz_number = models.IntegerField(verbose_name="رقم الجزء")
    score = models.FloatField(verbose_name="الدرجة")
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES)
    tester_name = models.CharField(max_length=200)
    notes = models.TextField(null=True, blank=True)
