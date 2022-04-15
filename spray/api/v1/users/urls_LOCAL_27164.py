from django.urls import path
from spray.api.v1.users import views
from .views import UserGetTokenView

urlpatterns = [
    path('hello/', views.HelloView.as_view(), name='hello'),
    path('get-token/', UserGetTokenView.as_view(), name='get_token'),

]