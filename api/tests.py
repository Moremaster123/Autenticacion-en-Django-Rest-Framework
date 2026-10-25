from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import Product


class ProductViewSetTests(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Taza', description='Cerámica', price=120, stock=10)
        self.list_url = reverse('api:product-list')
        self.detail_url = reverse('api:product-detail', args=[self.product.pk])

    def test_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([p['name'] for p in response.data['resultados']], ['Taza'])

    def test_create(self):
        data = {'name': 'Gorra', 'description': 'Negra', 'price': '250.00', 'stock': 5}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(name='Gorra').exists())

    def test_create_invalido(self):
        response = self.client.post(self.list_url, {'name': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.data['name'], 'Taza')

    def test_retrieve_no_existe(self):
        response = self.client.get(reverse('api:product-detail', args=[999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        data = {'name': 'Taza grande', 'description': 'Cerámica', 'price': '150.00', 'stock': 8}
        response = self.client.put(self.detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual((self.product.name, self.product.stock), ('Taza grande', 8))

    def test_update_incompleto_falla(self):
        response = self.client.put(self.detail_url, {'stock': 3}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update(self):
        response = self.client.patch(self.detail_url, {'stock': 3}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual((self.product.name, self.product.stock), ('Taza', 3))

    def test_destroy(self):
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.exists())


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@correo.com', 'ClaveAdmin2026')
        self.cliente = User.objects.create_user('cliente', 'cliente@correo.com', 'ClaveCliente2026')
        self.list_url = reverse('api:user-list')

    def test_solo_admin(self):
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.cliente)
        self.assertEqual(self.client.get(self.list_url).status_code, status.HTTP_403_FORBIDDEN)

    def test_crud_de_usuarios(self):
        self.client.force_authenticate(self.admin)
        data = {'username': 'ana', 'email': 'ana@correo.com', 'password': 'ClaveSegura2026'}
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)
        ana = User.objects.get(username='ana')
        self.assertTrue(ana.check_password('ClaveSegura2026'))

        detail_url = reverse('api:user-detail', args=[ana.pk])
        response = self.client.patch(detail_url, {'first_name': 'Ana'}, format='json')
        self.assertEqual(response.data['first_name'], 'Ana')

        self.assertEqual(self.client.get(self.list_url).data['total'], 3)
        self.assertEqual(self.client.delete(detail_url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(username='ana').exists())


class PaginationTests(APITestCase):
    def setUp(self):
        for i in range(1, 8):
            Product.objects.create(name=f'Producto {i}', description='Prueba', price=10 * i)
        self.url = reverse('api:product-list')

    def nombres(self, response):
        return [p['name'] for p in response.data['resultados']]

    def test_primera_pagina(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data['total'], 7)
        self.assertEqual(response.data['pagina_actual'], 1)
        self.assertEqual(response.data['total_paginas'], 3)
        self.assertIsNone(response.data['anterior'])
        self.assertIn('pagina=2', response.data['siguiente'])
        self.assertEqual(self.nombres(response), ['Producto 1', 'Producto 2', 'Producto 3'])

    def test_ultima_pagina(self):
        response = self.client.get(self.url, {'pagina': 'ultima'})
        self.assertEqual(response.data['pagina_actual'], 3)
        self.assertIsNone(response.data['siguiente'])
        self.assertEqual(self.nombres(response), ['Producto 7'])

    def test_tamano_personalizado(self):
        response = self.client.get(self.url, {'por_pagina': 5, 'pagina': 2})
        self.assertEqual(response.data['total_paginas'], 2)
        self.assertEqual(self.nombres(response), ['Producto 6', 'Producto 7'])

    def test_tamano_maximo(self):
        for i in range(8, 26):
            Product.objects.create(name=f'Producto {i}', description='Prueba', price=1)
        response = self.client.get(self.url, {'por_pagina': 100})
        self.assertEqual(len(response.data['resultados']), 20)

    def test_pagina_que_no_existe(self):
        response = self.client.get(self.url, {'pagina': 9})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'La página que buscas no existe.')


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.ana = User.objects.create_user('ana', 'ana@correo.com', 'ClaveAna2026', first_name='Ana')
        self.luis = User.objects.create_user('luis', 'luis@correo.com', 'ClaveLuis2026', first_name='Luis')
        self.profile_url = reverse('api:profile')

    def login(self, username, password):
        return self.client.post(reverse('api:login'), {'username': username, 'password': password}, format='json')

    def test_perfil_sin_login(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_incorrecto(self):
        response = self.login('ana', 'otra')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', response.data)

    def test_cada_usuario_ve_su_perfil(self):
        for user, password in [(self.ana, 'ClaveAna2026'), (self.luis, 'ClaveLuis2026')]:
            token = self.login(user.username, password).data['token']
            self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
            response = self.client.get(self.profile_url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['id'], user.id)
            self.assertEqual(response.data['email'], user.email)
            self.assertNotIn('password', response.data)

    def test_token_falso(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token tokenfalso123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_invalida_el_token(self):
        token = self.login('ana', 'ClaveAna2026').data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
        self.assertEqual(self.client.post(reverse('api:logout')).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(self.profile_url).status_code, status.HTTP_401_UNAUTHORIZED)
