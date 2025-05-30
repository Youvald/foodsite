from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET
from accounts.models import DeliveryAddress
from orders.models import Order, OrderItem
from cart.cart import Cart
from django.contrib.auth.decorators import login_required
from payment.forms import CryptoPaymentForm
from payment.utils import get_crypto_price
from payment.bscscan import check_bsc_transaction
import qrcode
import io
import base64
from datetime import timedelta, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from django.http import JsonResponse
from payment.models import Network, CryptoWallet


def get_networks_for_crypto(request):
    crypto = request.GET.get('crypto')
    networks = Network.objects.filter(cryptowallet__crypto=crypto).distinct()
    data = [{'id': n.id, 'name': str(n)} for n in networks]
    return JsonResponse({'networks': data})


def crypto_payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if not order.crypto_wallet:
        return redirect('select_crypto_payment', order_id=order_id)

    crypto = order.crypto_wallet.crypto
    address = order.crypto_wallet.network.address

    if not order.crypto_amount:
        rate = get_crypto_price(crypto)
        if rate:
            rate_decimal = Decimal(str(rate))
            amount = (order.total_price / rate_decimal).quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
            order.crypto_amount = amount
            order.save()
        else:
            amount = None
    else:
        amount = order.crypto_amount

    qr_data = f"{address}?amount={amount}"
    qr = qrcode.make(qr_data)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    expiration_time = order.created_at + timedelta(hours=2)

    if datetime.now(timezone.utc) > expiration_time and order.status != 'PAID':
        order.status = 'EXPIRED'
        order.save()

    if crypto == 'BNB' and str(order.crypto_wallet.network) == 'BSC' and order.status != 'PAID':
        if check_bsc_transaction(address, Decimal(str(amount))):
            order.status = 'PAID'
            order.save()
            return redirect('payment_success', order_id=order.id)

    context = {
        'order': order,
        'address': address,
        'amount': amount,
        'qr_code_base64': img_str,
        'expiration_time': expiration_time,
    }
    return render(request, 'payment/crypto_payment.html', context)


def select_crypto_payment(request):
    cart = Cart(request)
    data = request.session.get('checkout_data')

    if not data or not cart.cart:
        return redirect('checkout')

    if request.method == 'POST':
        form = CryptoPaymentForm(request.POST)
        if form.is_valid():
            crypto = form.cleaned_data['crypto']
            network = form.cleaned_data['network']
            try:
                wallet = CryptoWallet.objects.get(crypto=crypto, network=network)

                user = request.user
                address_obj = None
                address_str = ""

                if data['use_saved_address']:
                    address_obj = DeliveryAddress.objects.get(id=data['use_saved_address'])
                    address_str = f"{address_obj.street}, буд. {address_obj.building}"
                    if address_obj.apartment:
                        address_str += f", кв. {address_obj.apartment}"
                else:
                    address_str = f"{data['street']}, буд. {data['building']}"
                    if data['apartment']:
                        address_str += f", кв. {data['apartment']}"

                total = cart.get_total_price()
                if data['delivery_type'] == 'delivery' and total < 1500:
                    total += 100

                order = Order.objects.create(
                    user=user,
                    first_name=data['name'],
                    phone=data['phone'],
                    delivery_type=data['delivery_type'],
                    payment_method='crypto',
                    address=address_str,
                    total_price=total,
                    crypto_wallet=wallet
                )

                for item in cart:
                    OrderItem.objects.create(
                        order=order,
                        dish=item['dish'],
                        quantity=item['quantity'],
                        price=item['dish'].price
                    )

                cart.clear()
                del request.session['checkout_data']

                return redirect('crypto_payment_page', order_id=order.id)

            except CryptoWallet.DoesNotExist:
                form.add_error(None, 'Вибраного гаманця не існує')
    else:
        form = CryptoPaymentForm()

    return render(request, 'payment/select_crypto.html', {'form': form})


@require_GET
def check_payment_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if order.status == 'PAID':
        return JsonResponse({'status': 'PAID'})

    network = str(order.crypto_wallet.network).upper()
    token_symbol = order.crypto_wallet.crypto
    address = order.crypto_wallet.network.address
    expected_amount = order.crypto_amount
    created_after = order.created_at.replace(tzinfo=timezone.utc)

    wallet = order.crypto_wallet
    if network == 'BSC':
        is_paid = check_bsc_transaction(address, expected_amount, contract_address=wallet.contract_address, created_after=created_after)
        if is_paid:
            order.status = 'PAID'
            order.save()
            return JsonResponse({'status': 'PAID'})

    return JsonResponse({'status': 'PENDING'})


def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'payment/payment_success.html', {'order': order})
