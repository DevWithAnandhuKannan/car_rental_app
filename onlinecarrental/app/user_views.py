import json
import string
from time import timezone
from django.forms import ValidationError
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

def check_user_log(request):
    return 'user_id' in request.session

def user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if check_user_log(request):
            return view_func(request, *args, **kwargs)
        return redirect('user:login')
    return wrapper

def admin_or_user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if check_admin_log(request) or check_user_log(request):
            return view_func(request, *args, **kwargs)
        # Redirect to appropriate login based on context, or a default
        if 'admin' in request.path:  # If the URL suggests admin context
            return redirect('admin:admin_login')
        return redirect('user:login')
    return wrapper

class IndexView(TemplateView):
    template_name = 'index.html'

def login_view(request):
    if request.user.is_authenticated or 'user_id' in request.session:
        return redirect('user:index')
    error_message = None  
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password) 
        if user:
            login(request, user)
            request.session['user_id'] = user.id 
            return redirect('user:index')
        else:
            error_message = "Invalid email or password."
    return render(request, 'login.html', {'error_message': error_message})

def signup_view(request):
    if request.user.is_authenticated or 'user_id' in request.session:
        return redirect('user:index')

    error_message = None

    if request.method == 'POST':
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if User.objects.filter(email=email).exists():
            error_message = "This email is already taken."
        elif password1 != password2:
            error_message = "Passwords do not match."
        else:
            # Create Django user
            user = User.objects.create_user(username=email, email=email, password=password1)
            
            print(f"User Created: {user.id}")  # Debugging

            # Create Customer profile with empty strings instead of None
            Customer.objects.create(
                user=user,
            )

            if user:
                login(request, user)
                request.session['user_id'] = user.id 
                return redirect('user:index')

    return render(request, 'signup.html', {'error_message': error_message})


@user_required
def logout_view(request):
    logout(request)
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('user:login')

@admin_or_user_required
def vehicle_list(request):
    query = request.GET.get('q', '').strip()
    vehicles = Vehicle.objects.filter(
        brand__icontains=query
    ) | Vehicle.objects.filter(
        model__icontains=query
    ) | Vehicle.objects.filter(
        number_plate__icontains=query
    ) if query else Vehicle.objects.all()
    
    return render(request, 'admin/vehicle_list.html', {'vehicles': vehicles, 'query': query})

@admin_or_user_required
def spare_parts_list(request):
    spare_parts = SparePart.objects.all()
    return render(request, 'admin/spare_parts.html', {'spare_parts': spare_parts})

@admin_or_user_required
def car_list(request):
    cars = Vehicle.objects.all()
    return render(request, 'client/car_list.html', {'cars': cars})

@admin_required
@user_required
def car_details(request, car_id):
    car = get_object_or_404(Vehicle, id=car_id)
    return render(request, 'client/car_details.html', {'car': car})

@user_required
def check_availability(request, car_id):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Check if the vehicle is already booked for the selected dates
        overlapping_bookings = Booking.objects.filter(
            vehicle_id=car_id,
            start_date__lte=end_date,
            end_date__gte=start_date,
            booking_status='Confirmed'
        ).exists()

        return JsonResponse({'available': not overlapping_bookings})
    return JsonResponse({'available': False})

import random
import string

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))


def book_vehicle(request, car_id):
    print(f"Request method: {request.method}")
    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        user = request.user
        customer, _ = Customer.objects.get_or_create(user=user)

        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')
        address = Address.objects.create(
            customer=customer,
            street=street,
            city=city,
            state=state,
            postal_code=postal_code
        )
        print(f"Address created: {address}")

        customer.phone = request.POST.get('phone')
        customer.drivers_license = request.POST.get('driving_licence')
        customer.save()

        try:
            vehicle = Vehicle.objects.get(id=car_id)
            start_date_str = request.POST.get('start_date')
            end_date_str = request.POST.get('end_date')
            total_price = request.POST.get('total_price')
            print(f"Booking details: {start_date_str}, {end_date_str}, {total_price}")
            if not all([start_date_str, end_date_str, total_price]):
                messages.error(request, 'Missing required booking details.')
                return redirect('user:car_list')

            # Convert string dates to date objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            if start_date >= end_date:
                messages.error(request, 'End date must be after start date.')
                return redirect('user:car_list')

            booking = Booking(
                customer=customer,
                vehicle=vehicle,
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                payment_status='Pending',
                otp=generate_otp(),  # Call without arguments
                booking_status='Confirmed',
                return_status='Pending'
            )
            booking.save()
            print(f"Booking saved: {booking.id}")

            vehicle.availability = 'Booked'
            vehicle.save()
            print(f"Vehicle updated: {vehicle.availability}")

            messages.success(request, f'Booking successful! Your OTP: {booking.otp}')
            return redirect('user:booking_confirmation', booking_id=booking.id)
        except Exception as e:
            print(f"Error: {str(e)}")
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('user:car_list')

    print("Redirecting to car_list due to non-POST request")
    return redirect('user:car_list')


