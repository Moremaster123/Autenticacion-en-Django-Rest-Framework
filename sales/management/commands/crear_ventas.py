import random
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from address.models import Address
from billing_profile.models import BillingProfile
from cart.models import Cart
from orders.models import STATUS_CHOICES, Order
from product.models import Product

PRODUCTOS = [
    ('Camiseta', 199),
    ('Taza', 120),
    ('Gorra', 250),
    ('Mochila', 799),
    ('Sudadera', 549),
]


class Command(BaseCommand):
    help = 'Crea productos, clientes y órdenes de prueba de los últimos 7 días.'

    def add_arguments(self, parser):
        parser.add_argument('--ordenes', type=int, default=30)

    def handle(self, *args, **options):
        productos = [
            Product.objects.get_or_create(
                name=nombre, defaults={'description': nombre, 'price': precio, 'stock': 50}
            )[0]
            for nombre, precio in PRODUCTOS
        ]
        estados = [value for value, label in STATUS_CHOICES]
        ahora = timezone.now()
        inicio = User.objects.filter(username__startswith='cliente').count()

        for i in range(options['ordenes']):
            numero = inicio + i + 1
            user = User.objects.create_user(f'cliente{numero}')
            address = Address.objects.create(
                street=f'Calle {numero}',
                city='CDMX',
                state='CDMX',
                country='Mexico',
                postal_code='01000',
            )
            billing = BillingProfile.objects.create(
                user=user, email=f'cliente{numero}@correo.com', address=address
            )
            cart = Cart.objects.create(user=user)
            cart.products.add(*random.sample(productos, random.randint(1, 3)))
            order = Order.objects.create(
                billing_profile=billing,
                shipping_address=address,
                cart=cart,
                status=random.choices(estados, weights=[3, 4, 4, 1])[0],
                shipping_total=50,
            )
            order.update_total()
            fecha = ahora - timedelta(days=random.randint(0, 6), hours=random.randint(0, 8))
            Order.objects.filter(id=order.id).update(created_at=fecha, updated_at=fecha)

        self.stdout.write(self.style.SUCCESS(f'Se crearon {options["ordenes"]} órdenes de prueba.'))
