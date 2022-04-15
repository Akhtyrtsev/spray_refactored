from social_core.backends.google import GoogleOAuth2
from social_core.backends.facebook import FacebookOAuth2



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
