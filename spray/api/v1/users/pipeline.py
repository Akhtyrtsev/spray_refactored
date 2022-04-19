from social_core.backends.google import GoogleOAuth2
from social_core.backends.facebook import FacebookOAuth2

from spray.users.models import UserType

USER_FIELDS = ['username', 'email']


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


def create_user(strategy, details, backend, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = {name: kwargs.get(name, details.get(name))
              for name in backend.setting('USER_FIELDS', USER_FIELDS)}
    fields['user_type'] = int(UserType.objects.first())
    if not fields:
        return
    return {
        'is_new': True,
        'user': strategy.create_user(**fields)
    }
