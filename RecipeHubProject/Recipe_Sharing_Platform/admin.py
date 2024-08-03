from django.contrib import admin
from .models import UserProfile,Recipe,Review,Collection,Article,Order,Product,PaymentMode

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Recipe)
admin.site.register(Review)
admin.site.register(Collection)
admin.site.register(Article)
admin.site.register(Order)
admin.site.register(Product)
admin.site.register(PaymentMode)
