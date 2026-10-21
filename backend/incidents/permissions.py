from rest_framework.permissions import BasePermission


class IsResponder(BasePermission):
    """Only responders may use this endpoint (taking a case)."""

    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and u.role == 'responder'


class IsAssignedResponderOrAdmin(BasePermission):
    """Managing workers: the responder who owns the incident, or an admin."""

    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and u.role in ('responder', 'admin')

    def has_object_permission(self, request, view, obj):
        u = request.user
        return u.role == 'admin' or obj.assigned_to_id == u.id


class IsOnIncidentOrAdmin(BasePermission):
    """Resolving: the owning responder, a worker on the incident, or an admin."""

    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and u.role in ('responder', 'worker', 'admin')

    def has_object_permission(self, request, view, obj):
        u = request.user
        if u.role == 'admin':
            return True
        if u.role == 'responder':
            return obj.assigned_to_id == u.id
        if u.role == 'worker':
            return obj.workers.filter(pk=u.pk).exists()
        return False


class CanAddImages(BasePermission):
    """Reporter, assigned responder, a worker on the incident, or an admin."""

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        u = request.user
        return (
            u.role == 'admin'
            or obj.reporter_id == u.id
            or obj.assigned_to_id == u.id
            or obj.workers.filter(pk=u.pk).exists()
        )