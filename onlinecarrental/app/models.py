from datetime import timedelta, timezone
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

# Vehicle Model
from django.db import models

class Vehicle(models.Model):
    TRANSMISSION_CHOICES = [('Manual', 'Manual'), ('Automatic', 'Automatic')]
    FUEL_CHOICES = [('Petrol', 'Petrol'), ('Diesel', 'Diesel'), ('Electric', 'Electric')]
    AVAILABILITY_CHOICES = [('Available', 'Available'), ('Booked', 'Booked'), ('Maintenance', 'Maintenance')]
    VEHICLE_TYPE_CHOICES = [('Sedan', 'Sedan'), ('SUV', 'SUV'), ('Hatchback', 'Hatchback'), ('Truck', 'Truck')]

    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    number_plate = models.CharField(max_length=20, unique=True)
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    mileage = models.DecimalField(max_digits=10, decimal_places=2)
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES)
    transmission_type = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='Available')
    seats = models.IntegerField(default=4)  # Number of seats
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='Sedan')
    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)
    features = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"{self.brand} {self.model} ({self.number_plate})"

class Address(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='addresses')
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.state} {self.postal_code}"

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True, null=True)
    drivers_license = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Ensure at least one default address exists, but only if there are any addresses
        if self.addresses.exists():  # Check if any addresses exist first
            if not self.addresses.filter(is_default=True).exists():
                first_address = self.addresses.first()
                first_address.is_default = True
                first_address.save()

from django.utils import timezone
from datetime import timedelta
# Booking Model
class Booking(models.Model):
    BOOKING_STATUS_CHOICES = [('Confirmed', 'Confirmed'), ('Canceled', 'Canceled')]
    RETURN_STATUS_CHOICES = [('Returned', 'Returned'), ('Pending', 'Pending')]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=[('Paid', 'Paid'), ('Pending', 'Pending')], default='Pending')
    otp = models.CharField(max_length=6)
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS_CHOICES, default='Confirmed')
    return_status = models.CharField(max_length=20, choices=RETURN_STATUS_CHOICES, default='Pending')
    def can_be_canceled(self):
        # Check if the booking is at least 2 days before the start date
        return (self.start_date - timezone.now().date()) >= timedelta(days=2)

    def __str__(self):
        return f"Booking {self.id} - {self.customer.user.username} - {self.vehicle.brand} {self.vehicle.model}"



# Spare Parts Model
class SparePart(models.Model):
    CATEGORY_CHOICES = [('Engine', 'Engine'), ('Brake', 'Brake'), ('Suspension', 'Suspension'), ('Electrical', 'Electrical'), ('Other', 'Other')]

    part_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='spare_parts/', blank=True, null=True)
    car_compatibility = models.CharField(max_length=255)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.part_name} ({self.category})"
    def is_in_stock(self, quantity=1):
        return self.stock_quantity >= quantity

# Order Model
class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled')
    ]
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Pending', 'Pending'),
        ('Refunded', 'Refunded')
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    part = models.ForeignKey(SparePart, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='Pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    shipping_address = models.TextField()
    tracking_id = models.CharField(max_length=50, blank=True, null=True)  # New field for tracking ID

    def __str__(self):
        return f"Order {self.id} - {self.customer.user.username} - {self.part.part_name}"
    


# Review Model
class Review(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, null=True, blank=True)  # Optional
    sparepart = models.ForeignKey(SparePart, on_delete=models.CASCADE, null=True, blank=True)  # Optional
    rating = models.IntegerField()
    comments = models.TextField(blank=True, null=True)
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review {self.id} - {self.customer.user.username}"