from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from products.models import Product, Category, ProductImage
from orders.models import Order, OrderItem
from django.utils import timezone
from datetime import timedelta
import time

User = get_user_model()

class PerformanceTests(TestCase):
    def setUp(self):
        # Setup data for performance testing
        self.user = User.objects.create_superuser(
            email='admin@magicafro.com',
            password='password123'
        )
        self.client = Client()
        self.client.login(email='admin@magicafro.com', password='password123')
        
        # Create categories and products
        self.category = Category.objects.create(name="Cheveux", slug="cheveux")
        self.products = []
        for i in range(20):
            p = Product.objects.create(
                name=f"Produit {i}",
                slug=f"produit-{i}",
                price=1500.0,
                category=self.category,
                stock=10
            )
            self.products.append(p)
            ProductImage.objects.create(product=p, is_feature=True)

        # Create orders over the last 10 days
        for i in range(10):
            order_date = timezone.now() - timedelta(days=i)
            order = Order.objects.create(
                user=self.user,
                total=5000.0,
                payment_status=True,
                status='PAID'
            )
            # Manually set created_at as it's auto_now_add
            Order.objects.filter(id=order.id).update(created_at=order_date)
            
            OrderItem.objects.create(
                order=order,
                product=self.products[0],
                quantity=2,
                unit_price=2500.0
            )

    def test_dashboard_home_query_count(self):
        """
        Verify that the dashboard home page perform a limited number of queries 
        now that it has been optimized.
        """
        url = reverse('dashboard:home')
        
        # Before optimization: ~15-20 queries (due to loop)
        # After optimization: ~6-8 queries
        with self.assertNumQueries(8):
            response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)

    def test_product_list_query_count(self):
        """
        Verify that the product list performs optimized queries with select_related.
        """
        url = reverse('dashboard:product_list')
        
        # Should be ~4-5 queries (auth + products + categories count)
        with self.assertNumQueries(5):
            response = self.client.get(url)
            
        self.assertEqual(response.status_code, 200)

    def test_dashboard_home_performance_speed(self):
        """
        Measure execution time for the dashboard home.
        """
        url = reverse('dashboard:home')
        
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"\n[BENCHMARK] Dashboard Home execution time: {execution_time:.4f}s")
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(execution_time, 0.5) # Should be well under 500ms on a local dev machine
