from django.test import TestCase
from store.models import Product, Category

class ProductTestCase(TestCase):
    def test_create_category(self):
        category = Category.objects.create(name="Tea")
        self.assertEqual(category.name, "Tea")

    def test_str_method(self):
        category = Category.objects.create(name="Coffee")
        self.assertEqual(str(category),"Coffee")

class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tea")
        self.product = Product.objects.create(
            name = "Green Tea",
            price = 259,
            category = self.category
        )

    def test_product_creation(self):
        self.assertEqual(self.product.name, "Green Tea")
        self.assertEqual(self.product.price,259)
        self.assertEqual(self.product.category.name, "Tea")

    def test_str_method(self):
        self.assertEqual(str(self.product),"Green Tea")

    def test_price_in_integer(self):
        self.assertIsInstance(self.product.price,int)