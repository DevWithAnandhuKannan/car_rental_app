import json
import string
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password, make_password
from functools import wraps
from django.views.generic import TemplateView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Address, Customer, Order, Review, Vehicle
from .models import SparePart
from django.contrib import messages
from .models import Vehicle, Booking
from datetime import datetime
from django.utils import timezone
from django.db.models import Sum, Count
import random
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
import json
from .models import SparePart, Customer, Address, Order
import requests
from django.shortcuts import redirect
from django.contrib import messages
import json
import requests
from django.http import JsonResponse
from django.shortcuts import render
from functools import wraps



def check_admin_log(request):
    return 'admin_id' in request.session

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if check_admin_log(request):
            return view_func(request, *args, **kwargs)
        return redirect('admin:admin_login') 
    return wrapper

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin:admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  
            login(request, user)
            request.session['admin_id'] = user.id
            return redirect('admin:admin_dashboard')
        else:
            messages.error(request, "Invalid credentials or not an admin.")

    return render(request, 'admin/admin_login.html')

@admin_required
def admin_dashboard(request):
    # Vehicle Statistics
    total_vehicles = Vehicle.objects.count()
    available_vehicles = Vehicle.objects.filter(availability='Available').count()
    booked_vehicles = Vehicle.objects.filter(availability='Booked').count()
    
    # Customer Statistics
    total_customers = Customer.objects.count()
    new_customers = Customer.objects.filter(user__date_joined__gte=timezone.now().date() - timedelta(days=30)).count()
    
    # Booking Statistics
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(booking_status='Confirmed', return_status='Pending').count()
    total_revenue = Booking.objects.filter(payment_status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Order Statistics
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(order_status='Pending').count()
    total_parts_revenue = Order.objects.filter(payment_status='Paid').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    # Chart Data
    booking_status_data = Booking.objects.values('booking_status').annotate(count=Count('id'))
    vehicle_type_data = Vehicle.objects.values('vehicle_type').annotate(count=Count('id'))
    
    context = {
        'total_vehicles': total_vehicles,
        'available_vehicles': available_vehicles,
        'booked_vehicles': booked_vehicles,
        'total_customers': total_customers,
        'new_customers': new_customers,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_parts_revenue': total_parts_revenue,
        'booking_status_data': list(booking_status_data),
        'vehicle_type_data': list(vehicle_type_data),
    }
    
    return render(request, 'admin/admin_dashboard.html', context)

@admin_required
def admin_logout(request):
    logout(request)
    if 'admin_id' in request.session:
        del request.session['admin_id']
    return redirect('admin:admin_login')

@admin_required
def add_vehicle(request):
    if request.method == "POST":
        required_fields = ['brand', 'model', 'number_plate', 'price_per_day', 'mileage', 'fuel_type', 'transmission_type', 'availability']
        
        missing_fields = [field for field in required_fields if not request.POST.get(field, '').strip()]
        if missing_fields:
            for field in missing_fields:
                messages.error(request, f"{field.replace('_', ' ').capitalize()} is required.")
            return redirect('user:vehicle_list')
        
        image = request.FILES.get('image')
        
        Vehicle.objects.create(
            brand=request.POST['brand'].strip(),
            model=request.POST['model'].strip(),
            number_plate=request.POST['number_plate'].strip(),
            price_per_day=request.POST['price_per_day'],
            mileage=request.POST['mileage'],
            fuel_type=request.POST['fuel_type'],
            transmission_type=request.POST['transmission_type'],
            availability=request.POST['availability'],
            vehicle_type=request.POST['vehicle_type'],
            features=request.POST['features'],
            image=image
        )
        messages.success(request, "Vehicle added successfully!")
        return redirect('user:vehicle_list')
    
    return render(request, 'admin/add_vehicle.html')

@admin_required
def update_vehicle(request, vehicle_id):
    print('called update vehicle')
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == "POST":
        required_fields = ['brand', 'model', 'number_plate', 'price_per_day', 'mileage', 'fuel_type', 'transmission_type', 'availability']
        
        missing_fields = [field for field in required_fields if not request.POST.get(field, '').strip()]
        if missing_fields:
            for field in missing_fields:
                messages.error(request, f"{field.replace('_', ' ').capitalize()} is required.")
            return redirect('user:vehicle_list')
        
        vehicle.brand = request.POST['brand'].strip()
        vehicle.model = request.POST['model'].strip()
        vehicle.number_plate = request.POST['number_plate'].strip()
        vehicle.price_per_day = request.POST['price_per_day']
        vehicle.mileage = request.POST['mileage']
        vehicle.fuel_type = request.POST['fuel_type']
        vehicle.transmission_type = request.POST['transmission_type']
        vehicle.availability = request.POST['availability']
        vehicle.vehicle_type=request.POST['vehicle_type'],
        vehicle.features=request.POST['features'],
        
        if 'image' in request.FILES:
            vehicle.image = request.FILES['image']

        vehicle.save()
        messages.success(request, "Vehicle updated successfully!")
        return redirect('user:vehicle_list')

    return render(request, 'admin/update_vehicle.html', {'vehicle': vehicle})

@admin_required
def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    messages.success(request, "Vehicle deleted successfully!")
    return redirect('user:vehicle_list')

def add_spare_part(request):
    if request.method == 'POST':
        part_name = request.POST.get('part_name')
        category = request.POST.get('category')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        car_compatibility = request.POST.get('car_compatibility')
        sku = request.POST.get('sku')

        SparePart.objects.create(
            part_name=part_name,
            category=category,
            price=price,
            stock_quantity=stock_quantity,
            description=description,
            image=image,
            car_compatibility=car_compatibility,
            sku=sku
        )
        return redirect('user:spare_parts_list')
    
    return render(request, 'admin/spare_parts.html', {'action': 'Add'})

@admin_required
def update_spare_part(request, part_id):
    spare_part = get_object_or_404(SparePart, id=part_id)

    if request.method == 'POST':
        spare_part.part_name = request.POST.get('part_name')
        spare_part.category = request.POST.get('category')
        spare_part.price = request.POST.get('price')
        spare_part.stock_quantity = request.POST.get('stock_quantity')
        spare_part.description = request.POST.get('description')
        spare_part.image = request.FILES.get('image', spare_part.image)
        spare_part.car_compatibility = request.POST.get('car_compatibility')
        spare_part.sku = request.POST.get('sku')
        spare_part.save()
        return redirect('user:spare_parts_list')

    return render(request, 'admin/spare_parts.html', {'spare_part': spare_part, 'action': 'Update'})


@admin_required
def delete_spare_part(request, part_id):
    spare_part = get_object_or_404(SparePart, id=part_id)
    spare_part.delete()
    return redirect('user:spare_parts_list')

@admin_required
def order_list(request):
    orders = Order.objects.all()  # Admin can see all orders
    return render(request, 'admin/order_list.html', {'orders': orders})

@admin_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        new_status = request.POST.get('order_status')
        new_payment_status = request.POST.get('payment_status')
        tracking_id = request.POST.get('tracking_id')

        if new_status:
            order.order_status = new_status
        if new_payment_status:
            order.payment_status = new_payment_status
        if tracking_id:
            order.tracking_id = tracking_id

        # If the order is being canceled by the admin, set payment status to Refunded
        if new_status == 'Canceled':
            order.payment_status = 'Refunded'

        order.save()
        messages.success(request, "Order status updated successfully.")
        return redirect('admin:order_list')

    return render(request, 'admin/update_order_status.html', {'order': order})

@admin_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.order_status == 'Pending':
        order.order_status = 'Canceled'
        order.payment_status = 'Refunded'  # Update payment status to Refunded
        order.save()
        messages.success(request, "Your order has been cancelled and refunded.")
    else:
        messages.error(request, "You can only cancel pending orders.")

    return redirect('admin:order_list')

@admin_required
def refund_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.order_status == 'Canceled' and order.payment_status == 'Paid':
        order.payment_status = 'Refunded'
        order.save()
        messages.success(request, "The order has been refunded.")
    else:
        messages.error(request, "This order cannot be refunded.")

    return redirect('admin:order_list')

@admin_required
def admin_booking_list(request):
    bookings = Booking.objects.all()
    return render(request, 'admin/admin_booking_list.html', {'bookings': bookings})

@admin_required
def start_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        otp = request.POST.get('otp')
        if otp == booking.otp:
            booking.booking_status = 'Started'
            booking.save()
            messages.success(request, "Booking started successfully. Vehicle handed over to the customer.")
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return redirect('admin:admin_booking_list')

@admin_required
def return_vehicle(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == 'POST':
        condition = request.POST.get('condition', '').strip()
        if condition:
            booking.return_status = 'Returned'
            booking.vehicle.availability = 'Available'  # Mark vehicle as available
            booking.vehicle.save()
            booking.save()
            messages.success(request, f"Vehicle returned successfully. Condition: {condition}")
        else:
            messages.error(request, "Please provide the vehicle's condition.")

    return redirect('admin:admin_booking_list')

@admin_required
def check_car(request):
    return render(request, 'client/car_damage.html')

@admin_required
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        image_file = request.FILES['image']
        image_data = image_file.read()
        print(image_data)
        # Define the Flask API URL (match Flask's /predict endpoint and port)
        flask_api_url = 'http://127.0.0.1:8080/predict'

        try:
            # Send the image to Flask
            response = requests.post(flask_api_url, files={'image': image_data})
            response.raise_for_status()  # Raise exception for bad status codes
            flask_response = response.json()

            # Translate Flask response to match HTML expectations
            if 'error' in flask_response:
                return JsonResponse({'error': flask_response['error']}, status=400)
            else:
                return JsonResponse({
                    'result_image': flask_response['image'],
                    'prediction': flask_response['prediction']
                })

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': f'Failed to connect to detection service: {str(e)}'}, status=500)

    return JsonResponse({'error': 'No image uploaded'}, status=400)

@admin_required
def view_admin_account(request):
        admin_id = request.session.get('admin_id')
        user = User.objects.get(id=admin_id, is_superuser=True)
        return render(request, 'admin/account_settings.html',{'adminData':user})

@admin_required
def update_admin_account(request):
    # Check if user_id exists in session and get the user
    admin_id = request.session.get('admin_id')
    if not admin_id:
        messages.error(request, "Please login first")
        return redirect('admin:login')

    try:
        # Get user data and verify superuser status
        user = User.objects.get(id=admin_id, is_superuser=True)
    except User.DoesNotExist:
        messages.error(request, "You don't have permission to access this page")
        return redirect('admin:admin_dashboard')

    # Handle profile update
    if request.method == 'POST' and 'update_profile' in request.POST:
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        
        try:
            user.save()
            messages.success(request, "Profile updated successfully")
        except Exception as e:
            messages.error(request, "Error updating profile: " + str(e))

    # Handle password change without form
    if request.method == 'POST' and 'change_password' in request.POST:
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Validate password change
        if not check_password(old_password, user.password):
            messages.error(request, "Current password is incorrect")
        elif new_password1 != new_password2:
            messages.error(request, "New passwords don't match")
        elif len(new_password1) < 8:
            messages.error(request, "New password must be at least 8 characters long")
        else:
            try:
                user.password = make_password(new_password1)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Password updated successfully")
            except Exception as e:
                messages.error(request, "Error updating password: " + str(e))

    # Prepare data for template
    admin_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    }

    return render(request, 'admin/account_settings.html',{'adminData':user})

@admin_required
def vehicle_reviews(request):
    # Fetch all vehicles and spare parts for dropdowns
    vehicles = Vehicle.objects.all().values('id', 'brand', 'model', 'number_plate')
    spareparts = SparePart.objects.all().values('id', 'part_name', 'category')
    
    # Get all reviews
    reviews = Review.objects.all().select_related('customer__user', 'vehicle', 'sparepart')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete_review':
            review_id = request.POST.get('review_id')
            review = get_object_or_404(Review, id=review_id)
            review.delete()
            messages.success(request, "Review deleted successfully!")
            return redirect('admin:vehicle_reviews')
    
    context = {
        'vehicles': vehicles,
        'spareparts': spareparts,
        'reviews': reviews,
    }
    return render(request, 'admin/view_reviews.html', context)