from django.contrib import admin

from spray.subscriptions.models import Subscription, ClientSubscription

admin.site.register(Subscription)
admin.site.register(ClientSubscription)
