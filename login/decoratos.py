from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def staff_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('staff_id'):
            messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
            return redirect('login_staff')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
