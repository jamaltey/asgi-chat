from rest_framework.permissions import BasePermission

class IsAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.method in ['PUT', 'PATCH', 'DELETE']:
            return True
        return obj.author == request.user
