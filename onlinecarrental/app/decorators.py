from django.shortcuts import redirect

def login_required_session(view_func):
    """
    Decorator to check if the user has a valid session.
    Redirects to login page if not authenticated.
    """
    def wrapper(request, *args, **kwargs):
        if 'user_id' not in request.session:
            return redirect('login')  # Redirect to login if user is not authenticated
        return view_func(request, *args, **kwargs)
    return wrapper
