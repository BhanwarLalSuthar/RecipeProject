from rest_framework.permissions import BasePermission

class IsInstructor(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.user_type == 'author'

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.userprofile.user_type == 'customer'

class IsAssignedToCourse(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.userprofile.user_type == 'author':
            return True
        if request.user.userprofile.user_type == 'customer':
            print("hello")
            return obj.recipe.customer.filter(id=request.user.id).exists()
        return False