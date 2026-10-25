from django.contrib.auth.models import User
from django.test import TestCase

from address.models import Address
from billing_profile.models import BillingProfile
from cart.models import Cart
from product.models import Product

from .models import Order


class OrderTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@correo.com', 'clave12345')
        self.address = Address.objects.create(
            street='Calle 1', city='CDMX', state='CDMX', country='Mexico', postal_code='01000'
        )
        self.billing = BillingProfile.objects.create(
            user=self.admin, email='admin@correo.com', address=self.address
        )
        self.cart = Cart.objects.create(user=self.admin)
        self.cart.products.add(
            Product.objects.create(name='Taza', description='Ceramica', price=120),
            Product.objects.create(name='Gorra', description='Negra', price=250),
        )
        self.order = Order.objects.create(
            billing_profile=self.billing,
            shipping_address=self.address,
            cart=self.cart,
            shipping_total=30,
        )

    def test_total_de_la_orden(self):
        self.assertEqual(self.order.update_total(), 400)
        self.assertEqual(self.order.status, 'created')

    def test_modelos_en_el_admin(self):
        self.client.force_login(self.admin)
        response = self.client.get('/admin/')
        for nombre in ['Products', 'Addresses', 'Billing profiles', 'Carts', 'Orders']:
            self.assertContains(response, nombre)

    def test_paginas_del_admin(self):
        self.client.force_login(self.admin)
        for app, modelo in [
            ('product', 'product'),
            ('address', 'address'),
            ('billing_profile', 'billingprofile'),
            ('cart', 'cart'),
            ('orders', 'order'),
        ]:
            for pagina in ['', 'add/', '1/change/']:
                response = self.client.get(f'/admin/{app}/{modelo}/{pagina}')
                self.assertEqual(response.status_code, 200, f'{app}/{modelo}/{pagina}')
