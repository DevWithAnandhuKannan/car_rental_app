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
from .models import Address, Customer, Order, Vehicle
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

def check_user_log(request):
    return 'user_id' in request.session

def user_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if check_user_log(request):
            return view_func(request, *args, **kwargs)
        return redirect('login')
    return wrapper

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if check_admin_log(request):
            return view_func(request, *args, **kwargs)
        return redirect('admin_login')
    return wrapper


def check_car(request):
    return render(request, 'client/car_damage.html')

import requests
from django.http import JsonResponse

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

def admin_booking_list(request):
    bookings = Booking.objects.all()
    return render(request, 'admin/admin_booking_list.html', {'bookings': bookings})

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

    return redirect('admin_booking_list')

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

    return redirect('admin_booking_list')

def order_list(request):
    orders = Order.objects.all()  # Admin can see all orders
    return render(request, 'admin/order_list.html', {'orders': orders})


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
        return redirect('order_list')

    return render(request, 'admin/update_order_status.html', {'order': order})

def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.order_status == 'Pending':
        order.order_status = 'Canceled'
        order.payment_status = 'Refunded'  # Update payment status to Refunded
        order.save()
        messages.success(request, "Your order has been cancelled and refunded.")
    else:
        messages.error(request, "You can only cancel pending orders.")

    return redirect('order_list')

def refund_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.order_status == 'Canceled' and order.payment_status == 'Paid':
        order.payment_status = 'Refunded'
        order.save()
        messages.success(request, "The order has been refunded.")
    else:
        messages.error(request, "This order cannot be refunded.")

    return redirect('order_list')


def report_defect(request, order_id):
    if request.method == 'POST':
        defect_description = request.POST.get('defect_description')
        order = get_object_or_404(Order, id=order_id, customer__user=request.user)

        # Here you can implement the logic to save the defect report
        # For example, you might want to create a new model for defect reports

        messages.success(request, "Your defect report has been submitted.")
        return redirect('order_history')  # Redirect back to order history


def spare_parts(request):
    parts = SparePart.objects.filter(stock_quantity__gt=0)
    cart_data = get_cart_data(request)  # Get cart data to pass to the template
    return render(request, 'client/spare_parts.html', {'parts': parts, 'cart': cart_data})


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
                return redirect('checkout')

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
        return redirect('checkout')

    # Retrieve all addresses for the customer
    addresses = Address.objects.filter(customer=customer)
    cart_data = get_cart_data(request)  # Get cart data to pass to the template
    return render(request, 'client/checkout.html', {
        'addresses': addresses,
        'cart_items': cart_data['items'],
        'cart_total': cart_data['total']
    })


def order_history(request):
    orders = Order.objects.filter(customer__user=request.user).order_by('-id')
    return render(request, 'client/order_history.html', {'orders': orders})


def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, customer__user=request.user)
    
    if booking.can_be_canceled():
        booking.booking_status = 'Canceled'
        booking.save()
        messages.success(request, "Booking has been canceled successfully")
    else:
        messages.error(request, "Cancellation not allowed. Must be at least 2 days before start date")
    
    return redirect('booking_list')

def get_unavailable_dates(request, car_id):
    # Fetch all bookings for the vehicle
    bookings = Booking.objects.filter(vehicle_id=car_id, booking_status='Confirmed')

    # Generate a list of unavailable dates
    unavailable_dates = []
    for booking in bookings:
        start_date = booking.start_date
        end_date = booking.end_date
        current_date = start_date
        while current_date <= end_date:
            unavailable_dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)

    return JsonResponse({'unavailable_dates': unavailable_dates})


def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

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
        return redirect('home')

def book_vehicle(request, car_id):
    print('reached')
    if request.method == 'POST':
        print('reached')
        user = request.user
        customer, created = Customer.objects.get_or_create(user=user)

        # Update user details
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.save()

        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        postal_code = request.POST.get('postal_code')

        address, created = Address.objects.get_or_create(
            customer=customer,
            defaults={
                'street': street,
                'city': city,
                'state': state,
                'postal_code': postal_code,
            }
        )
        address.street = street
        address.city = city
        address.state = state
        address.postal_code = postal_code
        address.save()

        # Update customer details
        customer.phone = request.POST.get('phone')
        customer.drivers_license = request.POST.get('driving_licence')
        customer.save()

        # Create booking
        try:
            vehicle = Vehicle.objects.get(id=car_id)
            booking = Booking(
                customer=customer,
                vehicle=vehicle,
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                total_price=request.POST.get('total_price'),
                payment_status='Pending',
                otp=generate_otp(),
                booking_status='Confirmed',
                return_status='Pending'
            )
            booking.save()
            
            # Update vehicle availability if needed
            vehicle.availability = 'Booked'
            vehicle.save()
            
            messages.success(request, 'Booking successful! Your OTP: ' + booking.otp)
            return redirect('booking_confirmation', booking_id=booking.id)
            
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('car_list')

    return redirect('car_list')

