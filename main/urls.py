from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('menu/', views.menu, name='menu'),
    path('reservation/', views.reservation, name='reservation'),
    path('contact/', views.contact, name='contact'),
    path('news/', views.news, name='news'),
    path('news/<int:news_id>/', views.news_detail, name='news_detail'),

    # CART
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:item_id>/', views.increase_item, name='increase_item'),
    path('cart/decrease/<int:item_id>/', views.decrease_item, name='decrease_item'),
    path('cart/clear/', views.clear_cart, name='clear_cart'),
    path('cart/count/api/', views.cart_count_api, name='cart_count_api'),

    # CART API
    path('cart/add/api/', views.add_to_cart_api, name='add_to_cart_api'),

    # REVIEWS API
    path('api/reviews/<int:item_id>/', views.get_item_reviews, name='get_item_reviews'),
    path('api/reviews/add/', views.add_item_review, name='add_item_review'),
    path('api/item/<int:item_id>/', views.get_item_details, name='get_item_details'),
path('profile/', views.profile, name='profile'),
path('cart/clear/', views.clear_cart, name='clear_cart')
]
from django.contrib.auth import views as auth_views

urlpatterns += [
    path('login/', auth_views.LoginView.as_view(template_name='main/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]