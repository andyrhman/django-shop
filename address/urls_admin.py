from django.urls import path
from address.views import AddressAPIView

urlpatterns = [
    path("address", AddressAPIView.as_view())
]