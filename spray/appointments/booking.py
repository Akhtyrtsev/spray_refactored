from spray.users.models import Valet


def get_valet():
    valet = Valet.objects.get(email='valet@gmail.com')
    return valet


def is_free(valet, date, duration):
    pass
