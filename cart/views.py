from django.shortcuts import render, redirect, get_object_or_404
from menu.models import Dish
from .cart import Cart
from django.views.decorators.http import require_POST

def cart_view(request):
    cart = Cart(request)
    return render(request, 'cart/cart.html', {'cart': cart})

def add_to_cart(request, dish_id):
    cart = Cart(request)
    dish = get_object_or_404(Dish, id=dish_id)
    cart.add(dish_id=dish.id, quantity=1)
    return redirect('cart')

def remove_from_cart(request, dish_id):
    cart = Cart(request)
    cart.remove(dish_id)
    return redirect('cart')

@require_POST
def add_to_cart(request, dish_id):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(dish_id=dish_id, quantity=quantity)
    return redirect(request.POST.get('next', 'cart'))

@require_POST
def update_quantity(request, dish_id):
    cart = Cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(dish_id=dish_id, quantity=quantity, update_quantity=True)
    return redirect('cart')