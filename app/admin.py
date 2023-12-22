from django.contrib import admin

from app.models import *

admin.site.register(CustomUser)
admin.site.register(Content)
admin.site.register(Subscription)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Notification)
admin.site.register(Chat)
admin.site.register(Message)
