from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .forms import ReservationForm, OrderForm, ReviewForm
from .models import Category, MenuItem, Order, OrderItem, Review, MenuItemReview,Profile

import json
from django.contrib.auth.decorators import login_required



# =========================
# PAGES
# =========================
def index(request):
    return render(request, 'main/index.html')


def menu(request):
    categories = Category.objects.filter(is_active=True).order_by('order')
    return render(request, 'main/menu.html', {'categories': categories})


def reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            r = form.save()
            messages.success(request, f'Спасибо, {r.name}! Бронь создана.')
            return redirect('reservation')
    else:
        form = ReservationForm()

    return render(request, 'main/reservation.html', {'form': form})


def contact(request):
    reviews = Review.objects.filter(is_approved=True)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.is_approved = False
            review.save()
            messages.success(request, 'Спасибо за отзыв!')
            return redirect('contact')
    else:
        form = ReviewForm()

    return render(request, 'main/contact.html', {
        'reviews': reviews,
        'form': form
    })


def news(request):
    return render(request, 'main/news.html')

def news_detail(request, news_id):

    news_data = {
        1: {
            "title": "Открытие филиала",
            "images": [
                {"img": "images/news1.jpg", "text": "Наш новый филиал"},
                {"img": "images/news2.jpg", "text": "Интерьер кухни"},
            ]
        },
        2: {
            "title": "Новое меню",
            "images": [
                {"img": "images/news3.jpg", "text": "Десерты"},
                {"img": "images/news4.jpg", "text": "Основные блюда"},
            ]
        }
    }

    news = news_data.get(news_id, {
        "title": "Новость не найдена",
        "images": []
    })

    return render(request, 'main/news_detail.html', {
        'title': news['title'],
        'images': news['images']
    })
# =========================
# CART
# =========================
def _get_cart(request):
    return request.session.setdefault('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def add_to_cart(request, item_id):
    cart = _get_cart(request)
    item = get_object_or_404(MenuItem, id=item_id)

    item_id = str(item_id)

    if item_id in cart:
        cart[item_id]['quantity'] += 1
    else:
        cart[item_id] = {
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'quantity': 1,
            'image': item.image.url if item.image else ''
        }

    _save_cart(request, cart)
    return redirect('cart')


def remove_from_cart(request, item_id):
    cart = _get_cart(request)
    item_id = str(item_id)

    if item_id in cart:
        del cart[item_id]

    _save_cart(request, cart)
    return redirect('cart')


def increase_item(request, item_id):
    cart = _get_cart(request)
    item_id = str(item_id)

    if item_id in cart:
        cart[item_id]['quantity'] += 1

    _save_cart(request, cart)
    return redirect('cart')


def decrease_item(request, item_id):
    cart = _get_cart(request)
    item_id = str(item_id)

    if item_id in cart:
        cart[item_id]['quantity'] -= 1
        if cart[item_id]['quantity'] <= 0:
            del cart[item_id]

    _save_cart(request, cart)
    return redirect('cart')


def clear_cart(request):
    request.session['cart'] = {}
    return redirect('cart')


def cart_count_api(request):
    cart = request.session.get('cart', {})
    total = sum(item['quantity'] for item in cart.values())
    return JsonResponse({'count': total})


def cart(request):
    cart = _get_cart(request)
    total_price = 0

    for item in cart.values():
        item['total'] = item['price'] * item['quantity']
        total_price += item['total']

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total_price = total_price
            order.save()

            for item_id, item in cart.items():
                menu_item = get_object_or_404(MenuItem, id=item_id)

                OrderItem.objects.create(
                    order=order,
                    item_name=menu_item.name,
                    price=item['price'],
                    quantity=item['quantity']
                )

            _save_cart(request, {})
            messages.success(request, f'Заказ #{order.id} создан!')
            return redirect('cart')
    else:
        form = OrderForm()

    return render(request, 'main/cart.html', {
        'cart': cart,
        'total_price': total_price,
        'form': form
    })


# =========================
# CART API
# =========================
@csrf_exempt
def add_to_cart_api(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    try:
        data = json.loads(request.body)
        item = get_object_or_404(MenuItem, id=data['item_id'])

        cart = _get_cart(request)
        item_id = str(item.id)

        if item_id in cart:
            cart[item_id]['quantity'] += int(data.get('quantity', 1))
        else:
            cart[item_id] = {
                'id': item.id,
                'name': item.name,
                'price': float(item.price),
                'quantity': int(data.get('quantity', 1)),
                'image': item.image.url if item.image else ''
            }

        _save_cart(request, cart)

        return JsonResponse({
            'success': True,
            'cart_count': sum(i['quantity'] for i in cart.values())
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# =========================
# REVIEWS (MENU ITEM) - ИСПРАВЛЕНО
# =========================
def get_item_reviews(request, item_id):
    """Возвращает отзывы в формате, ожидаемом фронтендом"""
    reviews = MenuItemReview.objects.filter(
        menu_item_id=item_id,
        is_approved=True
    ).values('author_name', 'rating', 'text', 'created_at')
    
    # Преобразуем created_at в строку для JSON
    reviews_list = []
    for review in reviews:
        reviews_list.append({
            'author_name': review['author_name'],
            'rating': review['rating'],
            'text': review['text'],
            'created_at': review['created_at'].isoformat() if review['created_at'] else None
        })
    
    # Возвращаем в формате, который ожидает фронтенд
    return JsonResponse({
        'success': True,
        'reviews': reviews_list
    })


def get_item_details(request, item_id):
    item = get_object_or_404(MenuItem, id=item_id)

    return JsonResponse({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'price': float(item.price),
        'image': item.image.url if item.image else ''
    })


@csrf_exempt
def add_item_review(request):
    if request.method != 'POST':
        return JsonResponse({'success': False})

    try:
        data = json.loads(request.body)

        MenuItemReview.objects.create(
            menu_item_id=data['item_id'],
            author_name=data.get('author_name', 'Гость'),
            rating=data.get('rating', 5),
            text=data.get('text', ''),
            is_approved=False
        )

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def profile(request):
    orders = Order.objects.filter().order_by('-created_at')  # позже привяжем к user
    profile, created = Profile.objects.get_or_create(user=request.user)

    return render(request, 'main/profile.html', {
        'orders': orders,
        'profile': profile
    })