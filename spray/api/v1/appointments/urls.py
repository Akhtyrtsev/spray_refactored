from django.urls import include, path
from spray.api.v1.appointments.cancel.client import urls as client_cancel_urls
from spray.api.v1.appointments.cancel.valet import urls as valet_cancel_urls

urlpatterns = [
    path('', include(client_cancel_urls)),
    path('', include(valet_cancel_urls))

]
