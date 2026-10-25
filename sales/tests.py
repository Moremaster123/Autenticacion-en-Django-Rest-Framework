from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from address.models import Address
from billing_profile.models import BillingProfile
from cart.models import Cart
from orders.models import Order
from product.models import Product

AJAX = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}


class SalesTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@correo.com', 'clave12345')
        address = Address.objects.create(
            street='Calle 1', city='CDMX', state='CDMX', country='Mexico', postal_code='01000'
        )
        billing = BillingProfile.objects.create(
            user=self.admin, email='admin@correo.com', address=address
        )
        cart = Cart.objects.create(user=self.admin)
        cart.products.add(Product.objects.create(name='Taza', description='Taza', price=120))
        order = Order.objects.create(
            billing_profile=billing, shipping_address=address, cart=cart, status='paid'
        )
        order.update_total()

    def test_pagina_de_ventas(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('sales:sales'))
        self.assertContains(response, '<canvas id="salesChart"')
        self.assertContains(response, '$120')

    def test_datos_por_ajax(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('sales:sales-data'), **AJAX)
        data = response.json()
        self.assertEqual(len(data['labels']), 7)
        self.assertEqual(data['totals'][-1], 120)
        self.assertEqual(data['status_counts'], [0, 1, 0, 0])

    def test_rechaza_peticion_que_no_es_ajax(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('sales:sales-data'))
        self.assertEqual(response.status_code, 400)

    def test_solo_staff(self):
        response = self.client.get(reverse('sales:sales'))
        self.assertEqual(response.status_code, 302)
        cliente = User.objects.create_user('cliente', password='clave12345')
        self.client.force_login(cliente)
        response = self.client.get(reverse('sales:sales-data'), **AJAX)
        self.assertEqual(response.status_code, 403)
