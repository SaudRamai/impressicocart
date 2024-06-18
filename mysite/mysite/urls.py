"""OnlineShopping URL Configuration
 
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    from django.urls import include
    urlpatterns += [path('product/', include('product.urls')),
                     path('category/', include('category.urls')),
                     path('user/', include('user.urls'))]

    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin # type: ignore
from django.urls import path # type: ignore
from myapp.views import *

from django.conf import settings # type: ignore
from django.conf.urls.static import static # type: ignore
 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('login/', loginPage,name='login'),
    path('logout/', logoutPage, name='logout'),
    path('register/', registerPage,name='register'),
    path('products', product_search_view, name='products'),
    path('search/', search_view, name='search_results'),
    path('autosuggest/', autosuggest, name='autosuggest'),
    path('thumnails/', products_thumbnails, name='products_thumbnails'),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
