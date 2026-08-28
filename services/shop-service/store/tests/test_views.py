from django.test import TestCase
from django.urls import reverse
from store.models import Category, Product

class ProductViewsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tea")
        self.product = Product.objects.create(
            name = "Green Tea",
            price = 259,
            category = self.category
        )

    def test_product_list_view_status_code(self):
        url = reverse("product_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code,200)

    def test_product_list_view_contains_product(self):
        url = reverse("product_list")
        response = self.client.get(url)
        self.assertContains(response,"Green Tea")

    def test_product_list_view_uses_correct_template(self):
        url = reverse("product_list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "store/product_list.html")

    def test_product_list_view_empty(self):
        Product.objects.all().delete()
        url = reverse("product_list")
        response = self.client.get(url)
        self.assertContains(response,"Нет доступных товаров.")

    def test_product_list_view_filters_by_category(self):
        other_category = Category.objects.create(name = "Coffee")
        Product.objects.create(name="Espresso",price=199,category=other_category)
        url = reverse("product_list")
        response = self.client.get(url)
        self.assertContains(response,"Green Tea")
        self.assertContains(response,"Espresso")

    def test_product_list_view_filters_by_category_param(self):
        other_category = Category.objects.create(name="Coffee")
        Product.objects.create(name="Espresso",price=199,category=other_category)
        url = reverse("product_list") + "?category=Tea"
        response = self.client.get(url)
        self.assertContains(response,"Green Tea")
        self.assertNotContains(response,"Espresso")

    def test_product_list_view_filters_by_price_range(self):
        Product.objects.create(name="Cheap Mouse",price=100,category=self.category)
        Product.objects.create(name="Expensive Laptop", price=5000, category = self.category)
        url = reverse("product_list") + "?min_price=200&max_price=1000"
        response = self.client.get(url)
        self.assertNotContains(response,"Cheap Mouse")
        self.assertNotContains(response,"Expensive Laptop")

        Product.objects.create(name="Midrange Keyboard",price=500,category=self.category)
        response = self.client.get(url)
        self.assertContains(response,"Midrange Keyboard")

    def test_product_list_view_filters_by_search_query(self):
        Product.objects.create(name="Gaming Chair",price=3000,category=self.category)
        Product.objects.create(name="Office Desk",price=2000,category=self.category)
        url = reverse("product_list") + "?q=Chair"
        response = self.client.get(url)

        self.assertContains(response,"Gaming Chair")
        self.assertNotContains(response,"Office Desk")

    def test_product_list_view_filter_by_min_price(self):
        Product.objects.create(name="Cheap Mouse",price=100,category = self.category)
        Product.objects.create(name="Midrange Keyboard",price=500,category=self.category)
        url = reverse("product_list") + "?min_price=200"
        response = self.client.get(url)
        self.assertNotContains(response,"Cheap Mouse")
        self.assertContains(response,"Midrange Keyboard")

    def test_product_list_view_filter_by_max_price(self):
        Product.objects.create(name="Midrange Keyboard",price=500, category=self.category)
        Product.objects.create(name="Expensive Laptop",price=5000,category=self.category)
        url = reverse("product_list") + "?max_price=1000"
        response = self.client.get(url)
        self.assertContains(response,"Midrange Keyboard")
        self.assertNotContains(response,"Expensive Laptop")