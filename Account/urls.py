from django.urls import path
from .views import ChangePasswordApiView, ListCreateDeleteDeliveryLocationApiView, MatchedDeliveryLocationsApiView, UserRegistrationApiView, UserApiView, LoginApiView


urlpatterns = [
    path('', UserApiView.as_view()),
    path('register/', UserRegistrationApiView.as_view()),
    path('login/', LoginApiView.as_view()),
    path('change-password/', ChangePasswordApiView.as_view()),
    path('delivery-locations/', ListCreateDeleteDeliveryLocationApiView.as_view()),
    path('add-delivery-location/', ListCreateDeleteDeliveryLocationApiView.as_view()),
    path('matched-delivery-locations/<restaurant_id>/', MatchedDeliveryLocationsApiView.as_view()),
    path('delivery-location/<pk>/', ListCreateDeleteDeliveryLocationApiView.as_view()),
]