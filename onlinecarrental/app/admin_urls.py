from django.urls import path
from .admin_views import (
    admin_login, admin_dashboard, admin_logout, add_vehicle, update_vehicle,
    delete_vehicle, add_spare_part, update_spare_part, delete_spare_part,
    order_list, update_order_status, cancel_order, refund_order,
    admin_booking_list, start_booking, return_vehicle, check_car,
    upload_image, view_admin_account, update_admin_account, vehicle_reviews
)

app_name = 'admin'  

urlpatterns = [
    path('login/', admin_login, name='admin_login'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('logout/', admin_logout, name='admin_logout'),
    path('add_vehicle/', add_vehicle, name='add_vehicle'),
    path('update_vehicle/<int:vehicle_id>/', update_vehicle, name='update_vehicle'),
    path('delete_vehicle/<int:vehicle_id>/', delete_vehicle, name='delete_vehicle'),
    path('add_spare_part/', add_spare_part, name='add_spare_part'),
    path('update_spare_part/<int:part_id>/', update_spare_part, name='update_spare_part'),
    path('delete_spare_part/<int:part_id>/', delete_spare_part, name='delete_spare_part'),
    path('orders/', order_list, name='order_list'),
    path('orders/update/<int:order_id>/', update_order_status, name='update_order_status'),
    path('orders/cancel/<int:order_id>/', cancel_order, name='cancel_order'),
    path('orders/refund/<int:order_id>/', refund_order, name='refund_order'),
    path('bookings/', admin_booking_list, name='admin_booking_list'),
    path('bookings/start/<int:booking_id>/', start_booking, name='start_booking'),
    path('bookings/return/<int:booking_id>/', return_vehicle, name='return_vehicle'),
    path('checkcar/', check_car, name='check_car'),
    path('upload_image/', upload_image, name='upload_image'),
    path('account/', view_admin_account, name='view_admin_account'),
    path('account_update/', update_admin_account, name='admin_settings'),
    path('reviews/', vehicle_reviews, name='vehicle_reviews'),
]