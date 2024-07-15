from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrExecutorReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        if request.method in SAFE_METHODS:
            allowed = False
            if hasattr(obj, 'author'):
                allowed = obj.author_id == user_id
            elif hasattr(obj, 'executor'):
                allowed = obj.executor_id == user_id
            return allowed

        # Write permissions are only allowed to the owner of the snippet.
        elif hasattr(obj, 'author'):
            return obj.author == request.user
        return False
