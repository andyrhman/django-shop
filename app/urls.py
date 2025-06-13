""" URL configuration for app project.
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('success/', TemplateView.as_view(template_name='success.html'), name='success'),
    path('error/', TemplateView.as_view(template_name='error.html'), name='error'),
 
    path('admin/', admin.site.urls),
    path('', include('authorization.urls_template')),
    path('', include('product.urls_template')),
    path('', include('cart.urls_template')),
    path('api/user/',  include(('authorization.urls', 'auth'), namespace='user_auth')),
    path('api/admin/', include(('authorization.urls', 'auth'), namespace='admin_auth')),
    path('api/admin/', include(('user.urls', 'user'), namespace='admin_user')),
    path('api/admin/', include(('address.urls_admin', 'address'), namespace='admin_address')),
    path('api/admin/', include(('category.urls_admin', 'category'), namespace='admin_category')),
    path('api/admin/', include(('product.urls_admin', 'product'), namespace='admin_product')),
    path('api/admin/', include(('upload.urls', 'upload'), namespace='admin_upload')),
    path('api/admin/', include(('cart.urls_admin', 'cart'), namespace='admin_cart')),
    path('api/admin/', include(('order.urls_admin', 'order'), namespace='admin_order')),
    path('api/admin/', include(('review.urls_admin', 'review'), namespace='admin_review')),
    path('api/admin/', include(('statistic.urls_admin', 'statistic'), namespace='admin_statistic')),
    path('api/', include(('authorization.urls_verify', 'verify'), namespace='user_verify')),
    path('api/', include(('address.urls', 'address'), namespace='user_address')),
    path('api/', include(('category.urls', 'category'), namespace='user_category')),
    path('api/', include(('product.urls', 'product'), namespace='user_product')),
    path('api/', include(('cart.urls', 'cart'), namespace='user_cart')),
    path('api/', include(('order.urls', 'order'), namespace='user_order')),
    path('api/', include(('review.urls', 'review'), namespace='user_review')),
]