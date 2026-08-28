from django.test import TestCase,Client
from django.urls import reverse
from django.contrib.auth.models import User
from store.models import Product,Category

class CartEdgeCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'testuser',
            password = 'testpass123'
        )

        self.category = Category.objects.create(name="Tea")
        self.product = Product.objects.create(
            name = "Green Tea",
            price = 259.99,
            category = self.category
        )

        self.cart_url = reverse('cart_view')
        self.add_to_cart_url = reverse('add_to_cart',args = [self.product.id])
        self.client = Client()


    def test_cart_with_deleted_product(self):
        self.client.login(username='testuser',password = 'testpass123')
        self.client.post(self.add_to_cart_url)
        product_id = self.product.id
        self.product.delete()

        response = self.client.get(self.cart_url)
        self.assertEqual(response.status_code,200)

class AuthEdgeCaseTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'testuser',
            password = 'testpass123'
        )

        self.profile_url = reverse('profile')
        self.login_url = reverse('login')
        self.client = Client()

    def test_401_vs_403_profile(self):
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code,302)
        self.assertIn('login',response.url)

        self.client.login(username='testuser',password='testpass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code,200)

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url,{
            'username' : 'testuser',
            'password' : 'wrongpassword'
        })

        self.assertEqual(response.status_code,200)
        self.assertTemplateUsed(response,'store/login.html')
        self.assertContains(response,'Please enter a correct username and password')
        self.assertTrue(response.context['form'].errors)

    def test_login_empty_username(self):
        response = self.client.post(self.login_url,{
            'username' : '',
            'password':'testpass123'
        })

        self.assertEqual(response.status_code,200)
        self.assertContains(response,'This field is required')

    def test_login_long_username(self):
        long_username = 'a' * 500
        response = self.client.post(self.login_url,{
            'username':'long_username',
            'password':'testpass123'
        })

        self.assertEqual(response.status_code,200)
        self.assertTrue(response.context['form'].errors)

    def test_login_special_chars(self):
        response = self.client.post(self.login_url,{
            'username' : 'testuser',
            'password' : '!@#$%^&*()'
        })

        self.assertEqual(response.status_code,200)
        self.assertContains(response,'Please enter a correct username and password')

    def test_add_nonexistent_product(self):
        self.client.login(username='testuser',password='testpass123')
        url = reverse('add_to_cart',args=[9999])
        response = self.client.post(url)
        self.assertEqual(response.status_code,404)
        
    def test_login_username_with_spaces(self):
        response = self.client.post(self.login_url,{
            'username' : ' testuser ',
            'password' : 'testpass123'
        })

        self.assertEqual(response.status_code,302)
        self.assertRedirects(response,reverse('product_list'))

        profile_response = self.client.get(reverse('profile'))
        self.assertEqual(profile_response.status_code,200)
        self.assertContains(profile_response,'testuser')

    def test_logout(self):
        self.client.post(reverse('login'), {
            'username':'testuser',
            'password':'testpass123'
        })
        profile_response = self.client.get(reverse('profile'))
        logout_response = self.client.post(reverse('logout'))
        self.assertEqual(logout_response.status_code,302)
        self.assertRedirects(logout_response, reverse('product_list'))

        profile_after = self.client.get(reverse('profile'))
        self.assertEqual(profile_after.status_code, 302)
        self.assertIn('login', profile_after.url)







