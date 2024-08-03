from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# class CustomUser(AbstractUser):
#     is_regular_user = models.BooleanField(default=False)
#     is_contributor = models.BooleanField(default = False)

class UserProfile(models.Model):
    USER_ROLES = (
        ('author','Author'),
        ('customer','Customer')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=100, choices=USER_ROLES)
    profile_pic = models.ImageField(upload_to=None, blank=True, null = True)
    bio = models.TextField(blank=True, null= True)
    join_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.user.username
    
class Recipe(models.Model):
    title = models.CharField(max_length=250)
    ingredients = models.TextField()
    instructions = models.TextField()
    views = models.IntegerField(default=0, blank=True)
    prep_time = models.IntegerField(help_text="Preparation time in mintues")
    cook_time = models.IntegerField(help_text="Cooking time in mintues")
    servings = models.TextField() #  this is how much per person
    category = models.CharField(max_length=250)
    cuisine  = models.CharField(max_length=250)
    image = models.URLField(blank=True, null = True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=False)
    
    def __str__(self):
        return f'{self.title} - {self.author}'

class Review(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=False)
    
    def __str__(self):
        return f'{self.user.user.username} - {self.recipe.title}'
    
class Collection(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null= True)
    recipes = models.ManyToManyField(Recipe,related_name='collections')
    
    def __str__(self):
        return self.name

class Article(models.Model):
    title = models.CharField(max_length=250)    
    content = models.TextField()
    author = models.ForeignKey(UserProfile,on_delete=models.CASCADE)
    date_published = models.DateTimeField(auto_now_add=False)
    image = models.URLField(blank=True , null =True)
    
    def __str__(self):
        return self.title
    
class Product(models.Model):
    name= models.CharField(max_length=250)
    description = models.TextField()
    price = models.DecimalField( max_digits=10, decimal_places=2)
    category = models.CharField(max_length=250)
    image = models.URLField(blank=True)
    stock = models.IntegerField()
    
    def __str__(self):
        return self.name

class Order(models.Model):
    user = models.ForeignKey(UserProfile,on_delete=models.CASCADE)    
    products = models.ManyToManyField(Product, related_name='orders')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=250)
    date_ordered = models.DateTimeField(auto_now_add=False)
    waiting_time = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.date_ordered and not self.waiting_time:
            self.waiting_time = self.date_ordered + timedelta(minutes=30)
        super(Order, self).save(*args, **kwargs)

    def __str__(self):
        return f'Order {self.id} by {self.user.user.username}'

class PaymentMode(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name