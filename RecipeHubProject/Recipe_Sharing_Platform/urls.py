from django.contrib import admin
from django.urls import path
from .views import *
from rest_framework.permissions import AllowAny
from drf_yasg.views import get_schema_view as get_swagger_view
from drf_yasg import openapi
from drf_yasg.views import get_schema_view as get_redoc_view

schema_view = get_swagger_view(
    openapi.Info(
        title="AllRecipe API",
        default_version='v1',
        description="API documentation for AllRecipes",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

redoc_view = get_redoc_view(
    openapi.Info(
        title="AllRecipe API",
        default_version='v1',
        description="API documentation for AllRecipe",
    ),
    public=True,
    permission_classes=(AllowAny,),
)

urlpatterns = [
    # URL pattern for user registration
    path('register/', RegisterView.as_view(), name='register'),
    # URL pattern for user login
    path('login/', LoginView.as_view(), name='login'),
    # URL pattern for password reset request
    path('resetpassword/', PasswordResetRequestView.as_view(), name='resetpassword'),
    # URL pattern for password reset confirmation
    path('password_reset_confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # URL pattern for listing and creating recipes
    path('recipelist/', RecipeList.as_view(), name='recipe_list'),
    # URL pattern for retrieving, updating, and deleting a specific recipe
    path('recipelist/<int:pk>/', RecipeDetail.as_view(), name='recipe_detail'),
    
    # URL pattern for listing and creating reviews
    path('reviewlist/', ReviewList.as_view(), name='review_list'),
    # URL pattern for retrieving, updating, and deleting a specific review
    path('reviewlist/<int:pk>/', ReviewDetail.as_view(), name='review_detail'),
    
    # URL pattern for listing and creating articles
    path('articlelist/', ArticleList.as_view(), name='article_list'),
    # URL pattern for retrieving, updating, and deleting a specific article
    path('articlelist/<int:pk>/', ArticleDetail.as_view(), name='article_detail'),
    
    # URL pattern for listing and creating collections
    path('collectionlist/', CollectionList.as_view(), name='collection_list'),
    # URL pattern for retrieving, updating, and deleting a specific collection
    path('collectionlist/<int:pk>/', CollectionDetail.as_view(), name='collection_detail'),
    
    # URL pattern for listing and creating products
    path('productlist/', ProductList.as_view(), name='product_list'),
    # URL pattern for retrieving, updating, and deleting a specific product
    path('productlist/<int:pk>/', ProductDetail.as_view(), name='product_detail'),
    
    # URL pattern for listing and creating orders
    path('orderlist/', OrderList.as_view(), name='order_list'),
    # URL pattern for retrieving, updating, and deleting a specific order
    path('orderlist/<int:pk>/', OrderDetail.as_view(), name='order_detail'),
    
    # URL pattern for listing and creating payment modes
    path('paymentmodelist/', PaymentModeList.as_view(), name='paymentmode_list'),
    # URL pattern for retrieving, updating, and deleting a specific payment mode
    path('paymentmodedetail/<int:pk>/', PaymentModeDetail.as_view(), name='paymentmode_detail'),

    # URL pattern for Swagger UI documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger'),
    # URL pattern for ReDoc documentation
    path('redoc/', redoc_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]
