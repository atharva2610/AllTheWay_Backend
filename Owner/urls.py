from django.urls import path
from . import views


urlpatterns = [
    path('', views.AllRestaurantsByOwner.as_view()),
    path('add-restaurant/', views.CreateUpdateDeleteRestaurant.as_view()),
    path('cuisines/', views.ListCuisines.as_view()),
    path('add-menu-item/', views.CreateUpdateDeleteMenuItem.as_view()),
    path('order/<pk>/', views.RetrieveUpdateOrder.as_view()),
    path('update-order-status/<pk>/', views.RetrieveUpdateOrder.as_view()),
    path('menu-item/<pk>/', views.RetrieveMenuItem.as_view()),
    path('<pk>/', views.RetrieveRestaurant.as_view()),
    path('cuisines-by-restaurant/<restaurant_id>/', views.CuisinesByRestaurant.as_view()),
    path('update-restaurant/<pk>/', views.CreateUpdateDeleteRestaurant.as_view()),
    path('delete-restaurant/<pk>/', views.CreateUpdateDeleteRestaurant.as_view()),
    path('change-restaurant-banner/<pk>/', views.ChangeRestaurantBanner.as_view()),
    path('menu-items/<restaurant_id>/', views.ListMenuItems.as_view()),
    path('update-menu-item/<pk>/', views.CreateUpdateDeleteMenuItem.as_view()),
    path('delete-menu-item/<pk>/', views.CreateUpdateDeleteMenuItem.as_view()),
    path('change-item-image/<pk>/', views.ChangeItemImage.as_view()),
    path('orders/<restaurant_id>/<tag>/', views.RestaurantOrdersList.as_view()),
    path('order-summary/<pk>/', views.OrderSummary.as_view())
]