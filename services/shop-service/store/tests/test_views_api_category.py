from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase,APIClient
from rest_framework import status
from django.contrib.auth.models import User
from store.models import Category

class CategoryViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'regular_user',
            password = 'password123'
        )

        self.admin_user = User.objects.create_superuser(
            username = 'admin_user',
            password = 'admin123',
            email = 'admin@example.com'
        )

        self.category_tea = Category.objects.create(
            name = "Tea",
            slug = "tea",
            description = "All kinds of tea"
        )

        self.category_coffee = Category.objects.create(
            name = "Coffee",
            slug = "coffee"
        )

        self.category_green_tea = Category.objects.create(
            name = "Green Tea",
            parent = self.category_tea
        )

        self.client = APIClient()
        self.categories_url = reverse('category-list')

    def test_list_categories(self):
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results),3)
        category_names = [cat['name'] for cat in results]
        self.assertIn('Tea',category_names)
        self.assertIn('Coffee',category_names)
        self.assertIn('Green Tea',category_names)

        for cat in results:
            if cat['name'] == 'Tea':
                self.assertEqual(cat['slug'],'tea')
            elif cat['name'] == 'Coffee':
                self.assertEqual(cat['slug'],'coffee')

    def test_retrieve_category(self):
        url = reverse('category-detail',args = [self.category_tea.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

        self.assertEqual(response.data['name'],'Tea')
        self.assertEqual(response.data['slug'],'tea')
        self.assertEqual(response.data['description'],'All kinds of tea')



    def test_retrieve_category_not_found(self):
        url = reverse('category-detail',args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code,status.HTTP_404_NOT_FOUND)

    def test_create_category_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        new_category = {
            'name' : 'Herbal Tea',
            'description' : 'Healthy herbal teas'
        }

        response = self.client.post(self.categories_url,new_category,format='json')
        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(),4)

        category_db = Category.objects.get(name='Herbal Tea')
        self.assertEqual(category_db.description,'Healthy herbal teas')
        self.assertEqual(category_db.slug,'herbal-tea')

        self.assertEqual(response.data['name'],'Herbal Tea')
        self.assertEqual(response.data['description'],'Healthy herbal teas')
        self.assertEqual(response.data['slug'],'herbal-tea')

    def test_create_category_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        new_category = {
            'name' : 'Herbal Tea'
        }

        response = self.client.post(self.categories_url,new_category,format = 'json')
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(),3)

    def test_update_category_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)

        update_data = {
            'name' : 'Premium Tea',
            'description':'High quality tea'
        }

        url = reverse('category-detail',args=[self.category_tea.id])
        response = self.client.patch(url,update_data,format='json')

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.category_tea.refresh_from_db()
        self.assertEqual(self.category_tea.name, 'Premium Tea')
        self.assertEqual(self.category_tea.description, 'High quality tea')
        self.assertEqual(self.category_tea.slug,'tea')

        self.assertEqual(response.data['name'],'Premium Tea')
        self.assertEqual(response.data['description'],'High quality tea')

    def test_update_category_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        update_data = {
            'name' : 'Hacked Tea'
        }

        url = reverse('category-detail',args=[self.category_tea.id])
        response = self.client.patch(url,update_data,format='json')

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

        self.category_tea.refresh_from_db()
        self.assertEqual(self.category_tea.name,'Tea')

    def test_delete_category_as_admin(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('category-detail',args=[self.category_coffee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(),2)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=self.category_coffee.id)

    def test_delete_category_as_regular_user_forbidden(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('category-detail',args=[self.category_coffee.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
        self.assertEqual(Category.objects.count(),3)

    def test_delete_category_with_children(self):
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('category-detail',args=[self.category_tea.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(),1)
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=self.category_green_tea.id)