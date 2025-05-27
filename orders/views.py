from django.shortcuts import render, redirect
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.cart import Cart
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404

@login_required
def checkout_view(request):
    cart = Cart(request)

    if not cart.cart:
        return redirect('menu')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user

            total = cart.get_total_price()
            if order.delivery_type == 'delivery' and total < 1500:
                total += 100

            order.total_price = total
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    dish=item['dish'],
                    quantity=item['quantity'],
                    price=item['dish'].price
                )

            cart.clear()

            if order.payment_method in ['binance', 'liqpay']:
                return redirect(f'/pay/{order.id}/')
            return redirect(f'/order/{order.id}/')

    else:
        initial_data = {
            'first_name': request.user.first_name,
            'phone': request.user.phone
        }
        form = CheckoutForm(initial=initial_data)

    return render(request, 'orders/checkout.html', {'form': form, 'cart': cart})

@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def user_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})
