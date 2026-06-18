from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about_us, name='aboutus'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('registervendor/', views.register_as_vendor, name='registervendor'),
    path('update_user/', views.update_user, name='update_user'),
    path('update_info/', views.update_info, name='update_info'),
    path('update_password/', views.update_password, name='update_password'),
    path('vendor/', views.vendor_dashboard, name='vendor'),
    path('productdetail/<int:pk>', views.product_detail, name='productdetail'),
    path('store_detail/<int:pk>', views.store_detail, name='store_detail'),
    path('category/<str:slug>', views.category, name='category'),
    path('genre_summary/', views.genre_summary, name='genre_summary'),
    path('record_collection_summary/', views.record_collection_summary, name='record_collection_summary'),
    path('record_store_summary/', views.record_store_summary, name='record_store_summary'),
    path('search/', views.search, name='search'),
    #path('stores/', views.home, name='stores'),
    #path('stores_add/', views.home, name='stores'),
    #path('prodcut/', views.home, name='product'),
    #path('prodcut_add/', views.home, name='product_add'),
    #path('prodcut_deatil/', views.home, name='product_deatil'),
    #path('', views.home, name='home'),
]   # forgot password
