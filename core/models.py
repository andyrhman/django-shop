import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

# ! Fixing the migration problem if there is unknown error
# ? https://chat.openai.com/c/a2bedf2d-801d-4814-8298-9dd7fb0973c3
"""
TLDR;
Delete the migrations file, drop the tables, and do this
python manage.py flush
python manage.py makemigrations your_app_name
python manage.py migrate
"""

# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not username:
            raise ValueError("User must have a username")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.is_admin = False
        user.is_staff = False
        user.is_ambassador = False
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None):
        if not email:
            raise ValueError("User must have an email")
        if not username:
            raise ValueError("User must have a username")
        if not password:
            raise ValueError("User must have a password")

        user = self.model(email=self.normalize_email(email), username=username)
        user.set_password(password)
        user.is_admin = True
        user.is_ambassador = False
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    fullName = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, unique=True)
    is_user = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    first_name = None
    last_name = None
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]  # Ensures email is prompted when creating superuser

    objects = UserManager()

class Token(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    user = models.ForeignKey(User, null=True, related_name='token', on_delete=models.SET_NULL)
    token = models.CharField(max_length=255, unique=True)
    expiresAt = models.DateTimeField()
    used = models.BooleanField(default=False)

class Reset(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=255, unique=True)
    expiresAt = models.DateTimeField()
    used = models.BooleanField(default=False)

class Category(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)

class Product(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)   
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, null=True)
    image = models.CharField(max_length=255)
    price = models.FloatField()
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL, related_name='product_categories')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ProductVariation(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, null=False, on_delete=models.CASCADE, related_name='products_variation')

class ProductImages(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    product = models.ForeignKey(Product, null=False, on_delete=models.CASCADE, related_name='products_images')

class Address(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    zip = models.CharField(max_length=20)
    country = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    user = models.OneToOneField(User, null=False, on_delete=models.CASCADE, related_name='address_users')

class Order(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    transaction_id = models.CharField(max_length=255, null=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='order_users')
    
    @property
    def total(self):
        return sum(item.quantity * item.price for item in self.order_items.all())

    @property
    def total_orders(self):
        return self.order_items.count()

class OrderItemStatus(models.TextChoices):
    SEDANG_DIKEMAS = 'Sedang Dikemas', 'Sedang Dikemas'
    DIKIRIM = 'Dikirim', 'Dikirim'
    SELESAI = 'Selesai', 'Selesai'

class OrderItem(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    product_title = models.CharField(max_length=255)
    price = models.FloatField()
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=OrderItemStatus.choices, default=OrderItemStatus.SEDANG_DIKEMAS)
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, related_name='order_items_order')
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, related_name='order_items_products')
    variant = models.ForeignKey(ProductVariation, null=True, on_delete=models.SET_NULL, related_name='order_items_variants')

class Cart(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    product_title = models.CharField(max_length=255)
    price = models.FloatField()
    quantity = models.IntegerField()
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, related_name='cart_products')
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='cart_users')
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, related_name='cart_orders')
    variant = models.ForeignKey(ProductVariation, null=True, on_delete=models.SET_NULL, related_name='cart_variants')

class Review(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    star = models.IntegerField()
    comment = models.TextField(max_length=1000, null=True)
    image = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='review_users')
    product = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL, related_name='review_products')
    order = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL, related_name='review_orders')
    variants = models.ForeignKey(ProductVariation, null=True, on_delete=models.SET_NULL, related_name='review_variants')

    
