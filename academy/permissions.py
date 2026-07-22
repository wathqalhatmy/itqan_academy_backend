from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    صلاحية لمدراء النظام فقط.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and
                    getattr(request.user, 'profile', None) and
                    request.user.profile.role == 'ADMIN')

class IsTeacherOrAdmin(permissions.BasePermission):
    """
    صلاحية للمعلمين لرؤية بياناتهم، وللمدراء للتحكم بكل شيء.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.user.profile.role == 'ADMIN':
            return True

        # إذا كان الكائن حلقة، نتحقق من المعلم المسؤول
        if hasattr(obj, 'teacher_user'):
            return obj.teacher_user == request.user

        # إذا كان الكائن طالباً، نتحقق من حلقة الطالب
        if hasattr(obj, 'circle') and obj.circle:
            return obj.circle.teacher_user == request.user

        return False
