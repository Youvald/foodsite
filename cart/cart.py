from decimal import Decimal
from menu.models import Dish

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, dish_id, quantity=1, update_quantity=False):
        dish_id = str(dish_id)
        if dish_id not in self.cart:
            self.cart[dish_id] = {'quantity': 0}
        if update_quantity:
            self.cart[dish_id]['quantity'] = quantity
        else:
            self.cart[dish_id]['quantity'] += quantity
        self.save()

    def remove(self, dish_id):
        dish_id = str(dish_id)
        if dish_id in self.cart:
            del self.cart[dish_id]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session['cart'] = {}
        self.save()

    def __iter__(self):
        dish_ids = self.cart.keys()
        dishes = Dish.objects.filter(id__in=dish_ids)
        for dish in dishes:
            item = self.cart[str(dish.id)]
            item['dish'] = dish
            item['total_price'] = dish.price * item['quantity']
            yield item

    def get_total_price(self):
        return sum(item['dish'].price * item['quantity'] for item in self)
