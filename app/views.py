from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView, FormView

from .forms import CustomUserCreationForm, LoginForm, ContentForm, ProfileEditForm
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .forms import CommentForm
from .models import *

from django.contrib.auth.hashers import make_password
from django.core.files import File
from faker import Faker
from django.db.models.signals import post_save
from django.dispatch import receiver


def create_users_with_content(num_users, num_content_per_user):
    fake = Faker()
    for _ in range(num_users):
        username = fake.user_name()
        email = fake.email()
        password = make_password('zxc')
        user = CustomUser.objects.create_user(username=username, email=email, password=password)
        file_path = ['media/oslRgpWEAnDePQ1K4xZBb8qDFDPfNRMuRnGmiA_online_video_cutter_com.mp4', 'media/DZ_02_1.png']
        for i in range(num_content_per_user):
            title = fake.sentence()
            description = fake.paragraph()
            with open(file_path[i], 'rb') as f:
                content_file = File(f)
                content = Content.objects.create(author=user, title=title, description=description, file=content_file)


def main(request):
    # create_users_with_content(20, 2)
    user = request.user
    if str(user) == 'AnonymousUser':
        return redirect('register')
    subscriptions = user.subscriptions.all()
    content = Content.objects.filter(author__in=subscriptions.values_list('account')).order_by('-created_at')
    return render(request, 'app/main.html', {'content': content})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, 'app/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('profile')
            else:
                form.add_error(None, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()
    return render(request, 'app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('register')


def create_content_view(request):
    if request.method == 'POST':
        form = ContentForm(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.author = request.user
            content.save()
            return redirect('profile')
    else:
        form = ContentForm()
    return render(request, 'app/create_content.html', {'form': form})


def delete_content(request, content_id):
    content = Content.objects.get(id=content_id)
    if content.author == request.user:
        content.delete()
    return redirect('profile')


def update_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    if request.method == 'POST':
        form = ContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ContentForm(instance=content)

    return render(request, 'app/update_content.html', {'form': form})


def search_results(request):
    query = request.GET.get('query')
    results = CustomUser.objects.filter(username__icontains=query)
    return render(request, 'app/search_results.html', {'results': results})


@login_required
def profile_view(request, username=None):
    if username:
        author = get_object_or_404(CustomUser, username=username)
        user_content = Content.objects.filter(author=author)
        is_owner = author == request.user
        is_subscribed = Subscription.objects.filter(subscriber=request.user, account=author).exists()
        subscribers_count = Subscription.objects.filter(account=author).count()
        subscriptions_count = Subscription.objects.filter(subscriber=author).count()
        context = {
            'author': author,
            'user_content': user_content,
            'is_owner': is_owner,
            'is_subscribed': is_subscribed,
            'subscribers_count': subscribers_count,
            'subscriptions_count': subscriptions_count
        }
    else:
        user = request.user
        author = get_object_or_404(CustomUser, username=user)
        user_content = Content.objects.filter(author=user)
        is_owner = author == request.user
        is_subscribed = Subscription.objects.filter(subscriber=request.user, account=author).exists()
        subscribers_count = Subscription.objects.filter(account=author).count()
        subscriptions_count = Subscription.objects.filter(subscriber=author).count()
        context = {
            'user': user,
            'author': author,
            'user_content': user_content,
            'is_owner': is_owner,
            'is_subscribed': is_subscribed,
            'subscribers_count': subscribers_count,
            'subscriptions_count': subscriptions_count
        }

    return render(request, 'app/profile.html', context)


def explore_view(request):
    posts = Content.objects.all().order_by('-created_at')
    return render(request, 'app/explore.html', {'posts': posts})


@login_required
def subscribe_view(request, account_id):
    account = CustomUser.objects.get(id=account_id)
    subscription = Subscription(subscriber=request.user, account=account)
    subscription.save()
    return redirect('profile_view', username=account.username)


@login_required
def unsubscribe_view(request, author_id):
    author = CustomUser.objects.get(id=author_id)
    subscription = Subscription.objects.filter(subscriber=request.user, account=author)
    if subscription is not None:
        subscription.delete()
    return redirect('profile_view', username=author.username)


@login_required
def account_list(request, username, type):
    account = get_object_or_404(CustomUser, username=username)
    if type == 'subscribers':
        accounts = account.subscribers.all()
    elif type == 'subscriptions':
        accounts = account.subscriptions.all()
    else:
        accounts = []
    return render(request, 'app/account_list.html', {'accounts': accounts, 'type': type})


def content_detail(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    comments = content.comments.all()
    likes = content.likes.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.content = content
            comment.save()
            return redirect('content_detail', content_id=content_id)
    else:
        form = CommentForm()

    context = {
        'content': content,
        'comments': comments,
        'likes': likes,
        'form': form
    }

    return render(request, 'app/content_detail.html', context)


def like_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)

    if request.method == 'POST':
        like, created = Like.objects.get_or_create(user=request.user, content=content)
        if not created:
            like.delete()

    return redirect('content_detail', content_id=content_id)


def like_list(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    liked_users = content.likes.all()
    return render(request, 'app/like_list.html', {'liked_users': liked_users})


def add_comment(request, content_id):
    if request.method == 'POST':
        content = Content.objects.get(id=content_id)
        comment_text = request.POST.get('comment')
        Comment.objects.create(content=content, text=comment_text, user=request.user)
        return redirect('content_detail', content_id=content_id)
    else:
        return redirect('content_detail', content_id=content_id)


@login_required
def like_content(request, content_id):
    content = get_object_or_404(Content, id=content_id)
    user = request.user

    if Like.objects.filter(user=user, content=content).exists():
        Like.objects.filter(user=user, content=content).delete()
    else:
        like = Like(user=user, content=content)
        like.save()

    return redirect('content_detail', content_id=content_id)


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created:
        recipient = instance.content.author
        sender = instance.user
        message = f'{sender.username} оставил комментарий к вашему контенту "{instance.content.title}"'

        notification = Notification(recipient=recipient, sender=sender, message=message)
        notification.save()


@receiver(post_save, sender=Subscription)
def create_subscription_notification(sender, instance, created, **kwargs):
    if created:
        recipient = instance.account
        sender = instance.subscriber
        message = f'{sender.username} подписался на вас'

        notification = Notification(recipient=recipient, sender=sender, message=message)
        notification.save()


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    if created:
        recipient = instance.content.author
        sender = instance.user
        message = f'{sender.username} поставил лайк вашему контенту "{instance.content.title}"'

        notification = Notification(recipient=recipient, sender=sender, message=message)
        notification.save()


@login_required
def notifications(request):
    user = request.user
    notifications = user.notifications.all().order_by('-created_at')
    for notification in notifications:
        notification.is_read = True
        notification.save()

    context = {
        'notifications': notifications
    }

    return render(request, 'app/notifications.html', context)


# def chat_list(request):
#     chats = request.user.chats.all()
#     return render(request, 'app/chat_list.html', {'chats': chats})
#
#
# def chat_detail(request, chat_id):
#     chat = get_object_or_404(Chat, pk=chat_id, participants=request.user)
#     messages = chat.messages.order_by('timestamp')
#     return render(request, 'app/chat_detail.html', {'chat': chat, 'messages': messages})
#
#
# def send_message(request, chat_id):
#     chat = get_object_or_404(Chat, pk=chat_id, participants=request.user)
#     if request.method == 'POST':
#         content = request.POST.get('content')
#         if content:
#             Message.objects.create(chat=chat, sender=request.user, content=content)
#     return redirect('app/chat_detail', chat_id=chat_id)
class ChatListView(LoginRequiredMixin, ListView):
    model = Chat
    template_name = 'app/chat_list.html'
    context_object_name = 'chats'
    paginate_by = 10

    def get_queryset(self):
        user_chats = Chat.objects.filter(participants=self.request.user)
        return user_chats

    def post(self, request, *args, **kwargs):
        chat = self.get_object()
        content = request.POST.get('content')

        if content:
            sender = request.user
            message = Message(chat=chat, sender=sender, content=content)
            message.save()

        return redirect('chat', chat_id=chat.pk)


class ChatDetailView(LoginRequiredMixin, DetailView):
    model = Chat
    template_name = 'app/chat_detail.html'
    context_object_name = 'chat'


@login_required
def send_message(request, chat_id):
    chat = get_object_or_404(Chat, pk=chat_id)

    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            sender = request.user
            message = Message(chat=chat, sender=sender, content=content)
            message.save()
            return redirect('chat_detail', pk=chat_id)
    else:
        content = ''

    context = {
        'chat': chat,
        'content': content
    }

    return render(request, 'app/chat_detail.html', context)


def create_chat(request, username):
    participant1 = request.user
    participant2 = get_object_or_404(CustomUser, username=username)
    chat = Chat.objects.filter(participants=participant1).filter(participants=participant2).first()

    if chat is None:
        chat = Chat.objects.create()
        chat.participants.add(participant1, participant2)
        chat.save()

    return redirect('chat_detail', pk=chat.pk)


def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get('password')

            user.set_password(password)
            update_session_auth_hash(request, user)
            user.save()
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'app/profile_edit.html', {'form': form})
