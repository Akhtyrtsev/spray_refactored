from django.urls import include, path
from spray.api.v1.appointments.client import urls as client_urls
from spray.api.v1.appointments.valet import urls as valet_urls
from spray.api.v1.appointments.booking import urls as booking_urls

urlpatterns = [
    path('client/', include(client_urls)),
    path('valet/', include(valet_urls)),
    path('booking/', include(booking_urls)),

]