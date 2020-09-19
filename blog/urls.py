from django.conf.urls import url
from django.urls import path
from . import views
urlpatterns = [
    path('', views.home,name='blog-home'),
	url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',views.activate, name='activate'),
    path('contact', views.contact,name='contact'),
    path('about',views.about,name='about'),
    path('stripecheck/<int:pk>/',views.stripecheck,name='stripecheck'),
    url(r'^results-auctions/$',views.search_auctions,name='search_auctions'),
    url(r'^results-shop/$',views.search_shop,name='search_shop'),
    url(r'^results-upcoming/$',views.search_upcoming,name='search_upcoming'),
    path('charge/<int:pk>/', views.charge, name="charge"),
    path('success', views.successMsg, name="success"),
    path('address/<int:pk>/', views.address, name="address"),
    path('myorders',views.getmyorders,name="myorders"),
]
