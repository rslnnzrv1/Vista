from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=100, blank=True)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='avatars/', default='/avatars/default.jpg', blank=True, null=True)
    bio = models.TextField(null=True, blank=True)
    email = models.EmailField(unique=True)
    is_staff = models.BooleanField(default=False)
    content = models.ForeignKey('Content', on_delete=models.CASCADE, related_name='user_content', null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username


class Content(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='contents')
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='content_files/', null=True, blank=True)

    def get_file_extension(self):
        if self.file:
            file_extension = self.file.name.split('.')[-1]
            return file_extension
        return None

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.content.title}'


class Like(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.ForeignKey(Content, on_delete=models.CASCADE, related_name='likes')

    def __str__(self):
        return f'Like by {self.user.username} on {self.content.title}'


class Subscription(models.Model):
    subscriber = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscriptions')
    account = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='subscribers')
    start_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.subscriber} - {self.account}'


class Notification(models.Model):
    recipient = models.ForeignKey(CustomUser, related_name='notifications', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.message


class Chat(models.Model):
    participants = models.ManyToManyField(CustomUser, related_name='chats')

    def __str__(self):
        return f'{self.participants}'


class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(CustomUser, related_name='sent_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
