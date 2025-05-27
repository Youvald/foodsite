from django.shortcuts import render, get_object_or_404
from .models import Dish, Category

def menu_view(request):
    category_id = request.GET.get('category')
    if category_id:
        dishes = Dish.objects.filter(category_id=category_id)
    else:
        dishes = Dish.objects.all()

    categories = Category.objects.all()
    return render(request, 'menu/menu.html', {
        'dishes': dishes,
        'categories': categories,
        'active_category': int(category_id) if category_id else None
    })

def dish_detail_view(request, dish_id):
    dish = get_object_or_404(Dish, id=dish_id)
    return render(request, 'menu/dish_detail.html', {'dish': dish})
