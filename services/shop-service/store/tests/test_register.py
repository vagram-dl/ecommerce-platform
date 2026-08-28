from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

class RegisterViewTests(TestCase):
    def setUp(self):
        self.register_url = reverse('register')

    def test_register_page_loads(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'store/register.html')
        self.assertIn('form',response.context)

    def test_register_success(self):
        user_data = {
            'username':'newuser',
            'password1' : 'testpass123',
            'password2':'testpass123',
        }

        response = self.client.post(self.register_url,user_data)
        self.assertRedirects(response,reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

        user = User.objects.get(username = 'newuser')
        self.assertNotEqual(user.password,'testpass123')
        self.assertTrue(user.password.startswith('pbkdf2_'))

    def test_register_duplicate_username(self):
        User.objects.create_user(username = 'existing',password = 'pass123')

        user_data = {
            'username' : 'existing',
            'password1' : 'newpass123',
            'password2':'newpass123'
        }

        response = self.client.post(self.register_url,user_data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(User.objects.filter(username='existing').count(),1)
        self.assertFormError(
            response.context['form'],
            'username',
            "A user with that username already exists."
        )

    def test_register_password_too_short(self):
        user_data = {
            'username' : 'newuser',
            'password1' : 'short',
            'password2' : 'short',
        }

        response = self.client.post(self.register_url,user_data)
        self.assertEqual(response.status_code,200)
        self.assertFalse(User.objects.filter(username='newuser').exists())
        self.assertFormError(response.context['form'],'password2',"This password is too short. It must contain at least 8 characters.")

    def test_register_empty_username(self):
        user_data = {
            'username' : '',
            'password1' : 'testpass123',
            'password2' : 'testpass123',
        }

        response = self.client.post(self.register_url,user_data)
        self.assertEqual(response.status_code,200)
        self.assertEqual(User.objects.count(),0)
        self.assertFormError(response.context['form'],'username',"This field is required.")

    def test_register_authenticated_user_redirect(self):
        user = User.objects.create_user(username='testuser',password = 'pass123')
        self.client.login(username='testuser',password = 'pass123')
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'store/register.html')
        self.assertIn('form',response.context)
