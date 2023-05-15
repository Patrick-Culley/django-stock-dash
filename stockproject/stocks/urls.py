from django.urls import path
from .views import register
from .import views

urlpatterns = [
    path('', views.siteentry, name='siteentry'),
    path('home', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('register/login/', views.login, name='login'),
    path('stock/', views.stock, name='stock'),
    path('search/', views.search, name='search'),
    path('search/results/', views.addstock, name="addstock"),
    path('delete/', views.delete, name='delete'),
    path('watchlist/', views.watchlist, name='watchlist')
]   