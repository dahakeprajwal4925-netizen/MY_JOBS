from django.urls import path
from .views import *   # IMPORTANT

urlpatterns = [
    path('', home, name='home'),
    path('success/', success, name='success'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),   # THIS LINE
    path('dashboard/', dashboard, name='dashboard'),
]