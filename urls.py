from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('destinations', views.destination_list, name='destination_list'),
    path('signup', views.signup, name='signup'),
    path('login', views.login_user, name='login'),
    path('destination/<str:id>', views.destination_detail, name='destination_detail'),
    path('payment/<str:destination_id>', views.payment_page, name='payment_page'),
    path('itinerary/', views.generate_itinerary, name='generate_itinerary'),
    path('loged_home', views.loged_home, name='loged_home'),
    path('profile', views.profile, name='profile'),
    path('itinerary/profile.html', views.profile, name='profile'),
] 