from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_social_oauth2.views import ConvertTokenView
from rest_framework.views import APIView

from spray.users.models import UserType
from spray.api.v1.users.serializers import UserTokenSerializer, RegistrationSerializer


class UserGetTokenView(RetrieveAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            'success': 'True',
            'status code': status.HTTP_200_OK,
            'email': serializer.data['email'],
            'token': serializer.data['token'],
            'token_type': 'Bearer'
        }
        status_code = status.HTTP_200_OK
        return Response(response, status=status_code)


class SocialTokenView(ConvertTokenView):
    def post(self, request, *args, **kwargs):
        user_type = int(request.data['user_type'])
        if UserType.objects.first():
            UserType.objects.filter(pk=1).update(type=user_type)
        else:
            UserType.objects.create(pk=1, type=user_type)
        return super(SocialTokenView, self).post(request, *args, **kwargs)


class UserRegistrationView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        user_data = serializer.data

        return Response(user_data, status=status.HTTP_201_CREATED)

