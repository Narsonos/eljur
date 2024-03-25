from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test




def role_only(role,view_func=None, redirect_field_name=REDIRECT_FIELD_NAME,
                          login_url='login'):
    """
    View decorator that restricts access to a view by given role,
    Besides the user must be logged in.
    Requests to forbidden urls are redirected to login page
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_active and u.role==role,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if view_func:
        return actual_decorator(view_func)
    return actual_decorator