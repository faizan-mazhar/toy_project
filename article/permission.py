from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class EditorRequiredMixin(LoginRequiredMixin):

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
    
        if not getattr(request.user, 'is_editor', False):
            raise PermissionDenied(
                "You must be an editor to access this page."
                )

        return super().dispatch(request, *args, **kwargs)
