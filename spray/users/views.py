from drf_social_oauth2.views import ConvertTokenView

from spray.users.models import UserType


class SocialTokenView(ConvertTokenView):
    def post(self, request, *args, **kwargs):
        user_type = request.data['user_type']
        if UserType.objects.first():
            UserType.objects.update(type=user_type)
        else:
            UserType.objects.create(type=user_type)
        return super(SocialTokenView, self).post(request, *args, **kwargs)
