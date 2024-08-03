from django.shortcuts import render
import jwt,datetime,django_filters

from django.contrib.auth.models import User 
from django.contrib.auth import authenticate,login,logout

from rest_framework.exceptions import AuthenticationFailed

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, filters
from django_filters.rest_framework import DjangoFilterBackend



from rest_framework_simplejwt.tokens import RefreshToken,AccessToken
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

from .models import UserProfile,Recipe,Review,Collection,Article,Order,Product ,PaymentMode
from .serializers import RecipeSerializer, ReviewSerializer,OrderSerializer,ArticleSerializer,ProductSerializer,UserProfileSerializer,UserSerializer,CollectionSerializer ,PaymentModeSerializer
# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = UserProfile(user=user,user_type = request.data['user_type'])
            profile.save()
            return Response({'message':'User register successfully', 'user_details':serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response({'message':'User not Regitsered, Please Signup'}, status=status.HTTP_404_NOT_FOUND)
        if not user.check_password(password):
            return Response({'message':'wrong password, Please try again'}, status=status.HTTP_400_BAD_REQUEST)
        
        login(request, user)
        payload = {
            'id':user.id,
            'exp': datetime.datetime.now(datetime.UTC)+datetime.timedelta(minutes=60),
            'iat':datetime.datetime.now(datetime.UTC)
        }
        token = jwt.encode(payload, 'bhawar', algorithm='HS256')
        response = Response()
        response.data = {'message':'login successfull','token': token}
        response.status = status.HTTP_200_OK
        response.set_cookie(
            key='jwt',
            value=token,
            httponly=False,
            samesite=None,
            secure=None
        )
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
    queryset = Recipe.objects.all()
    serializer_class= RecipeSerializer
    
class ReviewList(generics.ListCreateAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['recipe__title', 'user__user__username']
    search_fields = ['recipe__title', 'user__user__username', 'comment']
    ordering_fields = ['rating', 'date']

class ReviewDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
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
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['author__user__username']
    search_fields = ['title', 'content', 'author__user__username']
    ordering_fields = ['title', 'date_published']
    
class ArticleDetail(generics.RetrieveUpdateDestroyAPIView):
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
    
