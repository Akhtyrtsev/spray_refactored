from django.urls import include, path
from spray.api.v1.reschedule.reschedule_client import urls as reschedule_client_urls
from spray.api.v1.reschedule.reschedule_valet import urls as reschedule_valet_urls

urlpatterns = [
    path('', include(reschedule_client_urls)),
    path('', include(reschedule_valet_urls))

]
