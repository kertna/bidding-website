"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from blog import views as blog_views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('register/',blog_views.register,name='blog-register'),
    path('login/',auth_views.LoginView.as_view(template_name='blog/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='blog/logout.html'),name='logout'),
    path('profile/',blog_views.profile,name='profile'),
    path('sell/',blog_views.get_name,name='sell'),
    path('<int:auction_id>/bid/', blog_views.bid, name='bid'),
    path('myitems/',blog_views.getmyitems,name='myitems'),
    path('mybids/',blog_views.my_bids,name='my_bids'),
    path('mywishlist/',blog_views.my_wishlist,name='my_wishlist'),
    path('auctions/',blog_views.auctions,name='all-auctions'),
    path('upcomingauctions/',blog_views.upauctions,name='upcoming-auctions'),
    path('shop/',blog_views.shop,name='shop'),
    path('pricerange1/',blog_views.pricerange1,name='pricerange1'),
    path('pricerange2/',blog_views.pricerange2,name='pricerange2'),
    path('pricerange3/',blog_views.pricerange3,name='pricerange3'),
    path('pricerange4/',blog_views.pricerange4,name='pricerange4'),
    path('pricerange5/',blog_views.pricerange5,name='pricerange5'),
    path('pricerange6/',blog_views.pricerange6,name='pricerange6'),
    path('pricerange7/',blog_views.pricerange7,name='pricerange7'),
    path('pricerange8/',blog_views.pricerange8,name='pricerange8'),
    path('pricerange9/',blog_views.pricerange9,name='pricerange9'),
    path('shop/item/<int:pid>', blog_views.shop_item, name='shop-item'),
    path('add_to_wishlist/<int:pid>', blog_views.add_to_wishlist, name='add-to-wishlist'),
    path('delete_from_wishlist/<int:pid>', blog_views.delete_from_wishlist, name='delete-from-wishlist'),
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='blog/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='blog/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='blog/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='blog/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    path('', include('blog.urls')),


]

if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)