from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from app.views import *

urlpatterns = [
    path('', main, name='main'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('profile/', profile_view, name='profile'),
    path('logout/', logout_view, name='logout'),
    path('create-content/', create_content_view, name='create_content'),
    path('content/delete/<int:content_id>/', delete_content, name='delete_content'),
    path('content/update/<int:content_id>/', update_content, name='update_content'),
    path('search/', search_results, name='search_results'),
    path('profile/<str:username>/', profile_view, name='profile_view'),
    path('explore/', explore_view, name='explore'),
    path('subscribe/<int:account_id>/', subscribe_view, name='subscribe_view'),
    path('unsubscribe/<int:author_id>/', unsubscribe_view, name='unsubscribe_view'),
    path('account_list/<str:username>/<str:type>/', account_list, name='account_list'),
    path('content/<int:content_id>/', content_detail, name='content_detail'),
    path('like_list/<int:content_id>/', like_list, name='like_list'),
    path('content/<int:content_id>/add_comment/', add_comment, name='add_comment'),
    path('like_content/<int:content_id>/', like_content, name='like_content'),
    path('notifications/', notifications, name='notifications'),
    path('chats/', ChatListView.as_view(), name='chat_list'),
    path('chats/<int:pk>/', ChatDetailView.as_view(), name='chat_detail'),
    path('chats/<int:chat_id>/send_message/', send_message, name='send_message'),
    path('create_chat/<str:username>/', create_chat, name='create_chat'),
    path('profile_edit/', profile_edit, name='profile_edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
