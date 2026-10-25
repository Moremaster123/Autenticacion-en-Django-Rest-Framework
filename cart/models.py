from django.contrib.auth.models import User
from django.db import models

from product.models import Product


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_total(self):
        return sum(product.price for product in self.products.all())

    def __str__(self):
        return f"Carrito {self.id} de {self.user}"
