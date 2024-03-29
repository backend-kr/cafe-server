from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import BasePermission, IsAdminUser
from common.permissions import ModelPermissions
from common.permissions import IsOwnerOrAdminUser, IsOwner
from common.exceptions import PreconditionFailed
from common.utils import DotDict

class AcceptMultipleOrPermissionMixin(object):
    def check_permissions(self, request):
        perms = self.get_permissions()
        has_perms = [permission.has_permission(request, self) for permission in perms]

        if True not in has_perms:
            for permission in perms:
                if not permission.has_permission(request, self):
                    self.permission_denied(
                        request, message=getattr(permission, 'message', None)
                    )


class AcceptObjectOrPermissionMixin(BasePermission):
    def check_object_permissions(self, request, obj):
        perms = self.get_permissions()
        has_perms = [permission.has_permission(request, self) for permission in perms]

        if True not in has_perms:
            for permission in perms:
                if not permission.has_object_permission(request, self, obj):
                    self.permission_denied(
                        request, message=getattr(permission, 'message', None)
                    )


class MappingViewSetMixin(object):
    serializer_action_map = {}
    permission_classes_map = {}
    queryset_map = {}

    def get_queryset(self):
        return self.queryset_map.get(self.action, self.queryset)


    def get_permissions(self):
        permission_classes = self.permission_classes
        if self.permission_classes_map.get(self.action, None):
            permission_classes = self.permission_classes_map[self.action]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.serializer_action_map.get(self.action, None):
            return self.serializer_action_map[self.action]
        return self.serializer_class


class AdminOrUserQuerySetMixin(object):
    def get_queryset(self):
        if not self.request.user.is_staff:
            return self.queryset.filter(user=self.request.user)
        return self.queryset


class UserQuerySetMixin(object):
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class AcceptMultiplePermissionMixin(AcceptMultipleOrPermissionMixin, AcceptObjectOrPermissionMixin):
    pass


class MultiPermsModelViewSet(AcceptMultipleOrPermissionMixin, ModelViewSet):
    """
    Acceptable Multiple Permissions.
    """
    pass


class IsSuperUser(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class AdminViewSetMixin(AcceptMultipleOrPermissionMixin):
    permission_classes = [IsSuperUser, ModelPermissions]


class CreateListMixin:
    """Allows bulk creation of a resource."""

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get('data', {}), list):
            kwargs['many'] = True

        return super().get_serializer(*args, **kwargs)
