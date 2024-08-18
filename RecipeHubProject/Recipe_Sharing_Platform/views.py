from django.shortcuts import render, redirect
import jwt,datetime,django_filters
from django.utils import timezone
from django.views import View


from django.contrib.auth import logout as auth_logout

from django.contrib.auth.models import User 
from django.contrib.auth import authenticate,login,logout

from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse, JsonResponse

from . permissions import *
from .models import UserProfile,Recipe,Review,Collection,Article,Order,Product ,PaymentMode
from .serializers import *
# Create your views here.
class HomeView(View):
    def get(self, request):
        return render(request, 'home.html')
    
class RegisterView(APIView):
    def post(self,request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = UserProfile(user=user,user_type = request.data.get('user_type'))
            profile.save()
            return Response({'detail':'SignUp Succesfull'},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class LogoutView(APIView):
    def post(self, request):
        auth_logout(request)
        response = JsonResponse({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        response.delete_cookie('jwt')
        return response
    
class LoginView(APIView):
    def post(self,request):
        username = request.data.get('username')
        password = request.data.get('password')
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response({"error": "Username does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Incorrect password"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)
        response = Response()
        response.data = {
            'refreshToken' : str(refresh),
            'accessToken' : str(refresh.access_token),
            'detail':'Login Successfull'
        }
        response.status = status.HTTP_200_OK
        response.set_cookie('access',str(refresh.access_token))
        response.set_cookie('refresh',str(refresh))
        return response
    
class PasswordResetRequestView(APIView):
    def post(self, request):
        
        email=request.data['email']
        user = User.objects.get(email=email)
        print(user)
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'message': 'User not registered, please sign up'}, status=status.HTTP_404_NOT_FOUND)
        
        
        refresh = RefreshToken.for_user(user)
        token = str(refresh.access_token)
        current_site = get_current_site(request)
        mail_subject = 'Reset Password'
        email_form = settings.EMAIL_HOST_USER
        message = render_to_string('password_reset_email.html',{
            'user': user,
            'domain': current_site,
            'token': token
        })
        
        send_mail(mail_subject,message, email_form,[email])
        return HttpResponse('Email Sent Successfully')
    
class PasswordResetConfirmView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        print(token)
        if not token:
            return Response({'message': 'Invalid token, Please use Reset Password Again'})
        
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        
        return render(request, 'password_reset_form.html', {'token': token})
    
    def post(self, request):
        password = request.data['password']
        confirm_password = request.data['confirm_password']
        token = request.data['token']
        if not token:
            return Response({'message': "Invalid token, Please use Reset Password again"})
        
        access_token = AccessToken(token)
        user_id = access_token['user_id']
        user = User.objects.get(id=user_id)
        if password == confirm_password:
            user.set_password(password)
            user.save()
            return Response({'message': 'Password Reset Successfully'})
        return Response({'message': 'Something went wrong'})



    
class UserProfileList(generics.ListCreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['user_type']
    search_fields = ['user__username','bio']
    
class UserProfileDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
class RecipeList(generics.ListCreateAPIView):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['category','cuisine', 'author__user__username' ]
    search_fields = ['title', 'ingredients', 'instructions', 'author__user__username']
    ordering_fields = ['title', 'created_at']
    
class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Recipe.objects.all()
    serializer_class= RecipeSerializer
    def get_object(self):
        pk = self.kwargs.get('pk')
        token = self.request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'bhawar', algorithms=['HS256'])
        profile = UserProfile.objects.filter(user_id = payload['id']).first()
        recipe = Recipe.objects.get(id=pk)
        if profile.id != recipe.author.user:
            raise PermissionDenied(detail='You Do Not have Permission to Update This recipe')
        return recipe
        
class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['recipe__title', 'user__user__username']
    search_fields = ['recipe__title', 'user__user__username', 'comment']
    ordering_fields = ['rating', 'date']

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    def get_object(self):
        pk = self.kwargs.get('pk')
        token = self.request.COOKIES.get('jwt')
        payload = jwt.decode(token, 'bhawar', algorithms=['HS256'])
        profile = UserProfile.objects.filter(user_id=payload['id']).first()
        print(self.request.author)
        # user_d = self.request.author
        # print(user_d)
        review = Review.objects.get(id=pk)
        if profile.id != review.user:
            raise  PermissionDenied(detail='you do not have permission to update this review' )
        return review
    
class CollectionList(generics.ListCreateAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['user__user__username']
    search_fields = ['name', 'user__user__username', 'description']
    ordering_fields = ['name', 'user__user__username']

class CollectionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    
class ArticleList(generics.ListCreateAPIView):
    # permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    queryset = Article.objects.all()
    # def post(self, request):
    #     pk = self.kwargs.get('pk')
    #     token = self.request.COOKIES.get('jwt')
    #     payload = jwt.decode(token, 'bhawar', algorithms=['HS256'])
    #     profile = UserProfile.objects.filter(user_id=payload['id']).first()
    #     article = Article.objects.all()
    #     if profile.user_type != "author":
    #         raise PermissionDenied(detail= "Customer do not have permission to create article")
    #     return article
            
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['author__user__username']
    search_fields = ['title', 'content', 'author__user__username']
    ordering_fields = ['title', 'date_published']

    
class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    
    
    
class ProductList(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['category']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']

class ProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    
    
class OrderList(generics.ListCreateAPIView):
    queryset= Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['user__user__username', 'status']
    search_fields = ['user__user__username', 'status']
    ordering_fields = ['date_ordered', 'total_price']
    
class OrderDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_object(self):
        order = super().get_object()
        date_now = timezone.now()  # Use timezone-aware datetime
        if order.waiting_time and date_now > order.waiting_time:
            order.status = 'Expired'
            order.save(update_fields=['status'])
        return order

    
    
class PaymentModeList(generics.ListCreateAPIView):
    queryset = PaymentMode.objects.all()
    serializer_class = PaymentModeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['name', 'description']
    ordering_fields = ['name']

class PaymentModeDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PaymentMode.objects.all()
    serializer_class = PaymentModeSerializer
    
