from django.urls import path,include
from .views import *

urlpatterns = [
    
    path('',home,name='home'),
    path('login/',log_in,name='login'),
    path('logout/',log_out,name='logout'),
    path('register/',register,name='register'),
    path('book/<int:pk>/',book_detail, name='book_detail'),

]