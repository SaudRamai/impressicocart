
from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    name = models.CharField(max_length=200, null=True)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class AggregatedCategory(models.Model):
    main_category = models.CharField(max_length=250)
    sub_category = models.CharField(max_length=250)

    def __str__(self):
        return self.sub_category


class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    no_of_ratings = models.IntegerField(null=True)
    sub_category = models.CharField(max_length=100, null=True)
    actual_price = models.CharField(max_length=100, default=0.00)
    ratings = models.CharField( max_length=100, null=True)
    discount_price = models.CharField(max_length=100,  null=True)
    name = models.CharField(max_length=255, null=True)
    link = models.URLField(null=True)  
    main_category = models.CharField(max_length=100, null=True)  

    def __str__(self):
        return self.name
        


