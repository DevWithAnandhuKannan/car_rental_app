from django.urls import path
from .user_views import (
    IndexView, login_view, signup_view, logout_view, vehicle_list,
    spare_parts_list, car_list, car_details, check_availability,
    book_vehicle, get_unavailable_dates, booking_list, cancel_booking,
    spare_parts, add_to_cart, remove_from_cart, checkout, order_history,
    report_defect, cancel_order, vehicle_reviews
)

app_name = 'user' 

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('logout/', logout_view, name='logout'),
    path('vehicles/', vehicle_list, name='vehicle_list'),
    path('spare_parts/', spare_parts_list, name='spare_parts_list'),
    path('cars/', car_list, name='car_list'),
    path('cars/<int:car_id>/', car_details, name='car_details'),
    path('book-vehicle/<int:car_id>/', book_vehicle, name='book_vehicle'),
    path('unavailable-dates/<int:car_id>/', get_unavailable_dates, name='get_unavailable_dates'),
    path('bookings/', booking_list, name='booking_list'),
    path('bookings/cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('parts/', spare_parts, name='spare_parts'),
    path('add-to-cart/<int:part_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:part_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('orders/', order_history, name='order_history'),
    path('order-history/', order_history, name='order_history'),
    path('report-defect/<int:order_id>/', report_defect, name='report_defect'),
    path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),
    path('check-availability/<int:car_id>/', check_availability, name='check_availability'),
    path('reviews/', vehicle_reviews, name='vehicle_reviews'),
]