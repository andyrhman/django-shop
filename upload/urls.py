from django.urls import path

from upload.views import ImageUploadAPIView


urlpatterns = [
    path('upload', ImageUploadAPIView.as_view())
]