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
 
    path('admin/', admin.site.urls),
    path('', include('authorization.urls_template')),
    path('', include('product.urls_template')),
    path('api/user/',  include(('authorization.urls', 'auth'), namespace='user_auth')),
    path('api/admin/', include(('authorization.urls', 'auth'), namespace='admin_auth')),
    path('api/admin/', include('user.urls')),
    path('api/admin/', include('address.urls_admin')),
    path('api/admin/', include(('category.urls_admin', 'category'), namespace='admin_category')),
    path('api/admin/', include(('product.urls_admin', 'product'), namespace='admin_product')),
    path('api/admin/', include('upload.urls')),
    path('api/admin/', include('cart.urls_admin')),
    path('api/admin/', include('order.urls_admin')),
    path('api/admin/', include('review.urls_admin')),
    path('api/admin/', include('statistic.urls_admin')),
    path('api/', include('authorization.urls_verify')),
    path('api/', include('address.urls')),
    path('api/', include(('category.urls', 'category'), namespace='user_category')),
    path('api/', include(('product.urls', 'product'), namespace='user_product')),
    path('api/', include('cart.urls')),
    path('api/', include('order.urls')),
    path('api/', include('review.urls')),
]