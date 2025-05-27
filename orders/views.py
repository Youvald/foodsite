from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from .forms import CheckoutForm
from cart.cart import Cart


@login_required
def checkout_view(request):
    cart = Cart(request)
    if not cart.cart:
        return redirect('menu')

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():
            # Створення замовлення без збереження
            order = Order(
                user=request.user,
                first_name=form.cleaned_data['name'],
                phone=form.cleaned_data['phone'],
                delivery_type=form.cleaned_data['delivery_type'],
                payment_method=form.cleaned_data['payment_method']
            )

            # Розрахунок суми
            total = cart.get_total_price()
            if order.delivery_type == 'delivery' and total < 1500:
                total += 100
            order.total_price = total

            # Адреса (нова або збережена)
            saved_address = form.cleaned_data.get('use_saved_address')
            if saved_address:
                order.street = saved_address.street
                order.building = saved_address.building
                order.apartment = saved_address.apartment
            else:
                order.street = form.cleaned_data['street']
                order.building = form.cleaned_data['building']
                order.apartment = form.cleaned_data['apartment']

            order.save()

            # Додавання позицій у замовлення
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    dish=item['dish'],
                    quantity=item['quantity'],
                    price=item['dish'].price
                )

            cart.clear()

            # Перенаправлення в залежності від способу оплати
            if order.payment_method in ['binance', 'liqpay']:
                return redirect(f'/pay/{order.id}/')
            return redirect(f'/order/{order.id}/')

    else:
        # Попереднє заповнення імені та телефону
        initial = {
            'name': request.user.first_name,
            'phone': request.user.phone,
        }
        form = CheckoutForm(initial=initial, user=request.user)

    return render(request, 'orders/checkout.html', {'form': form})


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def user_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})