from django.contrib.auth.decorators import login_required

def car_list(request):
    cars = Vehicle.objects.all()
    return render(request, 'client/car_list.html', {'cars': cars})


def car_details(request, car_id):
    car = get_object_or_404(Vehicle, id=car_id)
    return render(request, 'client/car_details.html', {'car': car})


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


def spare_parts_list(request):
    spare_parts = SparePart.objects.all()
    return render(request, 'admin/spare_parts.html', {'spare_parts': spare_parts})

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
        return redirect('spare_parts_list')
    
    return render(request, 'admin/spare_parts.html', {'action': 'Add'})

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
        return redirect('spare_parts_list')

    return render(request, 'admin/spare_parts.html', {'spare_part': spare_part, 'action': 'Update'})

def delete_spare_part(request, part_id):
    spare_part = get_object_or_404(SparePart, id=part_id)
    spare_part.delete()
    return redirect('spare_parts_list')

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

def add_vehicle(request):
    if request.method == "POST":
        required_fields = ['brand', 'model', 'number_plate', 'price_per_day', 'mileage', 'fuel_type', 'transmission_type', 'availability']
        
        missing_fields = [field for field in required_fields if not request.POST.get(field, '').strip()]
        if missing_fields:
            for field in missing_fields:
                messages.error(request, f"{field.replace('_', ' ').capitalize()} is required.")
            return redirect('vehicle_list')
        
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
        return redirect('vehicle_list')
    
    return render(request, 'admin/add_vehicle.html')

def update_vehicle(request, vehicle_id):
    print('called update vehicle')
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == "POST":
        required_fields = ['brand', 'model', 'number_plate', 'price_per_day', 'mileage', 'fuel_type', 'transmission_type', 'availability']
        
        missing_fields = [field for field in required_fields if not request.POST.get(field, '').strip()]
        if missing_fields:
            for field in missing_fields:
                messages.error(request, f"{field.replace('_', ' ').capitalize()} is required.")
            return redirect('vehicle_list')
        
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
        return redirect('vehicle_list')

    return render(request, 'admin/update_vehicle.html', {'vehicle': vehicle})

def delete_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    vehicle.delete()
    messages.success(request, "Vehicle deleted successfully!")
    return redirect('vehicle_list')


class IndexView(TemplateView):
    template_name = 'index.html'


def view_admin_account(request):
        admin_id = request.session.get('admin_id')
        user = User.objects.get(id=admin_id, is_superuser=True)
        return render(request, 'admin/account_settings.html',{'adminData':user})

def update_admin_account(request):
    # Check if user_id exists in session and get the user
    admin_id = request.session.get('admin_id')
    if not admin_id:
        messages.error(request, "Please login first")
        return redirect('login')

    try:
        # Get user data and verify superuser status
        user = User.objects.get(id=admin_id, is_superuser=True)
    except User.DoesNotExist:
        messages.error(request, "You don't have permission to access this page")
        return redirect('admin_dashboard')

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

def login_view(request):
    if request.user.is_authenticated or 'user_id' in request.session:
        return redirect('index')

    error_message = None  # Initialize error message

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)  # Use Django's built-in authentication
        if user:
            login(request, user)
            request.session['user_id'] = user.id 
            return redirect('index')
        else:
            error_message = "Invalid email or password."

    return render(request, 'login.html', {'error_message': error_message})


def signup_view(request):
    if request.user.is_authenticated or 'user_id' in request.session:
        return redirect('index')

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
                return redirect('index')

    return render(request, 'signup.html', {'error_message': error_message})


def logout_view(request):
    request.session.flush()  # Completely clear session
    logout(request)
    return redirect('login')
