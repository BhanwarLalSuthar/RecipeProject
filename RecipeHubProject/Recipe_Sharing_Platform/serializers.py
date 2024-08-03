from .models import Recipe, Review,UserProfile,Order,Product, Article, Collection, PaymentMode
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","email","password"]
        extra_kwargs = {'password':{'write_only': True}}
        
    def create(self,validated_data):
            instance = self.Meta.model(**validated_data)
            password = validated_data.pop('password',None)
            if password is not None:
                instance.set_password(password)
                instance.save()
                return instance
        
class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    
    class Meta:
        model = UserProfile
        fields = ['user', 'user_type', 'profile_pic', 'bio', 'join_date']
        
# class RegisterSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)
#     class Meta:
#         model = User
#         fields = ['id','username','password', 'email']
        
#     def create(self, validated_data):
#         user = User.objects.create(  # create a user object onky iwth username
#             username = validated_data['username']
#             # password = validated_data['password']
#         )
#         # user object has inbuikt fn called as set_password
#         user.set_password(validated_data['password']) # hashing the password
#         user.save()
#         return user
        
class RecipeSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'ingredients', 'instructions', 'views',
                  'prep_time', 'cook_time', 'servings', 'category',
                  'cuisine', 'image', 'author', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'user', 'recipe', 'rating', 'comment', 'date']
        
class CollectionSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    recipes = RecipeSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'user', 'name', 'description', 'recipes']
        
class ArticleSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'date_published', 'image']
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'image', 'stock']
        
class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ['id', 'name', 'description']

class OrderSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    products = ProductSerializer(many=True, read_only=True)
    payment_mode = PaymentModeSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'products', 'total_price', 'status', 'date_ordered', 'waiting_time', 'payment_mode']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product_data in products_data:
            order.products.add(product_data)
        return order