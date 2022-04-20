from social_core.backends.google import GoogleOAuth2
from social_core.backends.facebook import FacebookOAuth2

from spray.users.models import UserType, Client, Valet, User


def update_user_social_data(strategy, response, *args, **kwargs):
    """Set avatar for a user only if is new.
    """
    if not kwargs['is_new']:
        return

    backend = kwargs['backend']
    user = kwargs['user']

    if isinstance(backend, GoogleOAuth2):
        if response['picture']:
            avatar_url = response['picture']
            user.avatar_url = avatar_url


    elif isinstance(backend, FacebookOAuth2):
        fbuid = kwargs['response']['id']
        avatar_url = 'http://graph.facebook.com/%s/picture?type=large' % fbuid
        user.avatar_url = avatar_url

    user.save()


def create_user(user=None, *args, **kwargs):
    if user:
        return {'is_new': False}
    user_data = kwargs['response']
    user_type = int(UserType.objects.first())
    fields = {
        'first_name': user_data.get('given_name'),
        'last_name': user_data.get('family_name'),
        'avatar_url': user_data.get('picture'),
        'email': user_data.get('email'),
        'is_new': True,
        'user_type': int(UserType.objects.first())
    }
    # -----------------------------------------------------------------------------------------------
    # user_type
    # (1, 'superuser'),
    # (2, 'staff'),
    # (3, 'client'),
    # (4, 'valet'),
    # -----------------------------------------------------------------------------------------------
    if user_type == 3:
        user = Client(**fields)
    elif user_type == 4:
        user = Valet(**fields)
    else:
        user = User(**fields)
    user.save()
    return user
