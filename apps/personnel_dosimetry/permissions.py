from rest_framework import permissions
from .models import PersonnelDosimetryUsers


class IsLocalPersonnelDosimetryAdministrator(permissions.BasePermission):
    """
    Custom permission to only allow local personnel dosimetry administrators to see sensitive personnel information for
    a specific clinic
    """
    def has_object_permission(self, request, view, obj):
        return True


class IsPersonnelDosimetryAdministrator(permissions.BasePermission):
    """
    Custom permission to only allow personnel dosimetry administrator to handle all personnel dosimetry info
    """
    def has_permission(self, request, view):
        pd_user = PersonnelDosimetryUsers.objects.filter(
            user_id=request.user, personnel_dosimetry_admin__exact=True).count()

        return pd_user > 0
