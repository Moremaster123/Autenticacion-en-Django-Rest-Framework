from django.db import models

from address.models import Address
from billing_profile.models import BillingProfile
from cart.models import Cart

STATUS_CHOICES = [
    ('created', 'Creada'),
    ('paid', 'Pagada'),
    ('shipped', 'Enviada'),
    ('refunded', 'Reembolsada'),
]


class Order(models.Model):
    billing_profile = models.ForeignKey(BillingProfile, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.DO_NOTHING)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    shipping_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_total(self):
        self.total = self.cart.get_total() + self.shipping_total
        self.save()
        return self.total

    def __str__(self):
        return f"Orden {self.id}"
