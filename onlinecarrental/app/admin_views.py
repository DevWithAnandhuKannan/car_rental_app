from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User

# Admin Login View
def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # Allow only admin users
            login(request, user)
            # Store user ID in session
            request.session['admin_id'] = user.id
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, 'admin/admin_login.html')

# Admin Dashboard (Protected)
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('admin_login')
    
    total_users = User.objects.count()
    return render(request, 'admin/admin_dashboard.html', {'total_users': total_users})

# Admin Logout View
@login_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')
