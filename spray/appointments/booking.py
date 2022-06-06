from spray.users import models as users_models


def get_valet():
    valet = users_models.Valet.objects.get(email='payout-valet@gmail.com')
    return valet


def is_free(valet, date, duration):
    pass
