from django.contrib import admin

from spray.membership.models import MembershipEvent, Promocode

admin.site.register(MembershipEvent)
admin.site.register(Promocode)
