from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny
from spray.api.v1.users.serializers import UserTokenSerializer


class HelloView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)


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