@user_required
def get_unavailable_dates(request, car_id):
    try:
        bookings = Booking.objects.filter(vehicle_id=car_id, booking_status='Confirmed')
        unavailable_dates = []
        for booking in bookings:
            start_date = booking.start_date
            end_date = booking.end_date
            if start_date and end_date:
                current_date = start_date
                while current_date <= end_date:
                    unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
                    current_date += timedelta(days=1)
        return JsonResponse({'unavailable_dates': unavailable_dates})
    except Exception as e:
        return JsonResponse({'unavailable_dates': [], 'error': str(e)})

@user_required
def booking_list(request):
    try:
        customer = Customer.objects.get(user=request.user)
        address = Address.objects.filter(customer=customer)
        bookings = Booking.objects.filter(customer=customer).order_by('-start_date')
        context = {
            'bookings': bookings,
            'address': address
        }
        return render(request, 'client/bookings.html', context)
    except Customer.DoesNotExist:
        messages.error(request, "Customer profile not found")
        return redirect('user:login')

@user_required  
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer__user=request.user)
    
    if booking.can_be_canceled():
        booking.booking_status = 'Canceled'
        booking.save()
        messages.success(request, "Booking has been canceled successfully")
    else:
        messages.error(request, "Cancellation not allowed. Must be at least 2 days before start date")
    
    return redirect('user:booking_list')

