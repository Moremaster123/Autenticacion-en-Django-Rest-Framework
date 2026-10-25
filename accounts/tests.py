from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

DATOS = {
    'username': 'ana',
    'first_name': 'Ana',
    'last_name': 'López',
    'email': 'ana@correo.com',
    'password1': 'ClaveSegura2026',
    'password2': 'ClaveSegura2026',
}


class RegisterTests(TestCase):
    def test_registro_correcto(self):
        response = self.client.post(reverse('accounts:register'), DATOS, follow=True)
        self.assertContains(response, 'El usuario ana se registró correctamente.')
        user = User.objects.get(username='ana')
        self.assertEqual(user.email, 'ana@correo.com')
        self.assertTrue(user.check_password('ClaveSegura2026'))
        self.assertFalse(user.is_staff)

    def test_contrasenas_distintas(self):
        datos = {**DATOS, 'password2': 'OtraClave2026'}
        response = self.client.post(reverse('accounts:register'), datos)
        self.assertContains(response, 'Las contraseñas no coinciden.')
        self.assertFalse(User.objects.exists())

    def test_correo_repetido(self):
        User.objects.create_user('otro', email='ana@correo.com')
        response = self.client.post(reverse('accounts:register'), {**DATOS, 'email': 'ANA@correo.com'})
        self.assertContains(response, 'Ya existe un usuario con este correo.')

    def test_contrasena_debil(self):
        datos = {**DATOS, 'password1': '123', 'password2': '123'}
        self.client.post(reverse('accounts:register'), datos)
        self.assertFalse(User.objects.filter(username='ana').exists())

    def test_campos_obligatorios(self):
        response = self.client.post(reverse('accounts:register'), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['form'].errors), 6)
