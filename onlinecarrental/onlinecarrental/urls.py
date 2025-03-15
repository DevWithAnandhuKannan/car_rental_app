"""
URL configuration for onlinecarrental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from app.views import book_vehicle

urlpatterns = [
    path( '', include('app.user_urls')),         # User routes
    path('admin/', include('app.admin_urls')),  # Admin routes
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    
# urlpatterns = [
#     path('admin/login/', admin_login, name='admin_login'),
#     path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
#     path('admin/logout/', admin_logout, name='admin_logout'),
#     path('', IndexView.as_view(), name='index'),
#     path('login/', login_view, name='login'),
#     path('signup/', signup_view, name='signup'),
#     path('logout/', logout_view, name='logout'),
#     path('vehicles', vehicle_list, name='vehicle_list'),
#     path('add_vehicle/', add_vehicle, name='add_vehicle'),
#     path('update_vehicle/<int:vehicle_id>/', update_vehicle, name='update_vehicle'),
#     path('delete_vehicle/<int:vehicle_id>/', delete_vehicle, name='delete_vehicle'),
#     path('spare_parts/', spare_parts_list, name='spare_parts_list'),
#     path('add_spare_part/', add_spare_part, name='add_spare_part'),
#     path('update_spare_part/<int:part_id>/', update_spare_part, name='update_spare_part'),
#     path('delete_spare_part/<int:part_id>/', delete_spare_part, name='delete_spare_part'),
#     path('cars/', car_list, name='car_list'),
#     path('cars/<int:car_id>/', car_details, name='car_details'),
#     path('check-availability/<int:car_id>/', check_availability, name='check_availability'),
#     path('book/<int:car_id>/', book_vehicle, name='book_vehicle'),
#     path('book-vehicle/<int:car_id>/', book_vehicle, name='book_vehicle'),
#     path('unavailable-dates/<int:car_id>/', get_unavailable_dates, name='get_unavailable_dates'),
#     path('bookings/', booking_list, name='booking_list'),
#     path('bookings/cancel/<int:booking_id>/', cancel_booking, name='cancel_booking'),
#     path('parts/', spare_parts, name='spare_parts'),
#     path('add-to-cart/<int:part_id>/', add_to_cart, name='add_to_cart'),
#     path('remove-from-cart/<int:part_id>/', remove_from_cart, name='remove_from_cart'),
#     path('checkout/', checkout, name='checkout'),
#     path('orders/', order_history, name='order_history'),
#     path('order-history/', order_history, name='order_history'),
#     path('report-defect/<int:order_id>/', report_defect, name='report_defect'),
#     path('cancel-order/<int:order_id>/', cancel_order, name='cancel_order'),
#     path('admin/orders/', order_list, name='order_list'),
#     path('orders/update/<int:order_id>/', update_order_status, name='update_order_status'),
#     path('orders/cancel/<int:order_id>/', cancel_order, name='cancel_order'),
#     path('orders/refund/<int:order_id>/', refund_order, name='refund_order'),
#     path('admin/bookings/', admin_booking_list, name='admin_booking_list'),
#     path('admin/bookings/start/<int:booking_id>/', start_booking, name='start_booking'),
#     path('admin/bookings/return/<int:booking_id>/', return_vehicle, name='return_vehicle'),
#     path('admin/checkcar',check_car,name="check_car"),
#     path('admin/upload_image/', upload_image, name='upload_image'),
#     path('admin/account/', view_admin_account, name='view_admin_account'),
#     path('admin/account_update/', update_admin_account, name='admin_settings'),
# ]