@user_required
def get_cart_data(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = Decimal('0.00')
    
    for part_id, quantity in cart.items():
        try:
            part = SparePart.objects.get(id=int(part_id))
            item_total = part.price * quantity
            cart_items.append({
                'part_id': part.id,
                'part_name': part.part_name,
                'quantity': quantity,
                'unit_price': float(part.price),
                'total_price': float(item_total)
            })
            total += Decimal(item_total)
        except SparePart.DoesNotExist:
            continue 
    
    return {
        'items': cart_items,
        'total': float(total),
        'count': len(cart_items)
    }

@user_required
def add_to_cart(request, part_id):
    if request.method == 'POST':
        data = json.loads(request.body)  # Parse JSON data
        quantity_str = data.get('quantity', '1')  # Default to '1' if not provided

        try:
            quantity = int(quantity_str)  # Ensure quantity is an integer
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid quantity provided.'}, status=400)

        part = get_object_or_404(SparePart, id=part_id)  # Handle non-existent part

        # Check if the requested quantity is available in stock
        if part.stock_quantity < quantity:
            return JsonResponse({'status': 'error', 'message': 'Insufficient stock.'}, status=400)

        # Get or create cart in session
        cart = request.session.get('cart', {})
        cart[str(part_id)] = cart.get(str(part_id), 0) + quantity  # Add quantity to cart
        request.session['cart'] = cart  # Save cart to session
        request.session.modified = True  # Ensure the session is saved
        
        return JsonResponse({
            'status': 'success',
            'cart': get_cart_data(request)
        })
    return JsonResponse({'status': 'error'})

@user_required
def remove_from_cart(request, part_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        
        if str(part_id) in cart:
            del cart[str(part_id)]  # Remove the item from the cart
            request.session['cart'] = cart  # Update the session cart
            request.session.modified = True  # Ensure the session is saved
            
        return JsonResponse({
            'status': 'success',
            'cart': get_cart_data(request)
        })
    return JsonResponse({'status': 'error'})

@user_required
def spare_parts(request):
    parts = SparePart.objects.filter(stock_quantity__gt=0)
    cart_data = get_cart_data(request)  # Get cart data to pass to the template
    return render(request, 'client/spare_parts.html', {'parts': parts, 'cart': cart_data})

@user_required
def check_availability(request, car_id):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date or not end_date:
        return JsonResponse({'available': False, 'error': 'Start and end dates are required'})

    try:
        # Convert string dates to date objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        # Validate date range
        if start_date >= end_date:
            return JsonResponse({'available': False, 'error': 'End date must be after start date'})

        # Check if vehicle exists
        if not Vehicle.objects.filter(id=car_id).exists():
            return JsonResponse({'available': False, 'error': 'Vehicle not found'})

        # Check for overlapping bookings
        overlapping_bookings = Booking.objects.filter(
            vehicle_id=car_id,
            start_date__lte=end_date,  # Booking starts on or before requested end date
            end_date__gte=start_date,  # Booking ends on or after requested start date
            booking_status='Confirmed'
        ).exists()

        return JsonResponse({'available': not overlapping_bookings})

    except ValueError:
        return JsonResponse({'available': False, 'error': 'Invalid date format. Use YYYY-MM-DD'})
    except Exception as e:
        return JsonResponse({'available': False, 'error': f'An error occurred: {str(e)}'})

@user_required
@transaction.atomic
def checkout(request):
    customer = Customer.objects.get(user=request.user)

    if request.method == 'POST':
        # Process payment and create order
        cart = request.session.get('cart', {})
        shipping_address_id = request.POST.get('address') 

        # Check if the user selected an existing address or a new address
        if shipping_address_id == 'new':
            # Handle new address
            street = request.POST.get('new_street')
            city = request.POST.get('new_city')
            state = request.POST.get('new_state')
            postal_code = request.POST.get('new_postal_code')

            # Create a new address
            shipping_address = Address.objects.create(
                customer=customer,
                street=street,
                city=city,
                state=state,
                postal_code=postal_code
            )
        else:
            # Validate the selected address
            try:
                shipping_address = Address.objects.get(id=shipping_address_id, customer=customer)
            except Address.DoesNotExist:
                messages.error(request, "Invalid shipping address.")
                return redirect('user:checkout')

        total_price = 0  # Initialize total price
        for part_id, quantity in cart.items():
            part = SparePart.objects.get(id=int(part_id))
            item_total = part.price * quantity
            total_price += item_total  # Accumulate total price

            Order.objects.create(
                customer=customer,
                part=part,
                quantity=quantity,
                total_price=item_total,
                shipping_address=shipping_address,  
                payment_status='Paid'
            )
            part.stock_quantity -= quantity
            part.save()

        del request.session['cart']
        messages.success(request, "Your order has been placed successfully!")
        return redirect('user:checkout')

    # Retrieve all addresses for the customer
    addresses = Address.objects.filter(customer=customer)
    cart_data = get_cart_data(request)  # Get cart data to pass to the template
    return render(request, 'client/checkout.html', {
        'addresses': addresses,
        'cart_items': cart_data['items'],
        'cart_total': cart_data['total']
    })

@user_required
def order_history(request):
    orders = Order.objects.filter(customer__user=request.user).order_by('-id')
    return render(request, 'client/order_history.html', {'orders': orders})

@user_required
def report_defect(request, order_id):
    if request.method == 'POST':
        defect_description = request.POST.get('defect_description')
        order = get_object_or_404(Order, id=order_id, customer__user=request.user)

        # Here you can implement the logic to save the defect report
        # For example, you might want to create a new model for defect reports

        messages.success(request, "Your defect report has been submitted.")
        return redirect('user:order_history')  

@user_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.order_status == 'Pending':
        order.order_status = 'Canceled'
        order.payment_status = 'Refunded'
        order.save()
        messages.success(request, "Your order has been cancelled and refunded.")
    else:
        messages.error(request, "You can only cancel pending orders.")

    return redirect('admin:order_list')

@user_required
def vehicle_reviews(request):
    # Fetch all vehicles and spare parts for dropdowns
    vehicles = Vehicle.objects.all().values('id', 'brand', 'model', 'number_plate')
    spareparts = SparePart.objects.all().values('id', 'part_name', 'category')
    
    # Get all reviews
    reviews = Review.objects.all().select_related('customer__user', 'vehicle', 'sparepart')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'submit_review':
            customer = get_object_or_404(Customer, user=request.user)  # From session
            rating = request.POST.get('rating')
            comments = request.POST.get('comments', '')
            tag = request.POST.get('tag') == 'on'  # Checkbox checked
            
            vehicle_id = request.POST.get('vehicle_id') if tag else None
            sparepart_id = request.POST.get('sparepart_id') if tag else None
            
            try:
                if not rating:
                    raise ValueError("Rating is required.")
                
                review = Review(
                    customer=customer,
                    rating=int(rating),
                    comments=comments,
                )
                if vehicle_id:
                    review.vehicle = get_object_or_404(Vehicle, id=vehicle_id)
                if sparepart_id:
                    review.sparepart = get_object_or_404(SparePart, id=sparepart_id)
                
                review.save()
                messages.success(request, "Review submitted successfully!")
            except ValueError as e:
                messages.error(request, f"Error submitting review: {str(e)}")
            except Exception as e:
                messages.error(request, f"Unexpected error: {str(e)}")
            return redirect('user:vehicle_reviews')
        
        elif action == 'delete_review':
            review_id = request.POST.get('review_id')
            review = get_object_or_404(Review, id=review_id)
            review.delete()
            messages.success(request, "Review deleted successfully!")
            return redirect('user:vehicle_reviews')
    
    context = {
        'vehicles': vehicles,
        'spareparts': spareparts,
        'reviews': reviews,
    }
    return render(request, 'client/reviews.html', context)