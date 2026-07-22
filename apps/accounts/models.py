from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'مشرف عام'),
        ('teacher', 'معلم/شيخ'),
        ('student', 'طالب'),
        ('parent', 'ولي أمر'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='teacher', verbose_name='الدور/الصلاحية')
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='رقم الجوال')
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True, verbose_name='الصورة الشخصية')

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"
