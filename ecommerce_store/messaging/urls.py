from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('start/<int:vendor_id>/', views.start_conversation, name='start_conversation'),
    path('start/<int:vendor_id>/<int:product_id>/', views.start_conversation, name='start_conversation_product'),
    path('<int:pk>/', views.conversation_detail, name='conversation_detail'),
    path('<int:pk>/poll', views.poll_messages, name='poll_messages'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('message/<int:pk>/edit/', views.edit_message, name='edit_message'),
    path('message/<int:pk>/delete/', views.delete_message, name='delete_message'),
]