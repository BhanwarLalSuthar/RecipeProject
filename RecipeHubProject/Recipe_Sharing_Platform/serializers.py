import re
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
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','password']
        extra_kwargs = {'password':{'write_only':True}}
    def create(self,validated_data):
        instance = self.Meta.model(**validated_data)
        password = validated_data.pop('password',None)
        if password is not None:
            instance.set_password(password)
            instance.save()
            return instance
        return {'detail':'Password field cannot be empty'}
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        return value
    def validate_password(self,value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        
        return value
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
    # author = UserProfileSerializer()

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'ingredients', 'instructions', 'views',
                  'prep_time', 'cook_time', 'servings', 'category',
                  'cuisine', 'image', 'author', 'created_at']

class ReviewSerializer(serializers.ModelSerializer):
    # user = UserProfileSerializer(read_only=True)
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = Review
        fields = ['id', 'user', 'recipe', 'rating', 'comment', 'date']
        
class CollectionSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset = UserProfile.objects.all())
    recipes = serializers.PrimaryKeyRelatedField(queryset = Recipe.objects.all(),many=True)
    

    class Meta:
        model = Collection
        fields = ['id', 'user', 'name', 'description', 'recipes']
    def create(self, validated_data):
        user = validated_data.pop('user')
        recipes = validated_data.pop('recipes')
        collection,_ = Collection.objects.get_or_create(user= user,**validated_data)
        # print(collection)
        collection.recipes.set(recipes)
        print(collection)
        return collection
        
class ArticleSerializer(serializers.ModelSerializer):
    # author = UserProfileSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'date_published', 'image']
        
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'image', 'stock']
        

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset = UserProfile.objects.all())
    products = serializers.PrimaryKeyRelatedField(queryset = Product.objects.all(),many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'products', 'total_price', 'status', 'date_ordered', 'waiting_time']

    def create(self, validated_data):
        products_data = validated_data.pop('products')
        order = Order.objects.create(**validated_data)
        for product_data in products_data:
            order.products.add(product_data)
        return order
    
class PaymentModeSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    class Meta:
        model = PaymentMode
        fields = '__all__'
    def create(self, validated_data):
        order_data = validated_data.pop('order')
        order_serializer = OrderSerializer(data=order_data)
        if order_serializer.is_valid():
            order = order_serializer.save()
            validated_data['order'] = order
        payment_mode = PaymentMode.objects.create(**validated_data)
        return payment_mode

    def update(self, instance, validated_data):
        instance.payment_type = validated_data.get('payment_type', instance.payment_type)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.save()  # This will trigger the save method in PaymentMode and update the order status
        return instance
# class CollectionSerializer(serializers.ModelSerializer):
#     user = UserProfileSerializer()
#     recipe = RecipeSerializer()
#     class Meta:
#         model = Collection
#         fields = '__all__'
        