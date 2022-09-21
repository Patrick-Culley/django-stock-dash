from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('stock/', views.stock, name='stock'),
    path('search/', views.search, name='search'),
    path('search/results/', views.addstock, name="addstock"),
    path('delete/', views.delete, name='delete'),
    path('watchlist/', views.watchlist, name='watchlist')
]   