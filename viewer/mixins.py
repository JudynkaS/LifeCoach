from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class CoachRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to verify that the user is a coach."""

    def test_func(self):
        return self.request.user.profile.is_coach

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied


class ClientRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to verify that the user is a client."""

    def test_func(self):
        return self.request.user.profile.is_client

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied


class OwnerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Mixin to verify that the user is the owner of the object."""

    def test_func(self):
        obj = self.get_object()
        return obj.user == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise PermissionDenied
