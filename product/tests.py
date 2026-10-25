from django.test import TestCase
from django.urls import reverse

from .models import Product


class ProductTemplateTests(TestCase):
    def setUp(self):
        for i, nombre in enumerate(['gorra negra', 'mochila', 'taza', 'camiseta'], start=1):
            Product.objects.create(name=nombre, description='PRODUCTO DE PRUEBA', price=100 * i, stock=i)
        Product.objects.create(name='oculto', description='x', price=1, active=False)

    def test_lista_usa_base_y_filtros(self):
        response = self.client.get(reverse('product:list'))
        self.assertTemplateUsed(response, 'base.html')
        self.assertTemplateUsed(response, 'includes/navbar.html')
        self.assertTemplateUsed(response, 'product/includes/product_card.html')
        self.assertContains(response, 'Gorra Negra')
        self.assertContains(response, 'GORRA NEGRA')
        self.assertContains(response, 'Producto de prueba')
        self.assertContains(response, 'Tenemos 4 productos disponibles.')
        self.assertNotContains(response, 'oculto')

    def test_destacado_cada_tres(self):
        response = self.client.get(reverse('product:list'))
        self.assertContains(response, 'Destacado', count=1)
        self.assertContains(response, 'Llevas 3 productos vistos')

    def test_detalle_reutiliza_la_tarjeta(self):
        product = Product.objects.get(name='taza')
        response = self.client.get(reverse('product:detail', args=[product.pk]))
        self.assertContains(response, 'También te puede interesar')
        self.assertContains(response, 'Ver este producto', count=3)
        self.assertNotContains(response, f'href="{reverse("product:detail", args=[product.pk])}"')

    def test_inicio_redirige_a_productos(self):
        response = self.client.get('/')
        self.assertRedirects(response, reverse('product:list'))
