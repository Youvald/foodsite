from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_view, name='menu'),
    path('dish/<int:dish_id>/', views.dish_detail_view, name='dish_detail'),
]
