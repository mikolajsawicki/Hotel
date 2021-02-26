from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from . import views

app_name = 'hotelapp'
urlpatterns = [
    path('', views.index, name='index'),
    path('pokoje/<int:room_id>/', views.room_view, name='room'),
    path('pokoje/', views.search_rooms, name='rooms'),
    path('rejestracja/', views.guest_register, name='register'),
    path('logowanie/', views.guest_login, name='login'),
    path('wyloguj/', views.guest_logout, name='logout'),
    path('dodaj-rezerwacje/', views.guest_add_reservation, name='add_reservation'),
    path('moje-rezerwacje/', views.my_reservations, name='my_reservations'),
    path('zarzadzaj-rezerwacjami/', views.manage_reservations, name='manage_reservations'),
    path('zarzadzaj-goscmi/', views.manage_guests, name='manage_guests'),
    path('statistics/', views.statistics, name='statistics'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
