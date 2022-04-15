from django.urls import path
from spray.api.v1.users import views

urlpatterns = [
    path('hello/', views.HelloView.as_view(), name='hello'),
]