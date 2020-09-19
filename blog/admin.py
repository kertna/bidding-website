from django.contrib import admin
from . models import Profile,Post,Bid,Order

# Register your models here.
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Bid)
admin.site.register(Order)