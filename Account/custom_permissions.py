from rest_framework.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser

class UnauthenticatedOnly(BaseException):
    def has_permission(self, request, view):
        return request.user == AnonymousUser()