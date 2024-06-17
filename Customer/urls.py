from django.urls import path
from . import views

urlpatterns = [
    path('pay/', views.StartPayment.as_view()),
    path('payment/success/', views.PaymentSuccess.as_view()),
    path('orders/', views.ListOrders.as_view()),
    path('order-items/<order_id>/', views.ListOrderItems.as_view()),
    path('create-order/', views.RetrieveCreateOrder.as_view()),
    path('order/<pk>/', views.RetrieveCreateOrder.as_view()),
    path('favorite-restaurants/<favorites>/', views.ListFavoriteRestaurants.as_view()),
    path('update-order-status/<pk>/', views.RetrieveCreateOrder.as_view()),
    path('city/<city_id>/', views.ListRestaurantByCity.as_view()),
    path('city/<city_id>/search-restaurants/<search_for>/', views.ListSearchedRestaurants.as_view()),
    path('city/<city_id>/search-dishes/<search_for>/', views.ListSearchedDishes.as_view()),
    path('cart-items/<items>/', views.CartItems.as_view()),
    path('rate-order/<order_id>/', views.RateOrder.as_view()),
]