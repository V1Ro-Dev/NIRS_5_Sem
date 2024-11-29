from django.urls import path
from app import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('settings/', views.settings, name='settings'),
    path('logout/', views.logout, name='logout'),
    path('rooms/', views.rooms_and_bookings, name='rooms'),
    path('rooms/<str:room_type>', views.rooms, name='room'),
    path('booking/', views.booking, name='booking'),
    path('booking/<uuid:room_id>', views.book_room, name='book_room'),
    path('contacts/', views.contacts, name='contacts')
]