from spray.appointments.managers import NoValetAppointmentsManager
from spray.appointments.models import Appointment


class NoValetAppointments(Appointment):
    objects = NoValetAppointmentsManager()

    class Meta:
        proxy = True
        verbose_name = 'Appointment without valet'
        verbose_name_plural = 'Appointment without valets'