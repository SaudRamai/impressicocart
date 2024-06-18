from django.urls import path,include
from ..myapp.views import index

urlpatterns = [
    path('', index, name='index'),
    path('api/', include('product_search.urls')),

]